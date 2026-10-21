"""設定層的啟動守門測試：對應計畫 I/O & Edge-Case Matrix 的第四列。

矩陣列：缺 `SECRET_KEY`／`PGPASSFILE` 時啟動即失敗並指出缺哪一個（AD-23）。
這些檢查發生在 import 階段，因此用子行程執行，才能觀察到真正的失敗。
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
DJANGO_BOOTSTRAP = "import django; django.setup()"


def _boot_with_env(env_overrides: dict[str, str | None]) -> subprocess.CompletedProcess:
    """在乾淨環境下嘗試啟動 Django，回傳子行程結果。"""
    env = os.environ.copy()
    for key, value in env_overrides.items():
        if value is None:
            env.pop(key, None)
        else:
            env[key] = value

    env["DJANGO_SETTINGS_MODULE"] = "config.settings.prod"
    env["PYTHONPATH"] = str(BACKEND_DIR)
    return subprocess.run(
        [sys.executable, "-c", DJANGO_BOOTSTRAP],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
    )


def test_prod_settings_fail_without_secret_key():
    """缺 SECRET_KEY 時啟動失敗，且訊息指出缺哪一個。"""
    result = _boot_with_env({"SECRET_KEY": None, "ALLOWED_HOSTS": None})

    assert result.returncode != 0
    assert "SECRET_KEY" in result.stderr


def test_base_settings_fail_without_pgpassfile():
    """缺 PGPASSFILE 時啟動失敗，且訊息指出缺哪一個（不降級為無密碼連線）。"""
    result = _boot_with_env(
        {
            "PGPASSFILE": None,
            "SECRET_KEY": "x" * 50,
            "ALLOWED_HOSTS": "localhost",
            "DB_NAME": "AILearn",
        }
    )

    assert result.returncode != 0
    assert "PGPASSFILE" in result.stderr


def test_test_settings_never_point_at_the_real_database(settings):
    """測試環境絕不連 `AILearn`（AD-14）。"""
    assert settings.DATABASES["default"]["NAME"] != "AILearn"
