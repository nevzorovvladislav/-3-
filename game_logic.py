#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Логика игры в крестики-нолики.
"""

from typing import List, Optional, Tuple


class Game:
    """
    Класс, инкапсулирующий логику игры.
    Поле 3x3 хранится в self.board: список списков со значениями '', 'X', 'O'.
    """

    def __init__(self):
        self.reset()

    def reset(self, starting: str = "X") -> None:
        """Сброс состояния игры."""
        self.board: List[List[str]] = [["" for _ in range(3)] for _ in range(3)]
        self.current: str = starting  # 'X' или 'O'
        self.winner: Optional[str] = None  # 'X', 'O', 'Draw' или None
        self.move_count: int = 0
        self.history: List[Tuple[int, int, str]] = []  # (row, col, player)

    def make_move(self, r: int, c: int) -> bool:
        """
        Сделать ход. Возвращает True, если ход успешен.
        Валидация: проверяем границы, пустоту клетки и отсутствие победителя.
        """
        if self.winner:
            return False
        if not (0 <= r < 3 and 0 <= c < 3):
            raise ValueError("row/col out of range")
        if self.board[r][c] != "":
            return False

        self.board[r][c] = self.current
        self.history.append((r, c, self.current))
        self.move_count += 1

        if self._check_winner_after_move(r, c):
            self.winner = self.current
        else:
            if self.move_count == 9:
                self.winner = "Draw"
            else:
                self.current = "O" if self.current == "X" else "X"
        return True

    def undo(self) -> bool:
        """Отмена последнего хода. Возвращает True, если отмена выполнена."""
        if not self.history or (self.winner is not None and self.winner != "Draw"):
            pass
        if not self.history:
            return False
        r, c, player = self.history.pop()
        self.board[r][c] = ""
        self.move_count -= 1
        self.current = player
        self.winner = None
        return True

    def _check_winner_after_move(self, last_r: int, last_c: int) -> bool:
        p = self.board[last_r][last_c]
        # Проверка строки
        if all(self.board[last_r][c] == p for c in range(3)):
            return True
        # Проверка столбца
        if all(self.board[r][last_c] == p for r in range(3)):
            return True
        # Главная диагональ
        if last_r == last_c and all(self.board[i][i] == p for i in range(3)):
            return True
        # Вторая диагональ
        if last_r + last_c == 2 and all(self.board[i][2 - i] == p for i in range(3)):
            return True
        return False

    def get_winning_line(self) -> Optional[List[Tuple[int, int]]]:
        """
        Вернуть координаты выигрышной линии, если она есть.
        Нужна для подсветки в UI.
        """
        b = self.board
        lines = []
        # строки
        for r in range(3):
            lines.append([(r, 0), (r, 1), (r, 2)])
        # столбцы
        for c in range(3):
            lines.append([(0, c), (1, c), (2, c)])
        # диагонали
        lines.append([(0, 0), (1, 1), (2, 2)])
        lines.append([(0, 2), (1, 1), (2, 0)])

        for line in lines:
            a, b1, c1 = line
            v0 = self.board[a[0]][a[1]]
            if v0 != "" and self.board[b1[0]][b1[1]] == v0 and self.board[c1[0]][c1[1]] == v0:
                return line
        return None

    def get_state_copy(self) -> List[List[str]]:
        """Возвращает копию доски (для безопасного чтения из UI)."""
        return [row[:] for row in self.board]