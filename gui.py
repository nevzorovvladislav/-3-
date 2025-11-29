#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI приложения на tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from typing import Optional, Tuple, List, Dict, Callable
import traceback
import sys
import time
import json  # Добавлен недостающий импорт

from config import APP_NAME, MIN_WINDOW_SIZE, THEMES, KEY_TO_CELL
from models import Game, settings, score
from utils import log_exception

class TicTacToeGUI:
    """GUI-приложение, использующее tkinter."""

    def __init__(self, root: Optional[tk.Tk] = None):
        # Инициализация центральных объектов
        self.root = root or tk.Tk()
        self.root.title(APP_NAME)
        # Применяем настройки (ширина/высота)
        w = max(settings.width, MIN_WINDOW_SIZE)
        h = max(settings.height, MIN_WINDOW_SIZE)
        self.root.geometry(f"{w}x{h}")
        self.root.minsize(MIN_WINDOW_SIZE, MIN_WINDOW_SIZE)

        # Центральные модели
        self.game = Game()
        self.active_theme_name = settings.theme if settings.theme in THEMES else "Classic"
        self.theme = THEMES[self.active_theme_name]

        # UI элементы, которые нужно хранить
        self.canvas = None  # основной Canvas для отрисовки поля
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

    # ---------------- UI - STYLE ----------------
    def _setup_style(self):
        """Настройка стилей (ttk) и внешнего вида."""
        # Общие цвета фона
        try:
            self.root.configure(bg=self.theme["bg"])
        except Exception:
            pass

        # ttk style (можно расширить)
        style = ttk.Style(self.root)
        # use default theme if platform-specific fails
        try:
            style.theme_use("clam")
        except Exception:
            try:
                style.theme_use(style.theme_names()[0])
            except Exception:
                pass

        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=3)

    # ---------------- UI - MENU ----------------
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
                                      variable=tk.IntVar(value=1 if settings.show_highlight else 0),
                                      command=self._safe(self.toggle_highlight))
        settings_menu.add_checkbutton(label="Автосохранение счета", onvalue=1, offvalue=0,
                                      variable=tk.IntVar(value=1 if settings.autosave_score else 0),
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

    # ---------------- UI - TOOLBAR ----------------
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

        # Spacer
        spacer = ttk.Label(toolbar, text="")
        spacer.pack(side=tk.LEFT, expand=True)

        score_label = ttk.Label(toolbar, textvariable=self.score_var)
        score_label.pack(side=tk.RIGHT, padx=6)

    # ---------------- UI - BOARD AREA ----------------
    def _create_board_area(self):
        # Frame which will contain canvas; it expands with window
        self.board_frame = ttk.Frame(self.root)
        self.board_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # Canvas used to draw board grid lines and background
        self.canvas = tk.Canvas(self.board_frame, bg=self.theme["board_bg"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        # Bind resize event to redraw grid
        self.canvas.bind("<Configure>", lambda ev: self._safe(self._on_canvas_resize)(ev.width, ev.height))

        # We overlay buttons (or draw X/O directly on canvas)
        # We'll draw cells and keep track of their bounding boxes.
        self.cell_bbox: Dict[Tuple[int, int], Tuple[int, int, int, int]] = {}

        # Bind mouse clicks
        self.canvas.bind("<Button-1>", lambda ev: self._safe(self._on_canvas_click)(ev.x, ev.y))

        # Initially draw
        self._on_canvas_resize(self.canvas.winfo_width() or settings.width,
                               self.canvas.winfo_height() or settings.height)

    # ---------------- UI - STATUS AREA ----------------
    def _create_status_area(self):
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_label = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        info_label = ttk.Label(status_frame, textvariable=self.info_var, relief=tk.SUNKEN, anchor="e")
        info_label.pack(side=tk.RIGHT)

        self._update_score_var()

    # ----------------- UI UTILITIES -----------------
    def _update_score_var(self):
        self.score_var.set(f"X: {score.x_wins}   O: {score.o_wins}   Ничьи: {score.draws}")

    def _update_status_var(self):
        if self.game.winner is None:
            self.status_var.set(f"Ход: {self.game.current}  (горячие клавиши 1-9)")
        elif self.game.winner == "Draw":
            self.status_var.set("Ничья!")
        else:
            self.status_var.set(f"Победитель: {self.game.winner}")

    def _update_ui_from_state(self):
        # Обновляем статус и перерисовываем поле
        self._update_status_var()
        self._redraw_board()

    # ----------------- CANVAS DRAWING -----------------
    def _on_canvas_resize(self, width: int, height: int):
        """Обработка изменения размера canvas: пересчитать ячейки и перерисовать сетку."""
        try:
            self.canvas.delete("all")
            pad = 20  # padding around board
            # square area for board
            size = min(max(40, width - 2 * pad), max(40, height - 2 * pad))
            # center
            x0 = (width - size) // 2
            y0 = (height - size) // 2
            x1 = x0 + size
            y1 = y0 + size
            self.board_bbox = (x0, y0, x1, y1)

            # Draw background rectangle
            self.canvas.create_rectangle(x0 - 6, y0 - 6, x1 + 6, y1 + 6,
                                         fill=self.theme["board_bg"], outline=self.theme["line"], width=2)

            # Draw 3x3 grid lines
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
                    # Draw inner cell background
                    self.canvas.create_rectangle(cx0, cy0, cx1, cy1, fill=self.theme["board_bg"],
                                                 outline=self.theme["line"])
            # After setting up cell bboxes, draw X/O
            self._redraw_board()
        except Exception as e:
            log_exception(e)
            raise

    def _redraw_board(self):
        """Перерисовать компонент доски (X и O)."""
        try:
            # Clear all marks (but keep grid)
            # To avoid erasing the grid, we redraw grid each time from stored bboxes.
            # Simpler: delete marks by tag
            self.canvas.delete("mark")
            # Draw each mark according to board state
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
            # Highlight winning line if any
            self._update_highlight()
        except Exception as e:
            log_exception(e)
            raise

    def _draw_x(self, bbox: Tuple[int, int, int, int], tag: str = ""):
        x0, y0, x1, y1 = bbox
        pad = int(min(x1 - x0, y1 - y0) * 0.18)
        coords = (x0 + pad, y0 + pad, x1 - pad, y1 - pad)
        # two diagonal lines
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
        """Подсветка выигрышной линии (если есть и включена в настройки)."""
        # remove old highlight
        self.canvas.delete("highlight")
        if not settings.show_highlight:
            return
        line = self.game.get_winning_line()
        if not line:
            self.last_highlight = None
            return
        # Draw semi-transparent overlay on winning cells
        for (r, c) in line:
            bbox = self.cell_bbox.get((r, c))
            if not bbox:
                continue
            x0, y0, x1, y1 = bbox
            # slightly inset rect
            pad = int(min(x1 - x0, y1 - y0) * 0.06)
            self.canvas.create_rectangle(x0 + pad, y0 + pad, x1 - pad, y1 - pad,
                                         fill=self.theme["highlight"], outline="", stipple="gray25",
                                         tag="highlight")
        self.last_highlight = line

    # ----------------- EVENT HANDLERS -----------------
    def _on_canvas_click(self, x: int, y: int):
        """Обработка клика мыши по canvas: найти клетку и сделать ход."""
        # find cell by bbox
        for (r, c), bbox in self.cell_bbox.items():
            x0, y0, x1, y1 = bbox
            if x0 <= x <= x1 and y0 <= y <= y1:
                self._safe(self._try_make_move)(r, c)
                break

    def _try_make_move(self, r: int, c: int):
        """Попытка сделать ход и обновление UI/счета при завершении."""
        try:
            moved = self.game.make_move(r, c)
            if not moved:
                self.info_var.set("Клетка занята или игра окончена.")
                return
            self._update_ui_from_state()
            if self.game.winner:
                # Update score
                if self.game.winner == "X":
                    score.x_wins += 1
                elif self.game.winner == "O":
                    score.o_wins += 1
                elif self.game.winner == "Draw":
                    score.draws += 1
                score.save()
                self._update_score_var()
                # Show dialog
                if self.game.winner == "Draw":
                    messagebox.showinfo("Итог", "Ничья!")
                else:
                    messagebox.showinfo("Итог", f"Победитель: {self.game.winner}")
                # start blink animation on winning cells if any
                if settings.show_highlight and self.game.get_winning_line():
                    self._start_blink()
        except Exception as e:
            log_exception(e)
            raise

    # ----------------- GAME CONTROL -----------------
    def new_game(self):
        """Начать новую игру (с тем же стартовым игроком X)."""
        self._stop_blink()
        self.game.reset(starting="X")
        self._update_ui_from_state()
        self.info_var.set("Новая игра начата.")

    def do_undo(self):
        """Отмена последнего хода."""
        ok = self.game.undo()
        if not ok:
            self.info_var.set("Нечего отменять.")
            return
        # Возможно, нужно скорректировать счет, если undo после завершения игры
        # Мы не меняем счет автоматически при undo — такое поведение можно доработать.
        self._update_ui_from_state()
        self.info_var.set("Отменен последний ход.")

    def reset_score(self):
        """Сбросить счет на нули."""
        if messagebox.askyesno("Сброс счета", "Вы уверены, что хотите сбросить счет?"):
            score.x_wins = score.o_wins = score.draws = 0
            score.save()
            self._update_score_var()
            self.info_var.set("Счет сброшен.")

    def save_score_as(self):
        """Сохранить счет в файл через диалог."""
        path = filedialog.asksaveasfilename(title="Сохранить счет как", defaultextension=".json",
                                            filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                from dataclasses import asdict
                json.dump(asdict(score), f, ensure_ascii=False, indent=2)
            self.info_var.set(f"Счет сохранён в {path}")
        except Exception as e:
            log_exception(e)
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def load_score_from(self):
        """Загрузить счет из файла через диалог."""
        path = filedialog.askopenfilename(title="Загрузить счет", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            score.x_wins = int(data.get("x_wins", 0))
            score.o_wins = int(data.get("o_wins", 0))
            score.draws = int(data.get("draws", 0))
            score.save()
            self._update_score_var()
            self.info_var.set(f"Счет загружен из {path}")
        except Exception as e:
            log_exception(e)
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

    # ----------------- THEME / SETTINGS -----------------
    def _make_theme_switcher(self, theme_name: str) -> Callable:
        def switch():
            self._safe(self.change_theme)(theme_name)
        return switch

    def change_theme(self, theme_name: str):
        """Поменять тему (skin)."""
        if theme_name not in THEMES:
            return
        self.active_theme_name = theme_name
        self.theme = THEMES[theme_name]
        settings.theme = theme_name
        settings.save()
        # reconfigure backgrounds and redraw
        try:
            self.root.configure(bg=self.theme["bg"])
        except Exception:
            pass
        # update canvas bg and redraw
        if self.canvas:
            try:
                self.canvas.configure(bg=self.theme["board_bg"])
            except Exception:
                pass
            self._redraw_board()
        self.info_var.set(f"Тема установлена: {theme_name}")

    def change_window_size(self):
        """Диалог изменения размера окна (ширина/высота)."""
        try:
            w = simpledialog.askinteger("Размер окна", "Ширина (px):", initialvalue=self.root.winfo_width(), minvalue=MIN_WINDOW_SIZE)
            if w is None:
                return
            h = simpledialog.askinteger("Размер окна", "Высота (px):", initialvalue=self.root.winfo_height(), minvalue=MIN_WINDOW_SIZE)
            if h is None:
                return
            self.root.geometry(f"{w}x{h}")
            settings.width = w
            settings.height = h
            settings.save()
            self.info_var.set(f"Размер окна установлен: {w}x{h}")
        except Exception as e:
            log_exception(e)
            messagebox.showerror("Ошибка", f"Неверный ввод: {e}")

    def toggle_highlight(self):
        settings.show_highlight = not settings.show_highlight
        settings.save()
        self._redraw_board()

    def toggle_autosave(self):
        settings.autosave_score = not settings.autosave_score
        settings.save()

    # ----------------- ANIMATION (blink winning line) -----------------
    def _start_blink(self):
        """Запустить мигание подсветки выигрышной линии."""
        if self._blink_job:
            return
        self._blink_state = False
        self._blink_cycle()

    def _blink_cycle(self):
        self._blink_state = not self._blink_state
        if not settings.show_highlight:
            self._stop_blink()
            return
        if not self.game.get_winning_line():
            self._stop_blink()
            return
        if self._blink_state:
            # hide highlight -> delete highlight tag
            self.canvas.itemconfigure("highlight", state="hidden")
        else:
            self.canvas.itemconfigure("highlight", state="normal")
        # schedule next
        self._blink_job = self.root.after(500, self._blink_cycle)

    def _stop_blink(self):
        if self._blink_job:
            try:
                self.root.after_cancel(self._blink_job)
            except Exception:
                pass
            self._blink_job = None
            # ensure highlight is visible if appropriate
            self.canvas.itemconfigure("highlight", state="normal")
            self._blink_state = False

    # ----------------- SHORTCUTS -----------------
    def _bind_shortcuts(self):
        # New game Ctrl+N
        self.root.bind_all("<Control-n>", lambda ev: self._safe(self.new_game)())
        # Undo Ctrl+Z
        self.root.bind_all("<Control-z>", lambda ev: self._safe(self.do_undo)())
        # Number keys 1..9 for cells
        for k, (r, c) in KEY_TO_CELL.items():
            self.root.bind_all(k, lambda ev, rr=r, cc=c: self._safe(self._try_make_move)(rr, cc))

    # ----------------- DIALOGS / HELP -----------------
    def show_about(self):
        messagebox.showinfo("О программе",
                            f"{APP_NAME}\n\nПростой клиент для игры Крестики-нолики для двух игроков на одном компьютере.\n"
                            "Реализовано на Python/Tkinter.\n"
                            "Вариант A — улучшенный интерфейс для лабораторной работы.")

    def show_prototype_info(self):
        # Показываем краткую информацию о прототипе интерфейса (можно вставить ссылку/изображение)
        messagebox.showinfo("Прототип интерфейса",
                            "Интерфейс соответствует прототипу: меню, поле 3x3 в центре, статусная строка внизу, "
                            "диалог изменения размера окна и окно 'О программе'.\n\n"
                            "Для отчёта можете приложить скриншот этого окна и файл прототипа draw.io/figma.")

    # ----------------- EXCEPTIONS / SAFE CALL -----------------
    def _handle_callback_exception(self, exc, val, tb):
        """Обработка исключений, возникших в callback'ах tkinter (report_callback_exception)."""
        try:
            tb_str = "".join(traceback.format_exception(exc, val, tb))
            from config import LOG_FILE
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Uncaught exception in TK callback:\n{tb_str}\n")
        except Exception:
            pass
        # Показываем пользователю
        try:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{val}")
        except Exception:
            # если и это упало, печатаем в stderr
            print("Fatal UI exception:", val, file=sys.stderr)

    def _safe(self, func: Callable) -> Callable:
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
                    print("Error showing messagebox:", e, file=sys.stderr)
        return wrapper

    # ----------------- APP LIFECYCLE -----------------
    def on_close(self):
        """Выход из приложения: сохраняем размеры и настройки."""
        try:
            geom = self.root.geometry().split("+")[0]  # e.g. "800x600"
            w, h = geom.split("x")
            settings.width = int(w)
            settings.height = int(h)
        except Exception:
            # игнорируем, если что-то пошло не так
            pass
        settings.save()
        # autosave score already implemented in score.save()
        self.root.quit()
        try:
            self.root.destroy()
        except Exception:
            pass

    # ----------------- RUN -----------------
    def run(self):
        # Run the main loop; this is entry point after creating the GUI instance.
        try:
            self.root.mainloop()
        except Exception as e:
            log_exception(e)
            # If mainloop throws, show error and exit
            try:
                messagebox.showerror("Критическая ошибка", f"Приложение прервано: {e}")
            except Exception:
                pass