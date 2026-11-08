"""Summen-Hüte: q Farben, n Spieler, alle tippen gleichzeitig, das Team gewinnt, wenn mindestens ein Tipp stimmt (Kern, nur numpy/Standardbibliothek).

Strategie „Summe“: Spieler i bekommt vorab die Zahl r_i = i mod q (0-basiert). Er sieht die Hüte der anderen, bildet deren Summe s und tippt auf die Farbe (r_i − s) mod q.
Dann ist sein Tipp genau dann richtig, wenn die Summe ALLER Hüte gleich r_i ist."""

from __future__ import annotations

import numpy as np


def residue_of(player: int, q: int) -> int:
    """Die vorab verabredete Zielsumme von Spieler `player` (0-basiert)."""
    return player % q


def guess(player: int, others_sum: int, q: int) -> int:
    """Tipp von Spieler `player`, der die Hüte der anderen mit der Summe `others_sum` sieht."""
    return (residue_of(player, q) - others_sum) % q


def all_hats(n: int, q: int) -> np.ndarray:
    """Alle q^n Hutverteilungen als Matrix (q^n, n)."""
    return np.indices((q,) * n, dtype=np.int8).reshape(n, -1).T


def guesses_batch(hats: np.ndarray, q: int) -> np.ndarray:
    """Tipps aller Spieler für viele Verteilungen: (S, n) → (S, n). Spieler i benutzt nur die Summe der anderen Spalten."""
    s, n = hats.shape
    h = hats.astype(np.int64)
    total = h.sum(axis=1)
    out = np.zeros((s, n), dtype=np.int64)
    for i in range(n):
        out[:, i] = (residue_of(i, q) - (total - h[:, i])) % q
    return out


def right_counts(hats: np.ndarray, tips: np.ndarray) -> np.ndarray:
    """Zahl richtiger Tipps je Verteilung."""
    return (hats == tips).sum(axis=1)


def analyse_sums(n: int, q: int) -> dict:
    """Vollständige Aufzählung aller q^n Verteilungen: Häufigkeit jeder Trefferzahl, Gewinnzahl (mindestens ein Treffer)."""
    hats = all_hats(n, q)
    counts = np.bincount(right_counts(hats, guesses_batch(hats, q)), minlength=n + 1)
    total = q ** n
    return {"counts": counts, "total": total, "wins": int(total - counts[0]), "win_share": float((total - counts[0]) / total)}


def chance_win_share(n: int, q: int) -> float:
    """Gewinnanteil, wenn jeder Spieler unabhängig gleichverteilt tippt: 1 − (1 − 1/q)^n."""
    return 1.0 - (1.0 - 1.0 / q) ** n


def chance_distribution(n: int, q: int) -> np.ndarray:
    """Wahrscheinlichkeit jeder Trefferzahl 0 … n beim Raten ohne Plan."""
    from math import comb

    p = 1.0 / q
    return np.array([comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)])


def win_bound(n: int, q: int) -> float:
    """Obergrenze für den Gewinnanteil jeder Strategie: min(1, n / q) (Erwartungswert der Trefferzahl ist n / q)."""
    return min(1.0, n / q)
