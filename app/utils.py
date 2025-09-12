import hashlib
import random
import time
from pathlib import Path
from typing import List

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]


def random_ua() -> str:
    """Return a random User-Agent string."""
    return random.choice(USER_AGENTS)


def load_authors(file_path: str) -> List[str]:
    """Read author URLs from a file, ignoring comments and blank lines."""
    path = Path(file_path)
    authors = []
    if not path.exists():
        return authors
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        authors.append(line)
    return authors


def md5(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def random_delay(min_delay: float, max_delay: float) -> None:
    time.sleep(random.uniform(min_delay, max_delay))
