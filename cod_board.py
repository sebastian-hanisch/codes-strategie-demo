"""Schachbrett: ein umgedrehtes Feld überträgt log₂(N) Bit (Kern, nur numpy/Standardbibliothek).

Auf N Feldern (N = 2^m) liegt je eine Münze (0 = Zahl, 1 = Kopf). Gefangener A kennt das Schlüsselfeld k und muss genau eine Münze umdrehen; Gefangener B sieht nur das Brett und
muss k nennen. Verabredet wird die Zahl S(Brett) = XOR der Nummern aller Felder mit Kopf. A dreht das Feld S ⊕ k um, danach gilt S = k."""

from __future__ import annotations

import itertools

import numpy as np


def board_code(boards: np.ndarray) -> np.ndarray:
    """S(Brett) für viele Bretter auf einmal: (B, N) mit 0/1 → (B,). XOR der Nummern 0 … N − 1 der Felder mit Kopf."""
    boards = np.atleast_2d(boards)
    out = np.zeros(boards.shape[0], dtype=np.int64)
    for field in range(boards.shape[1]):
        out ^= np.where(boards[:, field] == 1, field, 0)
    return out


def flip_field(board: np.ndarray, key: int) -> int:
    """Das Feld, das A umdreht: S(Brett) ⊕ Schlüsselfeld."""
    return int(board_code(board)[0]) ^ int(key)


def apply_flip(board: np.ndarray, field: int) -> np.ndarray:
    """Eine Kopie des Bretts mit umgedrehtem Feld."""
    out = np.array(board, dtype=np.uint8, copy=True)
    out[field] ^= 1
    return out


def read_key(board: np.ndarray) -> int:
    """Was B abliest: der Schlüssel ist S(Brett nach dem Umdrehen)."""
    return int(board_code(board)[0])


def random_board(n_fields: int, rng: np.random.Generator) -> np.ndarray:
    """Ein gleichverteiltes Brett."""
    return rng.integers(0, 2, size=n_fields, dtype=np.uint8)


def all_boards(n_fields: int) -> np.ndarray:
    """Alle 2^N Bretter als Matrix (2^N, N); Zeile r hat in Spalte i das Bit i von r."""
    r = np.arange(1 << n_fields, dtype=np.int64)
    return ((r[:, None] >> np.arange(n_fields)) & 1).astype(np.uint8)


def check_all(n_fields: int) -> dict:
    """Prüft für jedes der 2^N Bretter und jedes der N Schlüsselfelder, dass B den Schlüssel abliest. Das Umdrehen wird tatsächlich ausgeführt und der Code neu berechnet."""
    if not is_power_of_two(n_fields):
        raise ValueError("Die Strategie braucht eine Zweierpotenz als Feldzahl")
    boards = all_boards(n_fields)
    code = board_code(boards)
    rows = np.arange(len(boards))
    failures = 0
    for key in range(n_fields):
        flipped = boards.copy()
        flipped[rows, code ^ key] ^= 1
        failures += int((board_code(flipped) != key).sum())
    return {"cases": len(boards) * n_fields, "failures": failures}


def check_sample(n_fields: int, count: int, rng: np.random.Generator) -> dict:
    """Wie `check_all`, aber an `count` Zufallsbrettern mit zufälligem Schlüsselfeld (Stichprobe, keine vollständige Prüfung)."""
    boards = rng.integers(0, 2, size=(count, n_fields), dtype=np.uint8)
    keys = rng.integers(0, n_fields, size=count)
    code = board_code(boards)
    flipped = boards.copy()
    flipped[np.arange(count), code ^ keys] ^= 1
    return {"cases": count, "failures": int((board_code(flipped) != keys).sum())}


def is_power_of_two(n_fields: int) -> bool:
    return n_fields >= 1 and n_fields & (n_fields - 1) == 0


def class_size(n_fields: int) -> tuple[int, int]:
    """Eine perfekte Strategie färbt die 2^N Bretter mit N Farben (Farbe = was B abliest) so, dass unter den N Nachbarn jedes Bretts jede Farbe genau einmal vorkommt.
    Jede Farbklasse hat dann 2^N / N Bretter. Rückgabe: (Zähler 2^N, Nenner N); ganzzahlig nur, wenn N ein Teiler von 2^N ist."""
    return 1 << n_fields, n_fields


def count_perfect_colorings(n_fields: int) -> int:
    """Zählt ALLE Färbungen der 2^N Bretter mit N Farben, bei denen die N Nachbarn jedes Bretts (je ein Feld umgedreht) alle N Farben tragen. Aufzählung aller N^(2^N) Färbungen,
    deshalb nur für N ≤ 3 gedacht (N = 3: 6 561 Färbungen)."""
    size = 1 << n_fields
    neighbours = [[v ^ (1 << j) for j in range(n_fields)] for v in range(size)]
    count = 0
    for colouring in itertools.product(range(n_fields), repeat=size):
        if all(len({colouring[u] for u in nb}) == n_fields for nb in neighbours):
            count += 1
    return count
