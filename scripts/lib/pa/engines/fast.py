import httpx
from pathlib import Path
from playwright.async_api import BrowserContext, Page
from pa.cdp.manager import connect_cdp
from pa.engines.base import Engine, FieldRule
from pa.extractors.base import extract_fields

STEALTH_SCRIPT_PATH = str(Path(__file__).parent.parent / "stealth" / "anti_crawler.js")

async def fetch_via_http(url: str, cookies: list[dict] | None = None) -> str:
    """用 httpx 直接获取页面 HTML，携带 cookies。"""
    cookie_header = "; ".join(f"{c['name']}={c['value']}" for c in (cookies or []))
    headers = {"Cookie": cookie_header} if cookie_header else {}
    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.text

class FastEngine(Engine):
    def __init__(self) -> None:
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._dom: str = ""

    async def open(self, url: str) -> None:
        self._context = await connect_cdp()
        self._page = await self._context.new_page()
        await self._page.add_init_script(path=STEALTH_SCRIPT_PATH)
        try:
            cookies = await self._context.cookies()
            self._dom = await fetch_via_http(url, cookies=cookies)
        except Exception:
            await self._page.goto(url)
            self._dom = await self._page.content()

    async def get_dom(self) -> str:
        return self._dom

    async def scroll_to_bottom(self) -> None:
        if self._page:
            await self._page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    async def extract(self, rules: list[FieldRule]) -> list[dict]:
        if not self._page:
            return []
        return await extract_fields(self._page, rules)

    async def close(self) -> None:
        if self._page:
            await self._page.close()
        # 不关闭 _context：context 是用户真实浏览器的 context，关掉会销毁登录态
