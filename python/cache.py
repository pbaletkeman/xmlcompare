"""Incremental comparison cache for xmlcompare --dirs mode.

Stores SHA-256 checksums of compared file pairs in a JSON file.
On subsequent --dirs runs, file pairs whose hashes haven't changed and
were equal last time are skipped, reducing work for large directory
comparisons where only a few files change between runs.

Usage (via CLI):
    python xmlcompare.py --dirs old/ new/ --cache .xmlcompare_cache.json

Usage (programmatic):
    import cache
    c = cache.load_cache(".cache.json")
    if cache.is_cached_equal(f1, f2, c):
        return []  # skip
    diffs = compare_xml_files(f1, f2, opts)
    cache.update_cache_entry(f1, f2, c, diffs)
    cache.save_cache(".cache.json", c)
"""

import hashlib
import json
from pathlib import Path


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def _cache_key(file1: str, file2: str) -> str:
    return f"{Path(file1).resolve()}|{Path(file2).resolve()}"


def load_cache(cache_file: str) -> dict:
    """Load the cache from *cache_file*. Returns empty dict if file doesn't exist."""
    p = Path(cache_file)
    if not p.exists():
        return {}
    try:
        with open(p) as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(cache_file: str, cache: dict) -> None:
    """Persist *cache* to *cache_file* as JSON."""
    with open(cache_file, 'w') as fh:
        json.dump(cache, fh, indent=2)


def is_cached_equal(file1: str, file2: str, cache: dict) -> bool:
    """Return True if both files match their cached hashes and the last result was equal."""
    key = _cache_key(file1, file2)
    if key not in cache:
        return False
    entry = cache[key]
    return (
        entry.get('hash1') == _sha256(file1)
        and entry.get('hash2') == _sha256(file2)
        and entry.get('equal') is True
    )


def update_cache_entry(file1: str, file2: str, cache: dict, diffs: list) -> None:
    """Record the comparison result for this file pair in the in-memory *cache* dict."""
    key = _cache_key(file1, file2)
    cache[key] = {
        'hash1': _sha256(file1),
        'hash2': _sha256(file2),
        'equal': len(diffs) == 0,
    }
