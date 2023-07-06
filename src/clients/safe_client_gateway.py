import logging
from functools import cache
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests

logger = logging.getLogger(__name__)


@cache
def setup_session() -> requests.Session:
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def flush(
    cgw_url: Optional[str],
    cgw_flush_token: Optional[str],
    alternative_cgw_url: Optional[str],
    alternative_cgw_flush_token: Optional[str],
    json: Dict[str, Any],
) -> None:
    if cgw_url is None:
        logger.error("CGW_URL is not set. Skipping hook call")
        return
    if cgw_flush_token is None:
        logger.error("CGW_FLUSH_TOKEN is not set. Skipping hook call")
        return
    if (alternative_cgw_url is not None) and (alternative_cgw_flush_token is None):
        logger.error(
            "ALTERNATIVE_CGW_FLUSH_TOKEN is not set. Skipping alternative hook call"
        )

    urls = [cgw_url, alternative_cgw_url]
    flush_urls = list(map(lambda url: urljoin(url, "/v2/flush"), urls))
    flush_tokens = [cgw_flush_token, alternative_cgw_flush_token]

    try:
        for url, token in zip(flush_urls, flush_tokens):
            post = setup_session().post(
                url,
                json=json,
                headers={"Authorization": f"Basic {token}"},
            )
        post.raise_for_status()
    except Exception as error:
        logger.error(error)
