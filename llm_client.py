"""
LLM Integration Module
Provides LLM API integration using OpenRouter for the DualMind system.
"""

import os
import json
import logging
import time
import re
import requests
from typing import Dict, Any, Optional, List, Union, Tuple
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime, timedelta
import time
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
    LLM client for making API calls to OpenRouter.
    """

    def __init__(self):
        """Initialize the LLM client."""
        load_dotenv()

        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Try multiple models in order of preference
        self.models = [
            os.getenv('OPENROUTER_MODEL', 'microsoft/wizardlm-2-8x22b'),
            'microsoft/wizardlm-2-8x22b',
            'anthropic/claude-3-haiku',
            'openai/gpt-3.5-turbo',
            'meta-llama/llama-3-8b-instruct',
        ]
        self.model = self.models[0]  # Start with preferred model
        
        self.logger = logging.getLogger(__name__)
        self.rate_limiter = RateLimiter(calls_per_minute=5)

        if not self.api_key:
            self.logger.warning("OpenRouter API key not found. LLM features will use fallback mode.")
            self.api_key = None

    def _try_next_model(self):
        """Try the next available model when current one fails."""
        current_index = self.models.index(self.model) if self.model in self.models else -1
        next_index = (current_index + 1) % len(self.models)
        self.model = self.models[next_index]
        self.logger.warning(f"Switching to model: {self.model}")

    def _rate_limit(self):
        """Simple rate limiting to prevent hitting API limits."""
        current_time = time.time()
        if hasattr(self, '_last_call'):
            elapsed = current_time - self._last_call
            if elapsed < 1.0:  # 1 second between calls
                time.sleep(1.0 - elapsed)
        self._last_call = time.time()

    def _extract_json_from_response(self, text: str) -> str:
        """Extract JSON from LLM response, handling various formats."""
        if not text:
            raise ValueError("Empty response from LLM")

        # Try to find JSON object or array
        json_match = re.search(r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}|\[[^\]]*\]', text, re.DOTALL)
        if json_match:
            try:
                # Try to parse the matched JSON
                json.loads(json_match.group(0))
                return json_match.group(0)
            except json.JSONDecodeError:
                pass

        # If no valid JSON found, try to clean and parse the whole text
        try:
            # Remove markdown code blocks if present
            cleaned = re.sub(r'```(?:json)?\s*', '', text, flags=re.IGNORECASE)
            cleaned = re.sub(r'```\s*$', '', cleaned)
            json.loads(cleaned)
            return cleaned
        except json.JSONDecodeError:
            pass

        # If all else fails, try to extract the first valid JSON object
        try:
            # Look for content between curly braces
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return match.group(0)
        except Exception:
            pass

        raise ValueError("Could not extract valid JSON from response")

    def call_llm(
        self, 
        prompt: str, 
        system_prompt: str = None, 
        max_tokens: int = 1000,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        require_json: bool = False
    ) -> Optional[Union[str, Dict, List]]:
        """
        Make a call to the LLM API with retry logic and JSON handling.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds (will be doubled each retry)
            require_json: If True, will attempt to parse response as JSON and return dict/list

        Returns:
            Response content (str, dict, or list) or None if all retries fail
        """
        if not self.api_key:
            self.logger.warning("No API key available for LLM call")
            return None

        retry_count = 0
        last_error = None
        delay = retry_delay

        while retry_count <= max_retries:
            try:
                self._rate_limit()  # Enforce rate limiting
                
                headers = {
                    'Authorization': f'Bearer {self.api_key.strip()}',
                    'X-API-Key': self.api_key.strip(),
                    'Content-Type': 'application/json',
                    'HTTP-Referer': 'https://github.com/Shashank-Reddy-Y/JARVIS-DOMAIN-SPECIFIC-V1',
                    'X-Title': 'DualMind Orchestrator',
                    'Accept': 'application/json'
                }

                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                data = {
                    'model': self.model,
                    'messages': messages,
                    'max_tokens': max(100, min(max_tokens, 4000)),  # Ensure reasonable limits
                    'temperature': 0.3,
                    'top_p': 0.9,
                    'frequency_penalty': 0.1,
                    'presence_penalty': 0.1
                }

                # Add JSON response format if requested and model supports it
                if require_json and 'gpt' in self.model.lower():
                    data['response_format'] = {'type': 'json_object'}

                self.logger.debug(f"Sending request to {self.model} (attempt {retry_count + 1}/{max_retries + 1})")
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,  # Use json parameter to automatically serialize
                    timeout=60  # Increased timeout for complex queries
                )

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('retry-after', 5))
                    self.logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()
                result = response.json()

                if not result.get('choices') or len(result['choices']) == 0:
                    raise ValueError("No choices in API response")

                content = result['choices'][0]['message']['content']
                
                if not content:
                    raise ValueError("Empty content in API response")

                self.logger.info("LLM API call successful")
                
                # If JSON is required, try to parse it
                if require_json:
                    try:
                        if isinstance(content, str):
                            json_str = self._extract_json_from_response(content)
                            return json.loads(json_str)
                        return content  # Already parsed by requests
                    except Exception as e:
                        self.logger.warning(f"Failed to parse JSON response: {e}")
                        if retry_count < max_retries:
                            retry_count += 1
                            time.sleep(delay)
                            delay *= 2  # Exponential backoff
                            continue
                        raise

                return content

            except requests.RequestException as e:
                last_error = e
                status_code = getattr(e.response, 'status_code', None)
                if status_code == 429:  # Rate limited
                    retry_after = int(e.response.headers.get('retry-after', min(30, 5 * (retry_count + 1))))
                    self.logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                elif status_code == 404:  # Model not found, try next model
                    self.logger.warning(f"Model {self.model} not found (404). Trying next model...")
                    self._try_next_model()
                    # Reset retry count for new model
                    retry_count = 0
                    delay = retry_delay
                    continue
                elif status_code and status_code >= 500:
                    self.logger.error(f"Server error ({status_code}): {e}")
                else:
                    self.logger.error(f"Request failed: {e}")

            except (json.JSONDecodeError, ValueError) as e:
                last_error = e
                self.logger.error(f"Failed to parse response: {e}")
                if retry_count < max_retries and 'context length' in str(e).lower():
                    # If context length exceeded, reduce max_tokens and retry
                    max_tokens = max(500, max_tokens // 2)
                    self.logger.warning(f"Context length exceeded, reducing max_tokens to {max_tokens}")
                    retry_count += 1
                    time.sleep(delay)
                    delay *= 2
                    continue

            except Exception as e:
                last_error = e
                self.logger.error(f"Unexpected error: {e}", exc_info=True)

            # If we get here, an error occurred and we should retry if possible
            retry_count += 1
            if retry_count <= max_retries:
                self.logger.warning(f"Retrying in {delay:.1f} seconds... (attempt {retry_count}/{max_retries + 1})")
                time.sleep(delay)
                delay = min(60, delay * 2)  # Exponential backoff with max 60s
            else:
                self.logger.error(f"Max retries exceeded. Last error: {last_error}")
                if require_json:
                    # If we need JSON but failed, return a basic error structure
                    return {
                        "error": "Failed to get valid response from LLM",
                        "details": str(last_error)[:200] if last_error else "Unknown error"
                    }
                return None

        return None

    def is_available(self) -> bool:
        """Check if LLM API is available and configured."""
        return self.api_key is not None

# Global LLM client instance
llm_client = LLMClient()
