import argparse
import sys
import time

import requests


def check(url: str, timeout: int, max_latency_ms: int) -> tuple[bool, str]:
    start = time.time()
    try:
        response = requests.get(url, timeout=timeout)
        latency_ms = round((time.time() - start) * 1000, 2)
        if response.status_code != 200:
            return False, f"{url} returned HTTP {response.status_code} in {latency_ms} ms: {response.text[:300]}"
        if latency_ms > max_latency_ms:
            return False, f"{url} latency {latency_ms} ms exceeded threshold {max_latency_ms} ms"
        return True, f"{url} passed in {latency_ms} ms"
    except Exception as exc:
        return False, f"{url} failed: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--max-latency-ms", type=int, default=1500)
    args = parser.parse_args()

    endpoints = ["/health", "/orders"]
    ok = True
    for endpoint in endpoints:
        passed, message = check(args.base_url.rstrip("/") + endpoint, args.timeout, args.max_latency_ms)
        print(message)
        ok = ok and passed
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
