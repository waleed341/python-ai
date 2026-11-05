"""Safe JSON HTTP requests with bounded retries and a one-hour memory cache."""
import time
import httpx

_cache: dict = {}

def get_json(url: str, params: dict | None = None, *, client=None) -> dict:
    """Fetch an object; retry transport/5xx failures, never retry 4xx or bad JSON."""
    key = (url, tuple(sorted((params or {}).items())))
    cached = _cache.get(key)
    if cached and time.monotonic() - cached[0] < 3600:
        return cached[1]
    fetch = client.get if client is not None else httpx.get
    for attempt in range(3):
        try:
            response = fetch(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object")
            _cache[key] = (time.monotonic(), data)
            return data
        except httpx.HTTPStatusError as error:
            if error.response.status_code < 500:
                raise ValueError(f"API returned HTTP {error.response.status_code}") from error
        except httpx.TransportError:
            pass
        except ValueError as error:
            raise ValueError("API returned invalid JSON") from error
        if attempt < 2:
            time.sleep(0.2 * (attempt + 1))
    raise ValueError("API unavailable after 3 attempts; check the internet connection")

if __name__ == "__main__":
    from unittest.mock import patch
    def offline(request):
        raise httpx.ConnectError("Offline", request=request)
    with httpx.Client(transport=httpx.MockTransport(offline)) as client, patch("time.sleep"):
        try:
            get_json("https://demo.invalid/offline", client=client)
        except ValueError as error:
            assert "3 attempts" in str(error)
        else:
            raise AssertionError("Offline request should fail safely")
    calls = []
    def success(request):
        calls.append(request)
        return httpx.Response(200, json={"demo":True})
    with httpx.Client(transport=httpx.MockTransport(success)) as client:
        assert get_json("https://demo.invalid/cache", client=client) == {"demo":True}
        get_json("https://demo.invalid/cache", client=client)
        assert len(calls) == 1
    print("API: offline/retry and hourly cache tests passed.")
