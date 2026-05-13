## 📋 目录

- [它能做什么](#-它能做什么)
- [安装](#-安装)
- [快速开始](#-快速开始)
- [支持平台](#-支持平台)
- [工作原理](#-工作原理)
- [常见问题](#-常见问题)
- [合规声明](#-合规声明)

---

## ✨ 它能做什么

**用对话完成爬虫，不用写代码。**

- 🎯 **平台自动识别** — 你说"小红书"或贴一个 URL，自动选最优引擎
- 🔐 **登录态复用** — 手动登录一次，后续永久免登录
- 🛡️ **反爬突破** — 内置 stealth 注入，绕过 `navigator.webdriver` 检测
- 📊 **结构化导出** — 直接产出 CSV / JSON，Excel 双击打开就能用
- 🌐 **覆盖广** — 小红书、微信公众号、抖音、微博、普通网页通吃

适合谁：想批量收集网页信息又不想学 Python/Playwright 的人。

---

## 📦 安装

### 方式 1：让 Claude 自己装（推荐）

在 Claude Code 里直接说：

```
帮我安装这个 skill：https://github.com/OhhGii/multi-platform-scraper
```

Claude 会自动 clone 到 `~/.claude/skills/multi-platform-scraper/`，重启会话即可生效。

### 方式 2：手动 clone

```bash
git clone https://github.com/OhhGii/multi-platform-scraper.git ~/.claude/skills/multi-platform-scraper
cd ~/.claude/skills/multi-platform-scraper
pip install -e .
playwright install chromium
```

### 系统要求

- macOS / Linux / Windows
- Python ≥ 3.11
- Google Chrome（已安装即可，脚本会启动独立实例，不影响日常使用）

---

## 🚀 快速开始

装好后，在 Claude Code 里直接说人话：

```
帮我爬取小红书"数字游民"话题下的前 20 条笔记，要标题、作者、点赞数
```

Claude 会按 6 步引导你：

1. 确认目标（话题/URL）
2. 推荐引擎（自动选 RPA 或 Fast）
3. 确认要采集的字段
4. 确认条数 / 是否翻页
5. 处理登录（首次会让你在弹出的 Chrome 里扫码）
6. 执行并导出 CSV 到 `~/pa-output/<时间戳>_result.csv`

**首次使用强反爬平台时**，需要在弹出的独立 Chrome 窗口手动登录一次，登录态会自动保存到 `~/.pa-chrome/`，后续无需重复。

---

## 🌍 支持平台

| 平台 | 推荐引擎 | 登录方式 | 备注 |
|------|---------|---------|------|
| 小红书 | RPA | 扫码 | 反爬强，必须登录 |
| 微信公众号 | RPA | 扫码 | 反爬强 |
| 抖音 | RPA | 手动登录 | 反爬强 |
| 微博 | RPA | 手动登录 | 反爬中 |
| 普通网站 | Fast | 通常无需 | 速度快 10× |

未列出的平台也支持 — 让 Claude 试一下，它会自动判断。

---

## 🔧 工作原理

pa 采用**双引擎架构**：

**RPAEngine（拟人模式）**
通过 CDP 接管真实 Chrome，注入反检测脚本，模拟人类操作（随机延迟、鼠标轨迹）。慢但成功率高，适合强反爬平台。

**FastEngine（快速模式）**
HTTP 请求为主，Playwright 兜底渲染 SPA。资源占用低、速度快，适合普通网页。

**字段提取**采用声明式规则：

```python
FieldRule(name="title", selector="h1.title", attr="text")
```

缺失字段标记为 `__missing__` 而不是直接报错 —— 部分成功也能拿到结果。

### 可配置环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PA_OUTPUT_DIR` | `~/pa-output` | 导出文件目录 |
| `PA_CHROME_PORT` | `9224` | Chrome remote-debugging 端口 |
| `PA_CHROME_USER_DATA` | `~/.pa-chrome` | Chrome 用户数据目录 |
| `PA_CHROME_BIN` | `/Applications/Google Chrome.app/...` | Chrome 可执行文件路径 |

---

## ❓ 常见问题

**Q: 会影响我日常用的浏览器吗？**
不会。pa 启动的是独立 Chrome 实例（端口 9224，数据目录 `~/.pa-chrome`），与你日常浏览完全隔离。

**Q: 登录态会丢吗？**
只要不删 `~/.pa-chrome/`，登录态永久保留。平台主动让你重新登录时再操作一次即可。

**Q: 选择器变了怎么办？**
Claude 会根据实际 DOM 动态推断选择器；个别字段失效会标记为 `__missing__`，不会中断整个任务。

**Q: 能爬登录后的内容吗？**
能。RPA 模式专为此设计 —— 你手动登录一次，后续抓取自动带上 Cookie。

**Q: 速度大概多快？**
- Fast 模式：~50 条/分钟
- RPA 模式：~10 条/分钟（含随机延迟，避免触发风控）

---

## ⚖️ 合规声明

本工具仅供**学习研究和个人数据备份**使用。使用前请：

- 确认符合目标网站的服务条款和 `robots.txt`
- 控制采集频率，不对目标服务器造成负担
- 遵守当地法律法规
- **不得用于商业数据窃取或侵犯他人隐私**

作者不对滥用造成的后果负责。

---
