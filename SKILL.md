---
name: pa
description: >
  通用网页爬虫 skill，用于采集微信公众号、小红书、普通网页等平台的结构化数据，
  导出为 CSV 或 JSON 文件。当用户提到"爬取"、"抓取"、"采集"某个网站或平台的内容，
  或者想把网页数据保存成文件时，使用此 skill。支持反爬能力较弱的普通网页（快速模式）
  和强反爬平台如小红书、微信公众号（RPA 模式）。即使用户没有明确说"爬虫"，
  只要他们想批量获取网页上的信息，也应触发此 skill。
compatibility:
  tools:
    - Bash
    - Read
    - Write
---

# pa — 通用爬虫 Skill

## 路径约定

本 skill 通过两个变量定位资源，避免硬编码：

- `PA_SKILL_DIR`：skill 自身所在目录（即本 SKILL.md 所在目录），所有命令通过它定位脚本与 Python 包。
- `PA_OUTPUT_DIR`：导出文件目录，默认 `${PA_OUTPUT_DIR:-$HOME/pa-output}`，用户可通过环境变量覆盖。

下文所有命令均使用上述变量，请勿替换为绝对路径。

---

## 前置条件

**启动爬虫专用 Chrome（与日常 Chrome 隔离，不影响已打开的标签页）：**

```bash
bash "$PA_SKILL_DIR/scripts/start_chrome.sh"
```

脚本会自动检测端口是否已就绪，已在运行则直接跳过，无需重复执行。登录态保存在 `$HOME/.pa-chrome`，下次启动自动复用。

**首次使用强反爬平台（小红书、公众号等）时**，脚本启动后在弹出的 Chrome 窗口中手动登录对应平台一次，后续爬取会自动复用登录态。

---

## 对话流程

按以下步骤与用户对话，每步只问一个问题：

### Step 1：目标确认

问用户：**"你想爬取哪个平台或 URL？"**

### Step 2：引擎推荐

拿到答案后，在 Bash 中调用 `resolve_platform()` 判断推荐引擎：

```bash
cd "$PA_SKILL_DIR" && python -c "
from pa.platform_rules import resolve_platform
import json
print(json.dumps(resolve_platform('<用户输入>')))
"
```

- 结果 `engine == "rpa"` → 告知用户：
  > "检测到 **[平台名]** 反爬较强，推荐 **RPA 模式**（会打开真实浏览器窗口，速度较慢，但成功率高）。是否采用？"

- 结果 `engine == "fast"` → 告知用户：
  > "推荐 **快速模式**（HTTP 直接请求 + Playwright 兜底，速度快）。是否采用？"

用户可以选择切换引擎。

### Step 3：字段配置

问用户：**"需要采集哪些字段？"**（例：标题、作者、发布时间、正文、点赞数）

### Step 4：范围配置

问用户：**"采集多少条？是否需要翻页？"**

### Step 5：登录处理

根据选定引擎：

- **FastEngine**：提示用户确认 Chrome 已开启 remote-debugging（已在前置条件说明）
- **RPAEngine**：告知用户：
  > "即将打开浏览器窗口，请在窗口中完成登录，登录成功后告诉我继续。"
  等待用户回复后再继续。

### Step 6：执行爬取

根据用户的字段输入，推断 CSS 选择器（或询问用户提供），然后在 Bash 中执行：

```python
import asyncio, os, datetime
from pa.engines.fast import FastEngine    # 或 from pa.engines.rpa import RPAEngine
from pa.engines.base import FieldRule
from pa.exporters.csv_exporter import export_csv

async def run():
    engine = FastEngine()    # 根据用户选择替换
    await engine.open('<URL>')
    await engine.scroll_to_bottom()
    rules = [
        FieldRule(name='<field1>', selector='<selector1>'),
        # 更多字段...
    ]
    records = await engine.extract(rules)
    await engine.close()
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir = os.environ.get('PA_OUTPUT_DIR', os.path.expanduser('~/pa-output'))
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f'{ts}_result.csv')
    await export_csv(records, out)
    print(f'导出完成：{out}')

asyncio.run(run())
```

完成后告知用户导出路径。

---

## 错误处理

| 错误 | 处理 |
|------|------|
| `CDPConnectionError` | 提示用户开启 Chrome remote-debugging，给出具体命令 |
| 元素未找到 | 继续执行，该字段值为空，完成后提示哪些字段为空 |
| 登录态失效（RPA） | 提示用户重新在浏览器窗口中登录，等待确认后继续 |
