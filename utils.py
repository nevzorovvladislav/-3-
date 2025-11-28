#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилиты приложения: логирование, безопасная работа с файлами.
"""

import time
import traceback
from pathlib import Path
from typing import Callable
from config import LOG_FILE
import tkinter.messagebox as messagebox


def safe_write_file(path: Path, data: str) -> None:
    """Безопасно записать текст в файл; не бросает исключения наружу."""
    try:
        path.write_text(data, encoding="utf-8")
    except Exception:
        pass


def log_exception(exc: Exception) -> None:
    """Записать исключение в лог-файл с меткой времени."""
    try:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        tb = traceback.format_exc()
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{now}] Exception: {exc}\n{tb}\n")
    except Exception:
        pass


def safe_function_wrapper(func: Callable) -> Callable:
    """
    Обертка, которая возвращает функцию-обработчик,
    вызывающую func и ловящую исключения с логированием и диалогом.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_exception(e)
            try:
                messagebox.showerror("Ошибка", f"Произошла ошибка:\n{e}")
            except Exception:
                print(f"Error showing messagebox: {e}")
    return wrapper