#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурация приложения - константы, настройки, темы
"""

from dataclasses import dataclass, asdict
from pathlib import Path
import json
from utils import log_exception

# ---------------------------------------------------------------------------
# Константы и настройки по умолчанию
# ---------------------------------------------------------------------------

APP_NAME = "Крестики-нолики"
DEFAULT_WINDOW_WIDTH = 640
DEFAULT_WINDOW_HEIGHT = 640
MIN_WINDOW_SIZE = 300
SETTINGS_FILE = Path.home() / ".tictactoe_variant_a_settings.json"
SCORE_FILE = Path.home() / ".tictactoe_variant_a_score.json"
LOG_FILE = Path.home() / ".tictactoe_variant_a_errors.log"

# Board coordinates mapping (for keyboard shortcuts 1..9)
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

# Themes (color schemes). Each theme is a dict of colors used in UI.
THEMES = {
    "Classic": {
        "bg": "#f0f0f0",
        "board_bg": "#ffffff",  # Белый фон доски
        "line": "#333333",
        "x_color": "#d33c3c",
        "o_color": "#2b6cb0",
        "highlight": "#ffd54f",
        "status_bg": "#e6e6e6",
        "btn_bg": "#f7f7f7",
    },
    "Dark": {
        "bg": "#2e2e2e",
        "board_bg": "#ffffff",  # Белый фон доски (было "#1f1f1f")
        "line": "#333333",
        "x_color": "#ff6b6b",
        "o_color": "#66d9ef",
        "highlight": "#ffaa00",
        "status_bg": "#212121",
        "btn_bg": "#2f2f2f",
    },
    "Green": {
        "bg": "#e8f5e9",
        "board_bg": "#ffffff",  # Белый фон доски
        "line": "#2e7d32",
        "x_color": "#2e7d32",
        "o_color": "#1b5e20",
        "highlight": "#a5d6a7",
        "status_bg": "#c8e6c9",
        "btn_bg": "#f1f8e9",
    },
}

@dataclass
class Settings:
    """Класс для хранения настроек приложения."""
    width: int = DEFAULT_WINDOW_WIDTH
    height: int = DEFAULT_WINDOW_HEIGHT
    theme: str = "Classic"
    show_highlight: bool = True
    autosave_score: bool = True

    @classmethod
    def load(cls) -> "Settings":
        if SETTINGS_FILE.exists():
            try:
                data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
                return cls(
                    width=int(data.get("width", DEFAULT_WINDOW_WIDTH)),
                    height=int(data.get("height", DEFAULT_WINDOW_HEIGHT)),
                    theme=str(data.get("theme", "Classic")),
                    show_highlight=bool(data.get("show_highlight", True)),
                    autosave_score=bool(data.get("autosave_score", True)),
                )
            except Exception as e:
                log_exception(e)
        return cls()

    def save(self) -> None:
        try:
            SETTINGS_FILE.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            log_exception(e)

@dataclass
class Score:
    """Хранение счета игроков и ничьих."""
    x_wins: int = 0
    o_wins: int = 0
    draws: int = 0

    @classmethod
    def load(cls) -> "Score":
        if SCORE_FILE.exists():
            try:
                data = json.loads(SCORE_FILE.read_text(encoding="utf-8"))
                return cls(
                    x_wins=int(data.get("x_wins", 0)),
                    o_wins=int(data.get("o_wins", 0)),
                    draws=int(data.get("draws", 0)),
                )
            except Exception as e:
                log_exception(e)
        return cls()

    def save(self) -> None:
        from models import settings  # Импортируем здесь, чтобы избежать циклического импорта
        if not settings.autosave_score:
            return
        try:
            SCORE_FILE.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            log_exception(e)