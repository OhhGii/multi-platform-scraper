import asyncio
import random
from pathlib import Path
from playwright.async_api import BrowserContext, Page
from pa.cdp.manager import connect_cdp
from pa.engines.base import Engine, FieldRule
from pa.extractors.base import extract_fields

STEALTH_SCRIPT_PATH = str(Path(__file__).parent.parent / "stealth" / "anti_crawler.js")

_URL_SETTLE_INTERVAL = 0.3  # 秒，轮询间隔
_URL_SETTLE_TIMEOUT = 10.0  # 秒，最多等待


class RPAEngine(Engine):
    def __init__(self) -> None:
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    async def open(self, url: str) -> None:
        self._context = await connect_cdp()
        self._page = await self._context.new_page()
        await self._page.add_init_script(path=STEALTH_SCRIPT_PATH)
        await self._page.goto(url)
        await self._wait_for_final_url()

    async def get_dom(self) -> str:
        if not self._page:
            return ""
        return await self._page.content()

    async def scroll_to_bottom(self) -> None:
        if not self._page:
            return
        for _ in range(5):
            await self._page.mouse.wheel(0, random.randint(300, 600))
            await self._random_delay()

    async def extract(self, rules: list[FieldRule]) -> list[dict]:
        if not self._page:
            return []
        return await extract_fields(self._page, rules)

    async def extract_list_items(self, item_selector: str, rules: list[FieldRule]) -> list[dict]:
        """
        提取列表页的多条记录。

        对每个匹配 item_selector 的条目：
        - 自动抓取条目上的完整 href（含所有 query 参数）存入 __url__
        - 再按 rules 提取各字段

        这样详情页 URL（含 token）由页面 DOM 决定，不手动构造。
        """
        if not self._page:
            return []

        items = await self._page.query_selector_all(item_selector)
        results = []
        for item in items:
            record: dict = {}

            # 自动提取完整 href（含 xsec_token 等参数）
            href = await item.get_attribute("href")
            if href is None:
                # 条目本身不是 <a>，尝试找内部第一个链接
                link = await item.query_selector("a[href]")
                if link:
                    href = await link.get_attribute("href")
            record["__url__"] = href or ""

            # 在条目范围内提取各字段
            for rule in rules:
                try:
                    el = await item.query_selector(rule.selector)
                    if el is None:
                        record[rule.name] = "__missing__"
                        continue
                    if rule.attr == "text":
                        record[rule.name] = await el.inner_text()
                    elif rule.attr == "html":
                        record[rule.name] = await el.inner_html()
                    else:
                        record[rule.name] = await el.get_attribute(rule.attr) or ""
                except Exception:
                    record[rule.name] = ""

            results.append(record)
        return results

    async def close(self) -> None:
        if self._page:
            await self._page.close()
        # 不关闭 _context：context 是用户真实浏览器的 context，关掉会销毁登录态

    async def _wait_for_final_url(self) -> None:
        """等待页面 URL 稳定（连续 N 秒不再变化），处理中转页跳转。"""
        if not self._page:
            return
        elapsed = 0.0
        prev_url = self._page.url
        while elapsed < _URL_SETTLE_TIMEOUT:
            await asyncio.sleep(_URL_SETTLE_INTERVAL)
            elapsed += _URL_SETTLE_INTERVAL
            current_url = self._page.url
            if current_url == prev_url:
                return  # URL 稳定，导航完成
            prev_url = current_url
        # 超时后不报错，以当前 URL 为准继续

    async def _human_click(self, selector: str) -> None:
        """三段式鼠标事件：move → down → up，间隔 100ms，模拟真实点击。"""
        if not self._page:
            return
        el = await self._page.query_selector(selector)
        if not el:
            return
        box = await el.bounding_box()
        if not box:
            return
        x = box["x"] + box["width"] / 2
        y = box["y"] + box["height"] / 2
        await self._page.mouse.move(x, y)
        await asyncio.sleep(0.1)
        await self._page.mouse.down()
        await asyncio.sleep(0.1)
        await self._page.mouse.up()

    async def _random_delay(self) -> None:
        await asyncio.sleep(random.uniform(1.0, 3.0))

    async def extract_cookies_after_login(self) -> list[dict]:
        """用户手动登录后，从 browser context 摘取所有 Cookie。"""
        if not self._context:
            return []
        return await self._context.cookies()
