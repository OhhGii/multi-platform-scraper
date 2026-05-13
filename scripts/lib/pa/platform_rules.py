from urllib.parse import urlparse

PLATFORM_RULES: dict[str, dict] = {
    "xiaohongshu.com": {"engine": "rpa", "login": "manual_scan"},
    "xhs.com":         {"engine": "rpa", "login": "manual_scan"},
    "mp.weixin.qq.com": {"engine": "rpa", "login": "manual_scan"},
    "weixin.qq.com":   {"engine": "rpa", "login": "manual_scan"},
    "douyin.com":      {"engine": "rpa", "login": "manual_scan"},
    "weibo.com":       {"engine": "rpa", "login": "manual_scan"},
    "_default":        {"engine": "fast", "login": "none"},
}

_KEYWORD_MAP: dict[str, str] = {
    "小红书": "xiaohongshu.com",
    "xhs": "xiaohongshu.com",
    "微信": "mp.weixin.qq.com",
    "公众号": "mp.weixin.qq.com",
    "微信公众号": "mp.weixin.qq.com",
    "抖音": "douyin.com",
    "微博": "weibo.com",
}

def resolve_platform(url_or_keyword: str) -> dict:
    """URL 或关键词 → 引擎配置字典。"""
    if url_or_keyword.startswith("http"):
        parsed = urlparse(url_or_keyword)
        host = (parsed.hostname or "").lstrip("www.").lower()
        for domain, rule in PLATFORM_RULES.items():
            if domain != "_default" and host.endswith(domain):
                return rule.copy()
        return PLATFORM_RULES["_default"].copy()

    keyword = url_or_keyword.strip()
    for kw, domain in _KEYWORD_MAP.items():
        if kw in keyword:
            return PLATFORM_RULES[domain].copy()
    return PLATFORM_RULES["_default"].copy()
