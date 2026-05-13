#!/bin/bash
# 启动用于 pa 爬虫的独立 Chrome 实例
# - 与日常 Chrome 完全隔离，不影响已打开的标签页
# - 登录态保存在 $PA_CHROME_USER_DATA（默认 ~/.pa-chrome），下次启动自动复用
# - 端口可通过 PA_CHROME_PORT 覆盖（默认 9224），便于避开本机其他占用 9222/9223 的工具

CHROME="${PA_CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
USER_DATA="${PA_CHROME_USER_DATA:-$HOME/.pa-chrome}"
PORT="${PA_CHROME_PORT:-9224}"

if [ ! -f "$CHROME" ]; then
  echo "错误：找不到 Chrome，路径：$CHROME"
  exit 1
fi

# 验证端口上跑的是否是 Google Chrome DevTools（排除 Electron 应用等）
is_pa_chrome() {
  local info
  info=$(curl -s --max-time 2 "http://localhost:$PORT/json/version" 2>/dev/null)
  # Browser 字段含 "Chrome/" 且 User-Agent 不含 "Electron"
  echo "$info" | grep -q '"Browser"' && \
  echo "$info" | grep -q 'Chrome/' && \
  ! echo "$info" | grep -q 'Electron'
}

if is_pa_chrome; then
  echo "pa-chrome 已在运行（端口 $PORT），无需重启。"
  exit 0
fi

# 端口被占但不是 Google Chrome，报错
if lsof -ti tcp:$PORT &>/dev/null; then
  echo "错误：端口 $PORT 已被其他进程占用："
  lsof -i tcp:$PORT | head -3
  exit 1
fi

echo "启动 pa-chrome（独立实例，端口 $PORT，数据目录：$USER_DATA）..."
"$CHROME" \
  --remote-debugging-port=$PORT \
  --user-data-dir="$USER_DATA" \
  --no-first-run \
  --no-default-browser-check \
  &>/dev/null &

# 等待 Google Chrome DevTools 就绪
for i in $(seq 1 20); do
  if is_pa_chrome; then
    echo "就绪：http://localhost:$PORT"
    exit 0
  fi
  sleep 0.5
done

echo "超时：Chrome 未能在 10s 内就绪，请手动检查。"
exit 1
