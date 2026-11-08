"""Erzeugt data/huete_optimum.json: je n = 2 … 8 eine kleinste dominierende Menge D des Würfelgraphen Q_n (Überdeckungscode vom Radius 1).

Das Team verliert im Hut-Spiel (raten oder passen, zwei Farben) genau auf D; jede Hutverteilung muss in D liegen oder einen Nachbarn (ein Hut anders) in D haben.
Gelöst wird das Überdeckungsproblem  min Σ x_v  mit  x_v + Σ_{u ~ v} x_u ≥ 1  als ganzzahliges Modell mit scipy.optimize.milp (HiGHS).
Aufruf (Test-venv): C:/Users/sebas/Claude Code Projects/_venvs/test/Scripts/python.exe tools/make_optimum.py   (n = 8 dauert etwa 8 Sekunden).
Eine andere Lösung gleicher Größe wäre ebenso gültig; tests/test_hats.py prüft Gültigkeit und Größe, nicht die Gleichheit der Mengen."""

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

OUT = Path(__file__).resolve().parent.parent / "data" / "huete_optimum.json"
MAX_N = 8


def smallest_dominating_set(n: int, time_limit: float = 120.0) -> tuple[list[int], str, float]:
    size = 1 << n
    a = lil_matrix((size, size))
    for v in range(size):
        a[v, v] = 1
        for j in range(n):
            a[v, v ^ (1 << j)] = 1
    res = milp(c=np.ones(size), constraints=LinearConstraint(a.tocsr(), lb=np.ones(size)), integrality=np.ones(size), bounds=Bounds(0, 1),
               options={"time_limit": time_limit, "disp": False})
    if res.x is None or res.status != 0:
        raise RuntimeError(f"n = {n}: kein optimales Ergebnis ({res.message})")
    return [v for v in range(size) if res.x[v] > 0.5], str(res.message), float(res.mip_dual_bound)


def main() -> int:
    codes = {}
    for n in range(2, MAX_N + 1):
        losing, message, bound = smallest_dominating_set(n)
        codes[str(n)] = {"losing": losing, "size": len(losing), "wins": (1 << n) - len(losing), "solver": message, "dual_bound": round(bound, 6)}
        print(f"n = {n}: |D| = {len(losing)}, Gewinnzahl {(1 << n) - len(losing)} von {1 << n} ({message})")
    payload = {
        "beschreibung": "Kleinste dominierende Mengen D des Würfelgraphen Q_n (Verlustverteilungen der besten Hut-Strategie); erzeugt von tools/make_optimum.py mit scipy.optimize.milp (HiGHS).",
        "codes": codes,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
