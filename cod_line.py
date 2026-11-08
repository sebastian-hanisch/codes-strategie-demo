"""Hüte in einer Reihe: die Summe wird angesagt (Kern, nur numpy/Standardbibliothek).

n Personen stehen hintereinander, jede trägt einen Hut einer von q Farben (0 … q − 1). Person 0 steht ganz hinten und sieht die Hüte der Personen 1 … n − 1 vor ihr,
Person k sieht die Hüte k + 1 … n − 1. Nacheinander (0, 1, …, n − 1) nennt jede laut eine Farbe als Tipp für den eigenen Hut; alle hören alle Tipps, erfahren aber nicht,
ob ein Tipp stimmte. Abgesprochen wird vorher.

Strategie „Summe ansagen“: Person 0 nennt die Summe (mod q) der Hüte vor ihr. Person k ≥ 1 kennt diese Summe, sieht die Hüte vor sich und hat die Tipps 1 … k − 1 gehört
(die, wenn sie stimmen, die Hüte 1 … k − 1 sind); sie nennt den Rest. Jede Person außer der ersten liegt damit immer richtig."""

from __future__ import annotations

import numpy as np


def first_answer(ahead: tuple[int, ...], q: int) -> int:
    """Tipp der Person ganz hinten: die Summe der Hüte vor ihr modulo q (die „Paritätsansage“ bei q = 2)."""
    return sum(ahead) % q


def later_answer(ahead: tuple[int, ...], spoken: tuple[int, ...], q: int) -> int:
    """Tipp der Person k ≥ 1. `ahead` = die Hüte, die sie vor sich sieht; `spoken` = alle bisher gehörten Tipps (Tipp 0 zuerst). Mehr weiß sie nicht."""
    return (spoken[0] - sum(ahead) - sum(spoken[1:])) % q


def play_line(hats: tuple[int, ...], q: int) -> tuple[int, ...]:
    """Spielt die Reihe Person für Person durch; jede Person bekommt nur ihre erlaubten Informationen (`ahead`, `spoken`)."""
    spoken: list[int] = []
    for k in range(len(hats)):
        ahead = tuple(hats[k + 1:])
        spoken.append(first_answer(ahead, q) if k == 0 else later_answer(ahead, tuple(spoken), q))
    return tuple(spoken)


def play_line_batch(hats: np.ndarray, q: int) -> np.ndarray:
    """Dieselbe Strategie für viele Hutverteilungen auf einmal: `hats` (S, n) → Tipps (S, n). Gleiches Ergebnis wie `play_line` je Zeile."""
    s, n = hats.shape
    h = hats.astype(np.int64)
    answers = np.zeros((s, n), dtype=np.int64)
    answers[:, 0] = h[:, 1:].sum(axis=1) % q
    for k in range(1, n):
        answers[:, k] = (answers[:, 0] - h[:, k + 1:].sum(axis=1) - answers[:, 1:k].sum(axis=1)) % q
    return answers


def all_hats(n: int, q: int) -> np.ndarray:
    """Alle q^n Hutverteilungen als Matrix (q^n, n)."""
    return np.indices((q,) * n, dtype=np.int8).reshape(n, -1).T


def sample_hats(n: int, q: int, count: int, rng: np.random.Generator) -> np.ndarray:
    """`count` unabhängig gleichverteilte Hutverteilungen."""
    return rng.integers(0, q, size=(count, n), dtype=np.int8)


def saved_counts(hats: np.ndarray, answers: np.ndarray) -> np.ndarray:
    """Zahl der richtigen Tipps je Verteilung."""
    return (hats == answers).sum(axis=1)


def count_distribution(saved: np.ndarray, n: int) -> np.ndarray:
    """Häufigkeit jeder Trefferzahl 0 … n."""
    return np.bincount(saved, minlength=n + 1)


def binomial_distribution(n: int, q: int) -> np.ndarray:
    """Wahrscheinlichkeit jeder Trefferzahl 0 … n, wenn jede Person unabhängig gleichverteilt tippt (Raten ohne Plan)."""
    from math import comb

    p = 1.0 / q
    return np.array([comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)])


def analyse_line(n: int, q: int, enum_limit: int, samples: int, rng: np.random.Generator) -> dict:
    """Wertet die Strategie „Summe ansagen“ aus: vollständig, wenn q^n ≤ enum_limit, sonst an `samples` Zufallsverteilungen."""
    exhaustive = q ** n <= enum_limit
    hats = all_hats(n, q) if exhaustive else sample_hats(n, q, samples, rng)
    saved = saved_counts(hats, play_line_batch(hats, q))
    return {"exhaustive": exhaustive, "cases": int(len(hats)), "counts": count_distribution(saved, n), "min": int(saved.min()), "mean": float(saved.mean())}
