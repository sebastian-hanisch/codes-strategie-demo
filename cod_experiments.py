"""Die drei Experimente der Demo (E1 alle Strategien für drei Hüte, E2 Sichtgraph, E3 Färbungen des Schachbretts) und ihre Verdikte (reine Funktionen)."""

from __future__ import annotations

import numpy as np

import cod_board as B
import cod_constants as C
import cod_evaluation as V
import cod_graph as G
import cod_hats as H


# --- E1: alle 3^12 Strategien für drei Hüte ---------------------------------------------------------------------------------------------------
def e1_all_strategies() -> dict:
    """Zählt für alle 531 441 Strategien die Gewinnzahl (von 8) und fasst sie als Häufigkeitstabelle zusammen."""
    r = H.enumerate_all_strategies_n3()
    wins = r["wins"]
    histogram = np.bincount(wins, minlength=9)
    return {"total": r["total"], "histogram": histogram, "best": int(wins.max()), "n_best": int((wins == wins.max()).sum()),
            "n_at_least_half": int((wins >= 4).sum())}


def verdict_e1(r: dict) -> tuple[str, str]:
    return "success", (f"Von {V.thousands(r['total'])} Strategien gewinnt keine in mehr als **{r['best']} von 8** Hutverteilungen ({V.pct(r['best'] / 8)}); "
                       f"{V.thousands(r['n_best'])} Strategien erreichen genau diesen Wert, {V.thousands(r['n_at_least_half'])} gewinnen mindestens die Hälfte (4 von 8).")


# --- E2: Sichtgraph ---------------------------------------------------------------------------------------------------------------------------
def has_triangle(nbrs: list[list[int]]) -> bool:
    """Gibt es drei Spieler, die einander alle sehen (und deshalb die Paritätsstrategie für drei Hüte spielen könnten)?"""
    n = len(nbrs)
    sets = [set(nb) for nb in nbrs]
    return any(b in sets[a] and c in sets[a] and c in sets[b] and a in sets[b] and a in sets[c] and b in sets[c]
               for a in range(n) for b in range(a + 1, n) for c in range(b + 1, n))


def e2_graph(kind: str, n: int) -> dict:
    """Beste Strategie für den Sichtgraphen (ganzzahliges Modell, feste Zeitgrenze) und Vergleich mit „Jeder sieht jeden“."""
    nbrs = G.make_graph(kind, n, C.GRAPH_KINDS)
    r = G.solve_best(nbrs, C.SOLVER_SECONDS)
    r.update({"kind": kind, "n": n, "triangle": has_triangle(nbrs), "edges": sum(len(x) for x in nbrs) // 2, "n_strategies": G.strategy_count(nbrs)})
    return r


def verdict_e2(r: dict) -> tuple[str, str]:
    total, wins = r["total"], r["wins"]
    head = f"Sichtgraph „{r['kind']}“ mit {r['n']} Spielern: Die beste Strategie gewinnt **{wins} von {total}** ({V.pct(wins / total)})"
    if r["status"] == "OPTIMAL":
        head += " (vom Löser als optimal bewiesen)."
    else:
        head += f" (Zeitgrenze erreicht: gefunden {wins} von {total}, die Schranke des Lösers liegt bei {r['bound']}; **nicht** als optimal bewiesen)."
    if r["triangle"]:
        tail = " Der Graph enthält drei Spieler, die einander alle sehen: Sie spielen die Paritätsstrategie, alle anderen passen, das gibt mindestens 3/4."
    else:
        tail = f" Kein Dreieck im Graphen. Ein einzelner Spieler, der immer »0« sagt, gewinnt ohnehin {total // 2} von {total}."
    return ("info" if r["status"] == "OPTIMAL" else "warning"), head + tail


# --- E3: perfekte Strategien auf dem Brett ----------------------------------------------------------------------------------------------------
def e3_colorings() -> dict:
    """Zählt alle perfekten Färbungen für N = 2 und N = 3 durch Aufzählung (4 bzw. 6 561 Färbungen werden geprüft) und gibt die Teilbarkeit von 2^N durch N für N = 2 … 16 an."""
    counts = {n: B.count_perfect_colorings(n) for n in (2, 3)}
    divisibility = [{"n_fields": n, "quotient": (1 << n) / n, "integer": (1 << n) % n == 0} for n in range(2, 17)]
    return {"counts": counts, "divisibility": divisibility}


def verdict_e3(r: dict) -> tuple[str, str]:
    c = r["counts"]
    integer = [d["n_fields"] for d in r["divisibility"] if d["integer"]]
    return "info", (f"Aufgezählt: für N = 2 gibt es {c[2]} perfekte Strategien, für N = 3 gibt es **{c[3]}**. Das Zählargument (2^N / N muss ganz sein) lässt zwischen N = 2 und N = 16 genau "
                    f"{', '.join(str(n) for n in integer)} zu: die Zweierpotenzen. Dass die Zweierpotenzen auch gehen, zeigt die XOR-Strategie.")
