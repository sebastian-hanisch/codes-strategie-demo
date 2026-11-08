"""Hüte gleichzeitig, raten oder passen (Kern, nur numpy/Standardbibliothek).

Spiel: n Spieler, jeder trägt einen Hut der Farbe 0 oder 1 (gleichverteilt, unabhängig), sieht die Hüte der anderen, nicht den eigenen. Alle sagen gleichzeitig
„0“, „1“ oder „passe“. Das Team gewinnt, wenn mindestens einer rät und alle, die raten, richtig liegen.

Eine Hutverteilung ist eine Zahl r in 0 … 2^n − 1; Spieler i (0-basiert) trägt das Bit i von r. Aktionen: 0 oder 1 (raten), PASS = 2.
Jede Regel ist eine eigene Funktion mit expliziten Ein- und Ausgaben (DEMO-PLAYBOOK §1b); `losing_set_strategy` ist die Einheit, die aus einer Menge D von
„Verlustverteilungen“ eine Strategie macht, `syndrome_zero_set` und die vorgerechneten Überdeckungscodes liefern solche Mengen D."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import cod_constants as C

PASS = 2
DATA_FILE = Path(__file__).resolve().parent / "data" / "huete_optimum.json"


def all_configs(n: int) -> np.ndarray:
    """Alle 2^n Hutverteilungen als Matrix (2^n, n) mit Werten 0/1; Zeile r hat in Spalte i das Bit i von r."""
    r = np.arange(1 << n, dtype=np.int64)
    return ((r[:, None] >> np.arange(n)) & 1).astype(np.uint8)


def config_index(bits: np.ndarray) -> np.ndarray:
    """Umkehrung von `all_configs`: Zeilen aus 0/1 zu ihrer Nummer r."""
    return (bits.astype(np.int64) << np.arange(bits.shape[1])).sum(axis=1)


def active_players(n: int) -> int:
    """Größte Zahl m = 2^r − 1 ≤ n (mindestens 1): so viele Spieler können den Hamming-Code nutzen, die übrigen passen immer."""
    m = 1
    while 2 * m + 1 <= n:
        m = 2 * m + 1
    return m


def syndrome(configs: np.ndarray, m: int) -> np.ndarray:
    """XOR der Positionen 1 … m, an denen eine 1 steht (Position = Spielernummer + 1). Null genau für die Codewörter des Hamming-Codes der Länge m."""
    s = np.zeros(configs.shape[0], dtype=np.int64)
    for p in range(1, m + 1):
        s ^= np.where(configs[:, p - 1] == 1, p, 0)
    return s


def syndrome_zero_set(n: int) -> np.ndarray:
    """Menge D der Verlustverteilungen der Code-Strategie als Wahrheitsvektor über alle 2^n Nummern: die Verteilungen, deren Syndrom (der ersten m Spieler) null ist."""
    return syndrome(all_configs(n), active_players(n)) == 0


def losing_set_strategy(in_d: np.ndarray, n: int) -> np.ndarray:
    """Aktionen (2^n, n) der Strategie zur Menge D (Wahrheitsvektor über die Nummern).

    Spieler i betrachtet die beiden Verteilungen, die zu dem passen, was er sieht (eigener Hut 0 oder 1). Liegt genau eine davon in D, rät er die Farbe der anderen
    (damit er auf der Verteilung außerhalb von D richtig liegt); liegen beide oder keine in D, passt er. Die Regel liest nur die Hüte der anderen."""
    r = np.arange(1 << n, dtype=np.int64)
    actions = np.full((1 << n, n), PASS, dtype=np.uint8)
    for i in range(n):
        c0 = r & ~(1 << i)          # Verteilung mit Hut 0 bei Spieler i und sonst wie sichtbar
        c1 = r | (1 << i)
        d0, d1 = in_d[c0], in_d[c1]
        actions[:, i] = np.where(d0 & ~d1, 1, np.where(d1 & ~d0, 0, PASS))
    return actions


def fixed_strategy(n: int, guessers: tuple[int, ...], color: int = 0) -> np.ndarray:
    """Die Spieler in `guessers` sagen immer `color`, alle anderen passen (Vergleichsstrategien ohne Code)."""
    actions = np.full((1 << n, n), PASS, dtype=np.uint8)
    for i in guessers:
        actions[:, i] = color
    return actions


def outcomes(actions: np.ndarray, configs: np.ndarray) -> dict:
    """Ergebnis je Verteilung: gewonnen, Zahl der Rater, Zahl falscher Tipps."""
    guess = actions != PASS
    wrong = guess & (actions != configs)
    n_guess = guess.sum(axis=1)
    n_wrong = wrong.sum(axis=1)
    return {"win": (n_guess >= 1) & (n_wrong == 0), "guessers": n_guess, "wrong": n_wrong}


def count_bound(n: int) -> int:
    """Obergrenze für die Zahl gewonnener Verteilungen jeder Strategie: ⌊n · 2^n / (n + 1)⌋ (Zählargument, siehe README)."""
    return (n * (1 << n)) // (n + 1)


def wins_of_losing_set(in_d: np.ndarray, n: int) -> int:
    """Gewinnzahl der Strategie zu D, gezählt über die Aktionen (nicht über die Formel 2^n − |D|)."""
    return int(outcomes(losing_set_strategy(in_d, n), all_configs(n))["win"].sum())


def load_optimum() -> dict[int, np.ndarray]:
    """Vorgerechnete kleinste dominierende Mengen D des Würfelgraphen Q_n (Überdeckungscode vom Radius 1), n = 2 … 8, als Wahrheitsvektoren."""
    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))["codes"]
    result = {}
    for key, entry in raw.items():
        n = int(key)
        mask = np.zeros(1 << n, dtype=bool)
        mask[entry["losing"]] = True
        result[n] = mask
    return result


def strategy_actions(n: int, strategy: str) -> np.ndarray:
    """Aktionen (2^n, n) für den Strategie-Namen der Oberfläche (`cod_constants.HAT_STRATEGIES`)."""
    if strategy == C.HAT_CODE:
        return losing_set_strategy(syndrome_zero_set(n), n)
    if strategy == C.HAT_BEST:
        return losing_set_strategy(load_optimum()[n], n)
    if strategy == C.HAT_ONE:
        return fixed_strategy(n, (0,))
    if strategy == C.HAT_ALL:
        return fixed_strategy(n, tuple(range(n)))
    raise ValueError(f"unbekannte Strategie {strategy!r}")


def enumerate_all_strategies_n3() -> dict:
    """Alle 3^12 Strategien für drei Spieler (je Sicht von zwei Hüten eine der Aktionen 0, 1, PASS) und ihre Gewinnzahlen.

    Rückgabe: {"wins": Gewinnzahl je Strategie (int8-Vektor), "total": Zahl der Strategien}. Spieler i sieht die zwei anderen in der Reihenfolge aufsteigender Spielernummer;
    die vier Sichten sind die Zahlen 0 … 3 (Bit 0 = der erste sichtbare Hut)."""
    n = 3
    total = 3 ** 12
    idx = np.arange(total, dtype=np.int64)
    digits = np.stack([(idx // 3 ** k) % 3 for k in range(12)], axis=1).astype(np.uint8)   # (total, 12): Zeile = Strategie, Spalte 4·i + Sicht
    wins = np.zeros(total, dtype=np.int16)
    for r in range(8):
        bits = [(r >> i) & 1 for i in range(n)]
        ok = np.ones(total, dtype=bool)
        any_guess = np.zeros(total, dtype=bool)
        for i in range(n):
            others = [bits[j] for j in range(n) if j != i]
            view = others[0] + 2 * others[1]
            a = digits[:, 4 * i + view]
            guess = a != PASS
            any_guess |= guess
            ok &= ~guess | (a == bits[i])
        wins += (ok & any_guess)
    return {"wins": wins, "total": total}
