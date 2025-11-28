#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tic-Tac-Toe — Вариант A (разделенная версия)
----------------------------------
Главный файл для запуска приложения
"""

import traceback
import sys
from tkinter import messagebox

from gui import TicTacToeGUI
from utils import log_exception

def main():
    """Главная функция запуска приложения"""
    try:
        gui = TicTacToeGUI()
        gui.run()
    except Exception as e:
        log_exception(e)
        # В крайнем случае вывести ошибку в консоль
        tb = traceback.format_exc()
        print("Unhandled exception during startup:", e, file=sys.stderr)
        print(tb, file=sys.stderr)
        try:
            messagebox.showerror("Ошибка", f"Не удалось запустить приложение: {e}")
        except Exception:
            pass

if __name__ == "__main__":
    main()