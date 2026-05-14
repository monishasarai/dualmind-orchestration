"""
LLM Integration Module
Provides LLM API integration using multiple providers (NVIDIA, OpenRouter)
for the DualMind system. Provider selection is automatic based on available
API keys, with graceful fallback.
"""

import os
import json
import logging
import time
import re
import requests
from typing import Dict, Any, Optional, List, Union
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime, timedelta


class RateLimiter:
    def __init__(self, calls_per_minute):
        self.calls_per_minute = calls_per_minute
        self.calls = []

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = datetime.now()
            # Remove calls older than 1 minute
            self.calls = [t for t in self.calls if now - t < timedelta(minutes=1)]

            if len(self.calls) >= self.calls_per_minute:
                # Calculate wait time
                oldest_call = self.calls[0]
                wait_time = (oldest_call + timedelta(minutes=1) - now).total_seconds()
                if wait_time > 0:
                    time.sleep(wait_time)

            self.calls.append(datetime.now())
            return func(*args, **kwargs)
        return wrapper


class LLMClient:
    """
    Multi-provider LLM client.

    Provider priority:
        1. NVIDIA Build API (if NVIDIA_API_KEY is set)
        2. OpenRouter (if OPENROUTER_API_KEY is set)

    Both providers expose the same ``call_llm`` interface so downstream
    consumers (planner, verifier) require zero changes.
    """

    def __init__(self):
        """Initialize the LLM client with all available providers."""
        load_dotenv()

        self.logger = logging.getLogger(__name__)
        self.rate_limiter = RateLimiter(calls_per_minute=10)

        # --- Provider: NVIDIA ---
        self.nvidia_api_key = os.getenv("NVIDIA_API_KEY")
        self.nvidia_base_url = os.getenv(
            "NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"
        )
        self.nvidia_model = os.getenv("NVIDIA_MODEL", "mistralai/mistral-nemotron")
        self._nvidia_client = None  # lazy init

        # --- Provider: OpenRouter ---
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        self.openrouter_models = [
            os.getenv("OPENROUTER_MODEL", "microsoft/wizardlm-2-8x22b"),
            "microsoft/wizardlm-2-8x22b",
            "anthropic/claude-3-haiku",
            "openai/gpt-3.5-turbo",
            "meta-llama/llama-3-8b-instruct",
        ]
        self.openrouter_model = self.openrouter_models[0]

        # --- Determine active provider ---
        if self.nvidia_api_key:
            self._active_provider = "nvidia"
            self.logger.info(
                f"Primary LLM provider: NVIDIA ({self.nvidia_model})"
            )
        elif self.openrouter_api_key:
            self._active_provider = "openrouter"
            self.logger.info(
                f"Primary LLM provider: OpenRouter ({self.openrouter_model})"
            )
        else:
            self._active_provider = None
            self.logger.warning(
                "No LLM API key found (NVIDIA_API_KEY / OPENROUTER_API_KEY). "
                "LLM features will use fallback mode."
            )

    # ------------------------------------------------------------------
    # NVIDIA helpers
    # ------------------------------------------------------------------

    def _get_nvidia_client(self):
        """Lazy-initialise the OpenAI-compatible NVIDIA client."""
        if self._nvidia_client is None:
            try:
                from openai import OpenAI

                self._nvidia_client = OpenAI(
                    base_url=self.nvidia_base_url,
                    api_key=self.nvidia_api_key,
                )
            except ImportError:
                self.logger.error(
                    "openai package not installed. Run: pip install openai"
                )
                raise
        return self._nvidia_client

    def _call_nvidia(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float = 0.6,
        top_p: float = 0.7,
    ) -> Optional[str]:
        """Execute a chat completion via NVIDIA Build API."""
        client = self._get_nvidia_client()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        completion = client.chat.completions.create(
            model=self.nvidia_model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stream=False,
        )

        if completion.choices and completion.choices[0].message:
            content = completion.choices[0].message.content
            return content.strip() if content else None
        return None

    # ------------------------------------------------------------------
    # OpenRouter helpers
    # ------------------------------------------------------------------

    def _try_next_openrouter_model(self):
        """Rotate to the next available OpenRouter model."""
        idx = (
            self.openrouter_models.index(self.openrouter_model)
            if self.openrouter_model in self.openrouter_models
            else -1
        )
        self.openrouter_model = self.openrouter_models[
            (idx + 1) % len(self.openrouter_models)
        ]
        self.logger.warning(f"Switching OpenRouter model to: {self.openrouter_model}")

    def _call_openrouter(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
    ) -> Optional[str]:
        """Execute a chat completion via OpenRouter REST API."""
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key.strip()}",
            "X-API-Key": self.openrouter_api_key.strip(),
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/satvik2106/HuggingGpt",
            "X-Title": "DualMind Orchestrator",
            "Accept": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.openrouter_model,
            "messages": messages,
            "max_tokens": max(100, min(max_tokens, 4000)),
            "temperature": 0.3,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1,
        }

        resp = requests.post(
            f"{self.openrouter_base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=60,
        )

        if resp.status_code == 429:
            retry_after = int(resp.headers.get("retry-after", 5))
            self.logger.warning(f"OpenRouter rate-limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
            raise requests.RequestException("Rate limited", response=resp)

        if resp.status_code == 404:
            self._try_next_openrouter_model()
            raise requests.RequestException("Model not found", response=resp)

        resp.raise_for_status()
        result = resp.json()

        if not result.get("choices"):
            raise ValueError("No choices in OpenRouter response")

        content = result["choices"][0]["message"]["content"]
        if not content:
            raise ValueError("Empty content in OpenRouter response")

        return content

    # ------------------------------------------------------------------
    # JSON extraction
    # ------------------------------------------------------------------

    def _extract_json_from_response(self, text: str) -> str:
        """Extract JSON from LLM response, handling all common formats."""
        if not text:
            raise ValueError("Empty response from LLM")

        # Strip leading/trailing whitespace (model often adds a leading space)
        text = text.strip()

        # 1. Try direct parse first (fastest path)
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            pass

        # 2. Strip markdown code fences
        cleaned = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.IGNORECASE)
        cleaned = re.sub(r'\n?```\s*$', '', cleaned).strip()
        try:
            json.loads(cleaned)
            return cleaned
        except json.JSONDecodeError:
            pass

        # 3. Find outermost { ... } using brace counting (most reliable)
        start = text.find('{')
        if start != -1:
            depth = 0
            for i in range(start, len(text)):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        candidate = text[start:i + 1]
                        try:
                            json.loads(candidate)
                            return candidate
                        except json.JSONDecodeError:
                            break

        # 4. Regex fallback
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                json.loads(match.group(0))
                return match.group(0)
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Could not extract valid JSON. Sample: {text[:200]}")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def call_llm(
        self,
        prompt: str,
        system_prompt: str = None,
        max_tokens: int = 1000,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        require_json: bool = False,
    ) -> Optional[Union[str, Dict, List]]:
        """
        Make a call to the LLM API with retry logic and provider fallback.

        The method tries the active provider first.  If it fails after
        exhausting retries it falls back to the other provider (if available).

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (doubles each retry)
            require_json: If True, parse response as JSON and return dict/list

        Returns:
            Response content (str, dict, or list) or None if all fail
        """
        # Build ordered list of providers to try
        providers = []
        if self._active_provider == "nvidia" and self.nvidia_api_key:
            providers.append("nvidia")
        if self.openrouter_api_key:
            providers.append("openrouter")
        if self._active_provider == "nvidia" and "nvidia" not in providers:
            pass  # already tried
        if not providers:
            self.logger.warning("No LLM provider available.")
            return None

        for provider in providers:
            result = self._call_provider(
                provider=provider,
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                max_retries=max_retries,
                retry_delay=retry_delay,
                require_json=require_json,
            )
            if result is not None:
                return result
            self.logger.warning(
                f"Provider '{provider}' failed. Trying next provider..."
            )

        self.logger.error("All LLM providers exhausted.")
        if require_json:
            return {
                "error": "Failed to get valid response from LLM",
                "details": "All providers exhausted",
            }
        return None

    def _call_provider(
        self,
        provider: str,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        max_retries: int,
        retry_delay: float,
        require_json: bool,
    ) -> Optional[Union[str, Dict, List]]:
        """Try a single provider with retries."""
        delay = retry_delay
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                # Rate limit
                current_time = time.time()
                if hasattr(self, '_last_call'):
                    elapsed = current_time - self._last_call
                    if elapsed < 1.0:
                        time.sleep(1.0 - elapsed)
                self._last_call = time.time()

                self.logger.debug(
                    f"[{provider}] attempt {attempt}/{max_retries}, "
                    f"max_tokens={max_tokens}"
                )

                # Dispatch to provider
                if provider == "nvidia":
                    content = self._call_nvidia(prompt, system_prompt, max_tokens)
                elif provider == "openrouter":
                    content = self._call_openrouter(prompt, system_prompt, max_tokens)
                else:
                    self.logger.error(f"Unknown provider: {provider}")
                    return None

                if not content:
                    raise ValueError(f"Empty response from {provider}")

                self.logger.info(f"[{provider}] API call successful.")

                # JSON handling
                if require_json:
                    try:
                        if isinstance(content, str):
                            json_str = self._extract_json_from_response(content)
                            return json.loads(json_str)
                        return content
                    except Exception as e:
                        self.logger.warning(f"JSON parse failed: {e}")
                        if attempt < max_retries:
                            time.sleep(delay)
                            delay *= 2
                            continue
                        raise

                return content

            except Exception as e:
                last_error = e
                error_msg = str(e)
                self.logger.error(f"[{provider}] Error: {error_msg}")

                if "context length" in error_msg.lower():
                    max_tokens = max(500, max_tokens // 2)
                    self.logger.warning(
                        f"Context length exceeded, reducing max_tokens to {max_tokens}"
                    )

                if attempt < max_retries:
                    self.logger.warning(f"Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    delay = min(60, delay * 2)

        self.logger.error(
            f"[{provider}] Max retries exceeded. Last error: {last_error}"
        )
        return None

    def is_available(self) -> bool:
        """Check if any LLM provider is available."""
        return self.nvidia_api_key is not None or self.openrouter_api_key is not None

    def get_active_provider(self) -> Optional[str]:
        """Return the name of the active primary provider."""
        return self._active_provider


# Global LLM client instance
llm_client = LLMClient()

