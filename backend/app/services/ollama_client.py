"""ForgeTeam AI - Ollama LLM client for local AI inference."""

import json
import logging
import httpx
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for communicating with the local Ollama service."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_tokens: Optional[int] = None,
    ):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout = timeout or settings.ollama_timeout
        self.max_tokens = max_tokens or settings.ollama_max_tokens

    async def check_connection(self) -> bool:
        """Check if Ollama service is reachable."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama connection check failed: {e}")
            return False

    async def check_model_available(self) -> bool:
        """Check if the configured model is available."""
        try:
            models = await self.list_models()
            return any(self.model in m for m in models)
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        """List available models from Ollama."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    return [m.get("name", "") for m in data.get("models", [])]
        except Exception as e:
            logger.warning(f"Failed to list Ollama models: {e}")
        return []

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_retries: int = 2,
    ) -> str:
        """Generate a completion from the local model.

        Args:
            prompt: The user prompt
            system_prompt: System instructions for the model
            temperature: Sampling temperature
            max_retries: Number of retry attempts on failure

        Returns:
            Generated text response

        Raises:
            OllamaError: If generation fails after all retries
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(
                        f"{self.base_url}/api/chat",
                        json={
                            "model": self.model,
                            "messages": messages,
                            "stream": False,
                            "options": {
                                "temperature": temperature,
                                "num_predict": self.max_tokens,
                            },
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data.get("message", {}).get("content", "")
                        if content:
                            return content
                        raise OllamaError("Empty response from model")
                    else:
                        raise OllamaError(
                            f"Ollama returned status {resp.status_code}: {resp.text[:500]}"
                        )
            except httpx.TimeoutException:
                last_error = OllamaError("Request timed out")
                logger.warning(f"Ollama timeout (attempt {attempt + 1}/{max_retries + 1})")
            except httpx.ConnectError:
                last_error = OllamaError(
                    f"Cannot connect to Ollama at {self.base_url}. "
                    "Is Ollama running? Install from https://ollama.ai and run: ollama serve"
                )
                break  # Don't retry connection errors
            except OllamaError:
                raise
            except Exception as e:
                last_error = OllamaError(f"Unexpected error: {e}")
                logger.error(f"Ollama generation error (attempt {attempt + 1}): {e}")

        raise last_error or OllamaError("Generation failed")

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_retries: int = 2,
    ) -> dict:
        """Generate a JSON response from the local model.

        Attempts to parse the response as JSON. Falls back to wrapping
        the raw text if parsing fails.
        """
        json_system = system_prompt + (
            "\n\nIMPORTANT: Respond ONLY with valid JSON. "
            "No markdown code fences, no explanatory text before or after the JSON."
        )

        raw = await self.generate(
            prompt=prompt,
            system_prompt=json_system,
            temperature=temperature,
            max_retries=max_retries,
        )

        return self._parse_json_response(raw)

    @staticmethod
    def _parse_json_response(raw: str) -> dict:
        """Parse a potentially messy or truncated LLM response as JSON."""
        # 1. Try direct parse
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        cleaned = raw.strip()

        # 2. Try extracting from markdown code fence
        if "```json" in cleaned:
            start = cleaned.index("```json") + 7
            end = cleaned.index("```", start) if "```" in cleaned[start:] else len(cleaned)
            try:
                return json.loads(cleaned[start:end].strip())
            except json.JSONDecodeError:
                cleaned = cleaned[start:end].strip()
        elif "```" in cleaned:
            start = cleaned.index("```") + 3
            end = cleaned.index("```", start) if "```" in cleaned[start:] else len(cleaned)
            try:
                return json.loads(cleaned[start:end].strip())
            except json.JSONDecodeError:
                cleaned = cleaned[start:end].strip()

        # 3. Try finding JSON object boundaries
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            if start_char in cleaned:
                start = cleaned.index(start_char)
                end = cleaned.rindex(end_char) + 1 if end_char in cleaned else len(cleaned)
                try:
                    return json.loads(cleaned[start:end])
                except json.JSONDecodeError:
                    pass

        # 4. Attempt to repair truncated JSON (handles token-limit cutoff for large code generation)
        for start_char in ["{", "["]:
            if start_char in cleaned:
                start = cleaned.index(start_char)
                partial = cleaned[start:]
                for suffix in ['"}]}', '"]}', "}]}", "}}", "]}", "}"]:
                    try:
                        return json.loads(partial + suffix)
                    except json.JSONDecodeError:
                        continue

        # 5. Last resort: wrap as raw text for caller-side recovery
        return {"raw_response": raw}


class OllamaError(Exception):
    """Error communicating with Ollama."""
    pass


# Singleton instance
ollama_client = OllamaClient()
