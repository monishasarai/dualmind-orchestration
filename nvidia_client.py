"""
NVIDIA Client Module
Reusable client for NVIDIA Build API (OpenAI-compatible).
Supports mistralai/mistral-nemotron and other NVIDIA-hosted models.
"""

import os
import logging
import time
from typing import Optional, List, Dict, Any, Union, Generator
from functools import wraps
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Default configuration
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_DEFAULT_MODEL = "mistralai/mistral-nemotron"


class NvidiaClient:
    """
    Client for NVIDIA Build API using OpenAI-compatible chat completions.
    Supports streaming, tool/function calling, and retry logic.
    """

    def __init__(self):
        """Initialize NVIDIA client with environment configuration."""
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.base_url = os.getenv("NVIDIA_BASE_URL", NVIDIA_BASE_URL)
        self.model = os.getenv("NVIDIA_MODEL", NVIDIA_DEFAULT_MODEL)
        self._client = None
        self._last_call = 0.0

        if not self.api_key:
            logger.warning("NVIDIA_API_KEY not found. NVIDIA LLM features will be unavailable.")
        else:
            logger.info(f"NVIDIA client initialized: model={self.model}")

    def _get_client(self):
        """Lazy-initialize the OpenAI-compatible client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    base_url=self.base_url,
                    api_key=self.api_key,
                )
                logger.info("NVIDIA OpenAI-compatible client created.")
            except ImportError:
                logger.error("openai package not installed. Run: pip install openai")
                raise
        return self._client

    def _rate_limit(self):
        """Enforce minimum delay between calls."""
        now = time.time()
        elapsed = now - self._last_call
        if elapsed < 0.5:
            time.sleep(0.5 - elapsed)
        self._last_call = time.time()

    def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.6,
        top_p: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ) -> Optional[Union[str, Generator]]:
        """
        Send a chat completion request to NVIDIA API.

        Args:
            prompt: The user message content.
            system_prompt: Optional system message.
            temperature: Sampling temperature.
            top_p: Nucleus sampling parameter.
            max_tokens: Maximum tokens in response.
            stream: If True, return a generator of streamed chunks.
            tools: Optional list of tool/function definitions for function calling.
            max_retries: Number of retries on failure.
            retry_delay: Initial delay between retries (doubles each retry).

        Returns:
            Response string, streaming generator, or None on failure.
        """
        if not self.api_key:
            logger.warning("NVIDIA API key not configured. Skipping call.")
            return None

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        delay = retry_delay

        for attempt in range(1, max_retries + 1):
            try:
                self._rate_limit()
                client = self._get_client()

                kwargs: Dict[str, Any] = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens,
                    "stream": stream,
                }

                if tools:
                    kwargs["tools"] = tools

                logger.debug(
                    f"NVIDIA API call attempt {attempt}/{max_retries}: "
                    f"model={self.model}, tokens={max_tokens}"
                )

                completion = client.chat.completions.create(**kwargs)

                if stream:
                    return self._stream_response(completion)

                # Non-streaming: extract content
                if completion.choices and completion.choices[0].message:
                    content = completion.choices[0].message.content
                    if content:
                        logger.info("NVIDIA API call successful.")
                        return content.strip()

                    # Check for tool calls
                    tool_calls = completion.choices[0].message.tool_calls
                    if tool_calls:
                        logger.info(f"NVIDIA API returned {len(tool_calls)} tool call(s).")
                        return str(tool_calls)

                logger.warning("NVIDIA API returned empty response.")
                return None

            except Exception as e:
                error_msg = str(e)
                logger.error(f"NVIDIA API error (attempt {attempt}/{max_retries}): {error_msg}")

                if "rate" in error_msg.lower() or "429" in error_msg:
                    delay = min(60, delay * 2)
                    logger.warning(f"Rate limited. Waiting {delay:.1f}s...")
                    time.sleep(delay)
                    continue

                if attempt < max_retries:
                    logger.warning(f"Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    delay = min(60, delay * 2)
                else:
                    logger.error(f"NVIDIA API: Max retries exceeded. Last error: {error_msg}")

        return None

    def _stream_response(self, completion) -> Generator:
        """Yield streamed content chunks."""
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def chat_sync(self, prompt: str, **kwargs) -> Optional[str]:
        """Convenience wrapper: always returns full string (no streaming)."""
        kwargs["stream"] = False
        return self.chat(prompt, **kwargs)

    def is_available(self) -> bool:
        """Check if the NVIDIA client is configured and ready."""
        return self.api_key is not None


# Module-level singleton
nvidia_client = NvidiaClient()
