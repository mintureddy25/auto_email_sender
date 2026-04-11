"""
Resolve shortened URLs (lnkd.in, bit.ly, etc.) by following HTTP redirects.
Uses stdlib urllib so we don't need an extra dependency. Parallelized via
ThreadPoolExecutor since each call is network-bound.
"""

from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

DEFAULT_TIMEOUT = 3
MAX_WORKERS = 20


def resolve_url(url, timeout=DEFAULT_TIMEOUT):
    """Follow redirects and return the final URL, or None on failure."""
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=timeout) as resp:
            return resp.url
    except (URLError, HTTPError, ValueError, TimeoutError):
        return None
    except Exception:
        return None


def resolve_all(urls, timeout=DEFAULT_TIMEOUT, max_workers=MAX_WORKERS):
    """Resolve a list of URLs in parallel, dropping any that fail."""
    if not urls:
        return []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        results = pool.map(lambda u: resolve_url(u, timeout=timeout), urls)
    return [r for r, original in zip(results, urls) if r and r != original]


def resolve_map(urls, timeout=DEFAULT_TIMEOUT, max_workers=MAX_WORKERS):
    """Resolve a list of URLs in parallel and return {original: resolved} dict.

    Failed resolutions are mapped to themselves so callers can still look them up.
    Deduplicates input.
    """
    unique = list({u for u in urls if u})
    if not unique:
        return {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        results = pool.map(lambda u: resolve_url(u, timeout=timeout), unique)
    return {original: (resolved or original) for original, resolved in zip(unique, results)}
