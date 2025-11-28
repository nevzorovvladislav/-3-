#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурационные константы и настройки приложения.
"""

from pathlib import Path

# Основные константы приложения
APP_NAME = "Крестики-нолики — Вариант A"
DEFAULT_WINDOW_WIDTH = 640
DEFAULT_WINDOW_HEIGHT = 640
MIN_WINDOW_SIZE = 300

# Пути к файлам
SETTINGS_FILE = Path.home() / ".tictactoe_variant_a_settings.json"
SCORE_FILE = Path.home() / ".tictactoe_variant_a_score.json"
LOG_FILE = Path.home() / ".tictactoe_variant_a_errors.log"

# Соответствие клавиш клеткам доски (для горячих клавиш 1..9)
KEY_TO_CELL = {
    "1": (2, 0),
    "2": (2, 1),
    "3": (2, 2),
    "4": (1, 0),
    "5": (1, 1),
    "6": (1, 2),
    "7": (0, 0),
    "8": (0, 1),
    "9": (0, 2),
}

# Темы оформления (цветовые схемы)
THEMES = {
    "Classic": {
        "bg": "#f0f0f0",
        "board_bg": "#ffffff",
        "line": "#333333",
        "x_color": "#d33c3c",
        "o_color": "#2b6cb0",
        "highlight": "#ffd54f",
        "status_bg": "#e6e6e6",
        "btn_bg": "#f7f7f7",
    },
    "Dark": {
        "bg": "#2e2e2e",
        "board_bg": "#1f1f1f",
        "line": "#ffffff",
        "x_color": "#ff6b6b",
        "o_color": "#66d9ef",
        "highlight": "#ffaa00",
        "status_bg": "#212121",
        "btn_bg": "#2f2f2f",
    },
    "Green": {
        "bg": "#e8f5e9",
        "board_bg": "#ffffff",
        "line": "#2e7d32",
        "x_color": "#2e7d32",
        "o_color": "#1b5e20",
        "highlight": "#a5d6a7",
        "status_bg": "#c8e6c9",
        "btn_bg": "#f1f8e9",
    },
}