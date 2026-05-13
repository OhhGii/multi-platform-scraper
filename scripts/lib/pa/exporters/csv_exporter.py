import csv
import asyncio
from pathlib import Path

async def export_csv(records: list[dict], path: str) -> None:
    """将记录列表写入 CSV 文件。空记录列表写入空文件。"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    if not records:
        await asyncio.to_thread(Path(path).write_text, "")
        return
    fieldnames = list(records[0].keys())
    await asyncio.to_thread(_write_csv, records, fieldnames, path)

def _write_csv(records: list[dict], fieldnames: list[str], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
