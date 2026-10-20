"""ForgeTeam AI - Groq Cloud LLM Client for ultra-fast, free cloud inference."""

import json
import logging
import httpx
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class GroqClient:
    """Client for Groq Cloud API (free tier, OpenAI-compatible)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.api_key = api_key or settings.groq_api_key
        self.model = model or settings.groq_model
        self.base_url = (base_url or settings.groq_base_url).rstrip("/")
        self.timeout = timeout or settings.groq_timeout

    def is_configured(self) -> bool:
        """Check if Groq API key is present."""
        return bool(self.api_key and self.api_key.strip())

    def set_api_key(self, key: str) -> None:
        """Update API key dynamically in memory and persist to .env."""
        cleaned = key.strip()
        self.api_key = cleaned
        settings.groq_api_key = cleaned

        # Persist to .env file
        try:
            env_path = settings.model_config.get("env_file", ".env")
            from pathlib import Path
            p = Path(env_path)
            lines = []
            key_found = False
            if p.exists():
                for line in p.read_text(encoding="utf-8").splitlines():
                    if line.startswith("GROQ_API_KEY="):
                        lines.append(f"GROQ_API_KEY={cleaned}")
                        key_found = True
                    else:
                        lines.append(line)
            if not key_found:
                lines.append(f"GROQ_API_KEY={cleaned}")
            p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        except Exception as e:
            logger.warning(f"Could not persist GROQ_API_KEY to .env: {e}")

    async def check_connection(self) -> bool:
        """Verify if Groq API key is valid and service reachable."""
        if not self.is_configured():
            return False
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/models", headers=headers)
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"Groq connection check failed: {e}")
            return False

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.4,
        max_retries: int = 2,
    ) -> str:
        """Generate a completion using Groq Cloud LPU inference."""
        if not self.is_configured():
            raise GroqError(
                "Groq API key not configured. Add GROQ_API_KEY to your .env file or Settings."
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": settings.groq_max_tokens,
            "response_format": {"type": "json_object"},
        }

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        choices = data.get("choices", [])
                        if choices:
                            content = choices[0].get("message", {}).get("content", "")
                            if content:
                                return content
                        raise GroqError("Empty response from Groq")
                    elif resp.status_code == 401:
                        raise GroqError("Invalid Groq API key. Please check your credentials.")
                    elif resp.status_code == 429:
                        raise GroqError("Groq rate limit reached. Please wait a moment and retry.")
                    else:
                        raise GroqError(f"Groq error ({resp.status_code}): {resp.text[:400]}")
            except httpx.TimeoutException:
                last_error = GroqError("Groq request timed out")
                logger.warning(f"Groq timeout (attempt {attempt + 1}/{max_retries + 1})")
            except GroqError:
                raise
            except Exception as e:
                last_error = GroqError(f"Unexpected Groq error: {e}")
                logger.error(f"Groq generation error: {e}")

        raise last_error or GroqError("Groq generation failed")

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_retries: int = 2,
    ) -> dict:
        """Generate and parse structured JSON from Groq."""
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
        """Clean and parse JSON from model output, with truncation repair."""
        # 1. Direct parse
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        cleaned = raw.strip()

        # 2. Strip markdown fences
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

        # 3. Find JSON object boundaries
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            if start_char in cleaned:
                start = cleaned.index(start_char)
                end = cleaned.rindex(end_char) + 1 if end_char in cleaned else len(cleaned)
                try:
                    return json.loads(cleaned[start:end])
                except json.JSONDecodeError:
                    pass

        # 4. Attempt to repair truncated JSON (common with large code outputs near token limit)
        # Try adding missing closing brackets to recover partial objects
        for start_char in ["{", "["]:
            if start_char in cleaned:
                start = cleaned.index(start_char)
                partial = cleaned[start:]
                # Count open/close delimiters and close them
                for suffix in ['"}]}', '"]}', "}]}", "}}", "]}", "}"]:
                    try:
                        return json.loads(partial + suffix)
                    except json.JSONDecodeError:
                        continue

        # 5. Last resort: return as raw text so caller can attempt regex recovery
        return {"raw_response": raw}


class GroqError(Exception):
    """Error interacting with Groq Cloud."""
    pass


groq_client = GroqClient()
