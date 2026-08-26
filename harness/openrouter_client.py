"""
Minimal OpenRouter client. Reads OPENROUTER_API_KEY from the environment.
On Windows/CMD:  setx OPENROUTER_API_KEY "sk-or-..."   (then open a new shell)
httpx is used deliberately: bare urllib gets Cloudflare 403s.
"""
import os
import json
import hashlib
import httpx
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _mock_chat(model, messages):
    """Offline stub used when WJ_MOCK=1: no network, deterministic. Lets the real
    run_targets/run_judges scripts execute end-to-end to verify plumbing. NOT real data."""
    last = messages[-1]["content"]
    is_judge = "return ONLY this JSON" in last or "Score each 0-3" in last
    h = int(hashlib.md5((model + last[:160]).encode()).hexdigest(), 16)
    if is_judge:
        pick = lambda shift: (h >> shift) & 3
        payload = {"plainness": pick(0), "hedging": pick(2),
                   "deflection": pick(4), "severity_ack": pick(6)}
        return {"text": json.dumps(payload), "usage": {"prompt_tokens": 60, "completion_tokens": 25},
                "raw_model": model + "-MOCK"}
    return {"text": "[MOCK] The incident is documented; a brief neutral characterization follows.",
            "usage": {"prompt_tokens": 90, "completion_tokens": 40}, "raw_model": model + "-MOCK"}


class RateLimited(Exception):
    pass


def _key() -> str:
    k = os.environ.get("OPENROUTER_API_KEY")
    if not k:
        raise RuntimeError("OPENROUTER_API_KEY not set. On Windows: setx OPENROUTER_API_KEY \"sk-or-...\"")
    return k


@retry(
    reraise=True,
    retry=retry_if_exception_type((RateLimited, httpx.TransportError)),  # NOT 4xx — those are permanent
    wait=wait_exponential(multiplier=2, min=2, max=30),
    stop=stop_after_attempt(4),
)
def chat(model: str, messages: list, max_tokens: int, temperature: float,
         timeout: float = 90.0) -> dict:
    """Returns {'text': str, 'usage': {...}}. Retries only on 429/5xx/transport.
    4xx (404 bad slug, 400, 401) fail immediately so a dead model doesn't stall the pool."""
    if os.environ.get("WJ_MOCK"):
        return _mock_chat(model, messages)
    headers = {
        "Authorization": f"Bearer {_key()}",
        "HTTP-Referer": "https://github.com/RaphaelKhalid/whose-jury",
        "X-Title": "whose-jury",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    with httpx.Client(timeout=timeout) as client:
        r = client.post(OPENROUTER_URL, headers=headers, json=payload)
        if r.status_code == 429 or r.status_code >= 500:
            raise RateLimited(f"{r.status_code}: {r.text[:160]}")  # retryable
        r.raise_for_status()  # 4xx -> raises immediately, no retry
        data = r.json()
    choice = data["choices"][0]["message"]
    text = choice.get("content") or ""
    return {"text": text, "usage": data.get("usage", {}), "raw_model": data.get("model", model)}
