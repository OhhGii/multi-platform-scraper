from playwright.async_api import async_playwright, BrowserContext

CDP_ERROR_MSG = """\
无法连接到 Chrome remote-debugging 端口（{port}）。
请先启动带 remote-debugging 的 Chrome：
  macOS: open -a "Google Chrome" --args --remote-debugging-port={port}
  Windows: chrome.exe --remote-debugging-port={port}
启动后重新运行。
"""

class CDPConnectionError(RuntimeError):
    pass

async def connect_cdp(port: int = 9224) -> BrowserContext:
    """接管用户已开启 remote-debugging 的真实 Chrome，返回第一个 BrowserContext。

    注意：返回的 BrowserContext 由调用方负责关闭。
    Playwright 实例通过 atexit 在进程退出时自动清理。
    """
    playwright = await async_playwright().start()
    try:
        browser = await playwright.chromium.connect_over_cdp(
            f"http://localhost:{port}"
        )
        contexts = browser.contexts
        if contexts:
            return contexts[0]
        # 没有已有 context 说明浏览器刚启动还没有任何窗口，新建一个
        # 注意：新建的 context 不含登录态，用户需要手动登录后重新运行
        return await browser.new_context()
    except Exception as e:
        await playwright.stop()
        raise CDPConnectionError(CDP_ERROR_MSG.format(port=port)) from e
