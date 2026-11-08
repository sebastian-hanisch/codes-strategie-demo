"""Hüte gleichzeitig mit Sichtgraph: Spieler i sieht nur die Hüte seiner Nachbarn (Kern; das ganzzahlige Modell importiert OR-Tools erst beim Aufruf).

Spiel wie in `cod_hats` (zwei Farben, raten oder passen, Gewinn: mindestens ein Rater und alle Rater richtig), aber Spieler i kennt nur die Hüte der Spieler in `nbrs[i]`.
Eine Strategie ist eine Tabelle je Spieler: Sicht (Bits der Nachbarhüte, Nachbar `nbrs[i][k]` an Bit k) → Aktion 0, 1 oder PASS."""

from __future__ import annotations

import itertools

import numpy as np

from cod_hats import PASS, all_configs


def complete_graph(n: int) -> list[list[int]]:
    """Jeder sieht jeden anderen."""
    return [[j for j in range(n) if j != i] for i in range(n)]


def ring_graph(n: int) -> list[list[int]]:
    """Jeder sieht seine beiden Nachbarn im Ring (n ≥ 3)."""
    return [sorted({(i - 1) % n, (i + 1) % n}) for i in range(n)]


def chain_graph(n: int) -> list[list[int]]:
    """Jeder sieht den Vorgänger und den Nachfolger in einer Kette (die Enden einen)."""
    return [[j for j in (i - 1, i + 1) if 0 <= j < n] for i in range(n)]


def star_graph(n: int) -> list[list[int]]:
    """Spieler 0 sieht alle anderen, jeder andere sieht nur Spieler 0."""
    return [list(range(1, n))] + [[0] for _ in range(1, n)]


def make_graph(kind: str, n: int, kinds: tuple[str, ...]) -> list[list[int]]:
    """Sichtgraph zum Namen der Oberfläche (`kinds` in der Reihenfolge vollständig, Ring, Kette, Stern)."""
    builders = dict(zip(kinds, (complete_graph, ring_graph, chain_graph, star_graph)))
    return builders[kind](n)


def view_index(configs: np.ndarray, neighbours: list[int]) -> np.ndarray:
    """Nummer der Sicht eines Spielers für jede Verteilung: Bit k = Hut des k-ten Nachbarn."""
    idx = np.zeros(configs.shape[0], dtype=np.int64)
    for k, j in enumerate(neighbours):
        idx |= configs[:, j].astype(np.int64) << k
    return idx


def actions_from_tables(tables: list[np.ndarray], nbrs: list[list[int]], configs: np.ndarray) -> np.ndarray:
    """Aktionen (S, n) aus Strategietabellen: Spieler i schlägt in `tables[i][Sicht]` nach."""
    out = np.zeros((configs.shape[0], len(nbrs)), dtype=np.uint8)
    for i, nb in enumerate(nbrs):
        out[:, i] = tables[i][view_index(configs, nb)]
    return out


def win_flags(actions: np.ndarray, configs: np.ndarray) -> np.ndarray:
    """Gewonnen: mindestens einer rät und kein Tipp ist falsch."""
    guess = actions != PASS
    return guess.any(axis=1) & ~(guess & (actions != configs)).any(axis=1)


def strategy_count(nbrs: list[list[int]]) -> int:
    """Zahl aller Strategien: Produkt über die Spieler von 3^(2^Grad)."""
    total = 1
    for nb in nbrs:
        total *= 3 ** (1 << len(nb))
    return total


def enumerate_best(nbrs: list[list[int]]) -> int:
    """Beste Gewinnzahl über ALLE Strategien (nur für wenige Strategien, z. B. höchstens eine Million)."""
    n = len(nbrs)
    configs = all_configs(n)
    total = strategy_count(nbrs)
    sizes = [3 ** (1 << len(nb)) for nb in nbrs]
    views = [view_index(configs, nb) for nb in nbrs]
    idx = np.arange(total, dtype=np.int64)
    wins = np.zeros(total, dtype=np.int16)
    # Strategie-Nummer in gemischter Basis: Spieler i hat sizes[i] Möglichkeiten; die Aktion bei Sicht v ist eine Ziffer zur Basis 3
    divisors = np.cumprod([1] + sizes[:-1])
    codes = [(idx // d) % s for d, s in zip(divisors, sizes)]
    for r in range(configs.shape[0]):
        ok = np.ones(total, dtype=bool)
        any_guess = np.zeros(total, dtype=bool)
        for i in range(n):
            action = (codes[i] // 3 ** int(views[i][r])) % 3
            guess = action != PASS
            any_guess |= guess
            ok &= ~guess | (action == configs[r, i])
        wins += ok & any_guess
    return int(wins.max())


def solve_best(nbrs: list[list[int]], time_limit: float) -> dict:
    """Beste Strategie als ganzzahliges Modell (CP-SAT, ein Arbeitsthread): je Spieler und Sicht genau eine Aktion, je Verteilung eine Gewinnvariable.

    Rückgabe: Status („OPTIMAL“ oder „FEASIBLE“ bei Zeitgrenze), Gewinnzahl, Schranke des Lösers, Rechenzeit."""
    from ortools.sat.python import cp_model

    n = len(nbrs)
    model = cp_model.CpModel()
    act = {}
    for i in range(n):
        for view in itertools.product((0, 1), repeat=len(nbrs[i])):
            xs = [model.NewBoolVar(f"a{i}_{view}_{a}") for a in range(3)]
            model.AddExactlyOne(xs)
            act[i, view] = xs
    wins = []
    for h in itertools.product((0, 1), repeat=n):
        w = model.NewBoolVar(f"w{h}")
        right, wrong = [], []
        for i in range(n):
            xs = act[i, tuple(h[j] for j in nbrs[i])]
            right.append(xs[h[i]])
            wrong.append(xs[1 - h[i]])
        model.Add(w <= sum(right))
        for x in wrong:
            model.Add(w + x <= 1)
        wins.append(w)
    model.Maximize(sum(wins))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = 1
    status = solver.Solve(model)
    return {"status": solver.StatusName(status), "wins": int(round(solver.ObjectiveValue())), "bound": int(solver.BestObjectiveBound() + 1e-6),
            "seconds": solver.WallTime(), "total": 1 << n}
