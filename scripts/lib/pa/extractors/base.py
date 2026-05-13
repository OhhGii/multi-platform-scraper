import asyncio
import logging
from playwright.async_api import Page
from pa.engines.base import FieldRule

logger = logging.getLogger(__name__)

_TIMEOUT = 10.0

MISSING = "__missing__"  # 选择器不存在时的标记值，区别于提取到的空字符串


async def _wait_for_element(page: Page, selector: str):
    """Wait up to 10s for element, return None on timeout (no exception)."""
    try:
        return await page.wait_for_selector(selector, timeout=int(_TIMEOUT * 1000))
    except Exception:
        return None


async def probe_selectors(page: Page, rules: list[FieldRule]) -> list[str]:
    """返回在当前页面中找不到的选择器名称列表（快速检测，不等待）。"""
    missing = []
    for rule in rules:
        try:
            el = await page.query_selector(rule.selector)
            if el is None:
                missing.append(rule.name)
        except Exception:
            missing.append(rule.name)
    return missing


async def extract_fields(page: Page, rules: list[FieldRule]) -> list[dict]:
    """
    按 FieldRule 列表提取字段，返回单条记录字典列表。

    - 选择器 10s 内未找到：字段值为 MISSING（"__missing__"），表示选择器不存在
    - 元素存在但提取失败：字段值为空字符串
    - rule.summarize=True 的字段：值不变，在 __summarize__ 键里列出字段名，
      由 skill 层 agent 负责对这些字段做摘要替换
    """
    record: dict = {}
    summarize_fields: list[str] = []

    for rule in rules:
        el = await _wait_for_element(page, rule.selector)
        if el is None:
            logger.warning("Selector not found within %.1fs: %s -> %s", _TIMEOUT, rule.name, rule.selector)
            record[rule.name] = MISSING
            continue
        try:
            if rule.attr == "text":
                record[rule.name] = await el.inner_text()
            elif rule.attr == "html":
                record[rule.name] = await el.inner_html()
            else:
                record[rule.name] = await el.get_attribute(rule.attr) or ""
        except Exception as e:
            logger.warning("Failed to extract field %s: %s", rule.name, e)
            record[rule.name] = ""

        if rule.summarize and record[rule.name] not in (MISSING, ""):
            summarize_fields.append(rule.name)

    if summarize_fields:
        record["__summarize__"] = summarize_fields

    return [record]
