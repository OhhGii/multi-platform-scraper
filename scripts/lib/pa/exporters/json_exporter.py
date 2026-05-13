import json
import asyncio
from pathlib import Path

async def export_json(records: list[dict], path: str) -> None:
    """将记录列表写入 JSON 文件（UTF-8，缩进 2）。"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(_write_json, records, path)

def _write_json(records: list[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
