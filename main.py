#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tic-Tac-Toe — Вариант A (модульная версия)
------------------------------------------
Главный файл приложения для запуска игры.
"""

import sys
import traceback
from gui import TicTacToeGUI
from utils import log_exception
import tkinter as tk
from tkinter import messagebox


def main():
    """Основная функция запуска приложения."""
    try:
        gui = TicTacToeGUI()
        gui.run()
    except Exception as e:
        log_exception(e)
        tb = traceback.format_exc()
        print("Unhandled exception during startup:", e, file=sys.stderr)
        print(tb, file=sys.stderr)
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Ошибка", f"Не удалось запустить приложение: {e}")
            root.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    main()