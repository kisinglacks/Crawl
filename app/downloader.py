from pathlib import Path
from typing import Iterable

import requests

from .anti_block import get_session, request_with_retry


def download_images(urls: Iterable[str], dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    session = get_session()
    for url in urls:
        try:
            resp = request_with_retry(session, url)
            fname = dest / Path(url).name
            fname.write_bytes(resp.content)
        except Exception:  # noqa: BLE001
            continue
