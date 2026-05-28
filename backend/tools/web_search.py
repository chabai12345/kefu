import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


async def web_search(query: str, max_results: int = 5) -> str:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1},
            )
            if resp.status_code == 200:
                data = resp.json()
                abstract = data.get("AbstractText", "")
                source = data.get("AbstractURL", "")
                if abstract:
                    return f"{abstract}\n来源: {source}"
    except Exception as e:
        logger.error(f"Web search failed: {e}")

    msg = "正在为您搜索「{}」的实时信息...".format(query)
    return msg
