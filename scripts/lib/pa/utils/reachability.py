import asyncio
import logging
import httpx

logger = logging.getLogger(__name__)

_TIMEOUT = 8.0   # 秒，单个 URL 超时阈值
_CONCURRENCY = 5  # 并发检测数


async def _check_one(client: httpx.AsyncClient, url: str) -> tuple[str, bool]:
    try:
        resp = await client.head(url, follow_redirects=True, timeout=_TIMEOUT)
        return url, resp.status_code < 500
    except Exception as e:
        logger.debug("Reachability check failed for %s: %s", url, e)
        return url, False


async def check_urls(urls: list[str]) -> dict[str, bool]:
    """
    批量检测 URL 可达性，返回 {url: reachable} 字典。

    使用 HEAD 请求，超时或 5xx 均视为不可达。
    并发数限制为 _CONCURRENCY，避免短时间内触发反爬。
    """
    results: dict[str, bool] = {}
    sem = asyncio.Semaphore(_CONCURRENCY)

    async def guarded(client: httpx.AsyncClient, url: str) -> None:
        async with sem:
            k, v = await _check_one(client, url)
            results[k] = v

    async with httpx.AsyncClient() as client:
        await asyncio.gather(*[guarded(client, url) for url in urls])

    unreachable = [u for u, ok in results.items() if not ok]
    if unreachable:
        logger.warning("Unreachable URLs: %s", unreachable)

    return results
