#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилиты: логирование, работа с файлами
"""

import time
import traceback
from pathlib import Path

def safe_write_file(path: Path, data: str) -> None:
    """Безопасно записать текст в файл; не бросает исключения наружу."""
    try:
        path.write_text(data, encoding="utf-8")
    except Exception:
        # Ничего не делаем — приложение не должно ломаться из-за неудачи сохранения
        pass

def log_exception(exc: Exception) -> None:
    """Записать исключение в лог-файл с меткой времени."""
    try:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        tb = traceback.format_exc()
        from config import LOG_FILE  # Импортируем здесь, чтобы избежать циклического импорта
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{now}] Exception: {exc}\n{tb}\n")
    except Exception:
        # если логирование не удалось — просто игнорируем, чтобы не ломать UX
        pass