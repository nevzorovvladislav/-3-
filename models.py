#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модели данных приложения.
"""

from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import List, Optional, Tuple
from config import SETTINGS_FILE, SCORE_FILE, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
from utils import log_exception


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
        """Загрузить настройки из файла."""
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
        """Сохранить настройки в файл."""
        try:
            SETTINGS_FILE.write_text(
                json.dumps(asdict(self), ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
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
        """Загрузить счет из файла."""
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

    def save(self, autosave: bool = True) -> None:
        """Сохранить счет в файл."""
        if not autosave:
            return
        try:
            SCORE_FILE.write_text(
                json.dumps(asdict(self), ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            log_exception(e)