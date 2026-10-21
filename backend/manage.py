#!/usr/bin/env python
"""Django 管理指令進入點。

預設使用開發層設定（config.settings.dev）。
"""
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:  # pragma: no cover - 環境未安裝依賴時的提示
        raise ImportError(
            "無法匯入 Django，請先建立虛擬環境並安裝依賴："
            "uv venv .venv && uv pip install -r backend/requirements.txt"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
