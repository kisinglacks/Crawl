from typing import Any, Dict, Optional

import requests
try:  # pragma: no cover - optional dependency
    from loguru import logger  # type: ignore
except Exception:  # pragma: no cover - fallback for environments without loguru
    import logging

    logger = logging.getLogger(__name__)
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)

from tenacity import retry, stop_after_attempt, wait_exponential

from . import utils


def get_session(headers: Optional[Dict[str, str]] = None) -> requests.Session:
    session = requests.Session()
    if headers:
        session.headers.update(headers)
    session.headers.setdefault("User-Agent", utils.random_ua())
    return session


def request_with_retry(
    session: requests.Session,
    url: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> requests.Response:
    retry_times = kwargs.pop("retry", 3)
    backoff = kwargs.pop("backoff", 1.5)
    timeout = kwargs.pop("timeout", 15)

    @retry(stop=stop_after_attempt(retry_times), wait=wait_exponential(multiplier=backoff))
    def _request() -> requests.Response:
        logger.debug(f"requesting {url}")
        resp = session.request(method, url, params=params, timeout=timeout, **kwargs)
        resp.raise_for_status()
        return resp

    return _request()
