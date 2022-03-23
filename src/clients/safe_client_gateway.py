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
    cgw_url: Optional[str], cgw_flush_token: Optional[str], json: Dict[str, Any]
) -> None:
    if cgw_url is None:
        logger.error("CGW_URL is not set. Skipping hook call")
        return
    if cgw_flush_token is None:
        logger.error("CGW_FLUSH_TOKEN is not set. Skipping hook call")
        return

    url = urljoin(cgw_url, "/v2/flush")
    try:
        post = setup_session().post(
            url,
            json=json,
            headers={"Authorization": f"Basic {cgw_flush_token}"},
        )
        post.raise_for_status()
    except Exception as error:
        logger.error(error)
