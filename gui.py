#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Графический интерфейс приложения.
"""

import sys
import time
import traceback
from typing import List, Optional, Tuple, Callable, Dict

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog, filedialog
except Exception:
    print("Ошибка импорта tkinter. Установите tkinter для вашей версии Python.")
    raise

from config import APP_NAME, MIN_WINDOW_SIZE, KEY_TO_CELL, THEMES, LOG_FILE
from models import Settings, Score
from game_logic import Game
from utils import log_exception, safe_function_wrapper


class TicTacToeGUI:
    """GUI-приложение, использующее tkinter."""

    def __init__(self, root: Optional[tk.Tk] = None):
        # Загружаем настройки и счет при старте
        self.settings = Settings.load()
        self.score = Score.load()

        # Инициализация центральных объектов
        self.root = root or tk.Tk()
        self.root.title(APP_NAME)
        # Применяем настройки (ширина/высота)
        w = max(self.settings.width, MIN_WINDOW_SIZE)
        h = max(self.settings.height, MIN_WINDOW_SIZE)
        self.root.geometry(f"{w}x{h}")
        self.root.minsize(MIN_WINDOW_SIZE, MIN_WINDOW_SIZE)

        # Центральные модели
        self.game = Game()
        self.active_theme_name = self.settings.theme if self.settings.theme in THEMES else "Classic"
        self.theme = THEMES[self.active_theme_name]

        # UI элементы, которые нужно хранить
        self.canvas = None
        self.cell_widgets: Dict[Tuple[int, int], Dict[str, object]] = {}
        self.status_var = tk.StringVar()
        self.info_var = tk.StringVar()
        self.score_var = tk.StringVar()
        self.last_highlight: Optional[List[Tuple[int, int]]] = None

        # For animation/timers
        self._blink_state = False
        self._blink_job = None

        # Setup UI
        try:
            self._setup_style()
            self._create_menu()
            self._create_toolbar()
            self._create_board_area()
            self._create_status_area()
            self._bind_shortcuts()
            self._update_ui_from_state()
            # Centralized exception handling for mainloop callbacks
            self.root.report_callback_exception = self._handle_callback_exception
        except Exception as e:
            log_exception(e)
            messagebox.showerror("Ошибка инициализации", f"Ошибка при инициализации интерфейса:\n{e}")

    def _setup_style(self):
        """Настройка стилей (ttk) и внешнего вида."""
        try:
            self.root.configure(bg=self.theme["bg"])
        except Exception:
            pass

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            try:
                style.theme_use(style.theme_names()[0])
            except Exception:
                pass

        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=3)

    def _create_menu(self):
        menu = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Новая игра", command=self._safe(self.new_game))
        file_menu.add_command(label="Сброс счета", command=self._safe(self.reset_score))
        file_menu.add_separator()
        file_menu.add_command(label="Сохранить счет...", command=self._safe(self.save_score_as))
        file_menu.add_command(label="Загрузить счет...", command=self._safe(self.load_score_from))
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self._safe(self.on_close))
        menu.add_cascade(label="Файл", menu=file_menu)

        # Settings menu
        settings_menu = tk.Menu(menu, tearoff=0)
        settings_menu.add_command(label="Размер окна...", command=self._safe(self.change_window_size))
        settings_menu.add_checkbutton(label="Подсветка выигрышной линии", onvalue=1, offvalue=0,
                                      variable=tk.IntVar(value=1 if self.settings.show_highlight else 0),
                                      command=self._safe(self.toggle_highlight))
        settings_menu.add_checkbutton(label="Автосохранение счета", onvalue=1, offvalue=0,
                                      variable=tk.IntVar(value=1 if self.settings.autosave_score else 0),
                                      command=self._safe(self.toggle_autosave))
        menu.add_cascade(label="Настройки", menu=settings_menu)

        # View / Themes
        view_menu = tk.Menu(menu, tearoff=0)
        theme_menu = tk.Menu(view_menu, tearoff=0)
        for theme_name in THEMES.keys():
            theme_menu.add_command(label=theme_name, command=self._make_theme_switcher(theme_name))
        view_menu.add_cascade(label="Тема", menu=theme_menu)
        menu.add_cascade(label="Вид", menu=view_menu)

        # Help menu
        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="О программе", command=self._safe(self.show_about))
        help_menu.add_command(label="Прототип интерфейса", command=self._safe(self.show_prototype_info))
        menu.add_cascade(label="Справка", menu=help_menu)

        self.root.config(menu=menu)

    def _create_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=4, pady=2)

        new_btn = ttk.Button(toolbar, text="Новая игра", command=self._safe(self.new_game))
        new_btn.pack(side=tk.LEFT, padx=2)

        undo_btn = ttk.Button(toolbar, text="Отмена", command=self._safe(self.do_undo))
        undo_btn.pack(side=tk.LEFT, padx=2)

        size_btn = ttk.Button(toolbar, text="Размер окна", command=self._safe(self.change_window_size))
        size_btn.pack(side=tk.LEFT, padx=2)

        theme_label = ttk.Label(toolbar, text="Тема:")
        theme_label.pack(side=tk.LEFT, padx=(12, 2))
        theme_combo = ttk.Combobox(toolbar, values=list(THEMES.keys()), state="readonly")
        theme_combo.set(self.active_theme_name)
        theme_combo.bind("<<ComboboxSelected>>", lambda ev: self._safe(self.change_theme)(theme_combo.get()))
        theme_combo.pack(side=tk.LEFT, padx=2)

        spacer = ttk.Label(toolbar, text="")
        spacer.pack(side=tk.LEFT, expand=True)

        score_label = ttk.Label(toolbar, textvariable=self.score_var)
        score_label.pack(side=tk.RIGHT, padx=6)

    def _create_board_area(self):
        self.board_frame = ttk.Frame(self.root)
        self.board_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.canvas = tk.Canvas(self.board_frame, bg=self.theme["board_bg"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda ev: self._safe(self._on_canvas_resize)(ev.width, ev.height))

        self.cell_bbox: Dict[Tuple[int, int], Tuple[int, int, int, int]] = {}

        self.canvas.bind("<Button-1>", lambda ev: self._safe(self._on_canvas_click)(ev.x, ev.y))

        self._on_canvas_resize(self.canvas.winfo_width() or self.settings.width,
                               self.canvas.winfo_height() or self.settings.height)

    def _create_status_area(self):
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_label = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        info_label = ttk.Label(status_frame, textvariable=self.info_var, relief=tk.SUNKEN, anchor="e")
        info_label.pack(side=tk.RIGHT)

        self._update_score_var()

    def _update_score_var(self):
        self.score_var.set(f"X: {self.score.x_wins}   O: {self.score.o_wins}   Ничьи: {self.score.draws}")

    def _update_status_var(self):
        if self.game.winner is None:
            self.status_var.set(f"Ход: {self.game.current}  (горячие клавиши 1-9)")
        elif self.game.winner == "Draw":
            self.status_var.set("Ничья!")
        else:
            self.status_var.set(f"Победитель: {self.game.winner}")

    def _update_ui_from_state(self):
        self._update_status_var()
        self._redraw_board()

    def _on_canvas_resize(self, width: int, height: int):
        try:
            self.canvas.delete("all")
            pad = 20
            size = min(max(40, width - 2 * pad), max(40, height - 2 * pad))
            x0 = (width - size) // 2
            y0 = (height - size) // 2
            x1 = x0 + size
            y1 = y0 + size
            self.board_bbox = (x0, y0, x1, y1)

            self.canvas.create_rectangle(x0 - 6, y0 - 6, x1 + 6, y1 + 6,
                                         fill=self.theme["board_bg"], outline=self.theme["line"], width=2)

            cell_w = size / 3.0
            cell_h = size / 3.0
            self.cell_bbox.clear()
            for r in range(3):
                for c in range(3):
                    cx0 = int(x0 + c * cell_w)
                    cy0 = int(y0 + r * cell_h)
                    cx1 = int(cx0 + cell_w)
                    cy1 = int(cy0 + cell_h)
                    self.cell_bbox[(r, c)] = (cx0, cy0, cx1, cy1)
                    self.canvas.create_rectangle(cx0, cy0, cx1, cy1, fill=self.theme["board_bg"],
                                                 outline=self.theme["line"])
            self._redraw_board()
        except Exception as e:
            log_exception(e)
            raise

    def _redraw_board(self):
        try:
            self.canvas.delete("mark")
            board = self.game.get_state_copy()
            for r in range(3):
                for c in range(3):
                    symbol = board[r][c]
                    bbox = self.cell_bbox.get((r, c))
                    if not bbox:
                        continue
                    if symbol == "X":
                        self._draw_x(bbox, tag="mark")
                    elif symbol == "O":
                        self._draw_o(bbox, tag="mark")
            self._update_highlight()
        except Exception as e:
            log_exception(e)
            raise

    def _draw_x(self, bbox: Tuple[int, int, int, int], tag: str = ""):
        x0, y0, x1, y1 = bbox
        pad = int(min(x1 - x0, y1 - y0) * 0.18)
        coords = (x0 + pad, y0 + pad, x1 - pad, y1 - pad)
        self.canvas.create_line(coords[0], coords[1], coords[2], coords[3],
                                fill=self.theme["x_color"], width=6, capstyle=tk.ROUND, tag=tag)
        self.canvas.create_line(coords[0], coords[3], coords[2], coords[1],
                                fill=self.theme["x_color"], width=6, capstyle=tk.ROUND, tag=tag)

    def _draw_o(self, bbox: Tuple[int, int, int, int], tag: str = ""):
        x0, y0, x1, y1 = bbox
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        r = min((x1 - x0), (y1 - y0)) * 0.36
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                outline=self.theme["o_color"], width=6, tag=tag)

    def _update_highlight(self):
        self.canvas.delete("highlight")
        if not self.settings.show_highlight:
            return
        line = self.game.get_winning_line()
        if not line:
            self.last_highlight = None
            return
        for (r, c) in line:
            bbox = self.cell_bbox.get((r, c))
            if not bbox:
                continue
            x0, y0, x1, y1 = bbox
            pad = int(min(x1 - x0, y1 - y0) * 0.06)
            self.canvas.create_rectangle