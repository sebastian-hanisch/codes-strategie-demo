"""Kennzahlen, Szenen und Verdikte der vier Kulissen. Die Verdikte sind reine Funktionen (Art, Text); die App ruft st.<Art>(Text)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import cod_board as B
import cod_constants as C
import cod_hats as H
import cod_line as L
import cod_sums as S


@dataclass(frozen=True)
class Settings:
    n_hut: int = C.DEFAULT_N_HUT
    hat_strategy: str = C.DEFAULT_HAT_STRATEGY
    n_reihe: int = C.DEFAULT_N_REIHE
    q_reihe: int = C.DEFAULT_Q_REIHE
    q_summe: int = C.DEFAULT_Q_SUMME
    n_summe: int = C.DEFAULT_N_SUMME
    m_brett: int = C.DEFAULT_M_BRETT
    seed: int = C.DEFAULT_SEED


# --- Formatierung -----------------------------------------------------------------------------------------------------------------------------
def de(x: float, nd: int = 1) -> str:
    """Zahl mit Dezimalkomma und festen Nachkommastellen."""
    return f"{x:.{nd}f}".replace(".", ",")


def pct(share: float, nd: int = 1) -> str:
    """Anteil 0 … 1 als Prozentangabe mit Dezimalkomma."""
    return f"{de(100 * share, nd)} %"


def thousands(n: int) -> str:
    """Ganze Zahl mit Leerzeichen als Tausendertrenner."""
    return f"{n:,}".replace(",", " ")


# --- Hüte gleichzeitig ------------------------------------------------------------------------------------------------------------------------
OUTCOME_WIN, OUTCOME_WRONG, OUTCOME_SILENT = 0, 1, 2     # Kategorien je Hutverteilung


def hat_outcome_classes(actions: np.ndarray, configs: np.ndarray) -> np.ndarray:
    """0 = gewonnen, 1 = verloren, weil mindestens ein Tipp falsch war, 2 = verloren, weil niemand riet."""
    o = H.outcomes(actions, configs)
    cls = np.full(len(configs), OUTCOME_SILENT, dtype=np.int8)
    cls[o["guessers"] >= 1] = OUTCOME_WRONG
    cls[o["win"]] = OUTCOME_WIN
    return cls


def action_text(action: int) -> str:
    return "passt" if action == H.PASS else f"rät {action}"


@dataclass(frozen=True)
class HatAnalysis:
    n: int
    strategy: str
    wins: int
    total: int
    bound_wins: int
    optimum_wins: int
    code_wins: int
    classes: np.ndarray
    scene: tuple          # Zeilen (Spieler, sieht, Aktion, eigener Hut, Ergebnis) der gezogenen Verteilung
    scene_win: bool
    scene_index: int

    @property
    def share(self) -> float:
        return self.wins / self.total


def hat_scene(actions: np.ndarray, configs: np.ndarray, index: int) -> tuple:
    row, act = configs[index], actions[index]
    n = len(row)
    lines = []
    for i in range(n):
        sees = "".join(str(int(row[j])) for j in range(n) if j != i)
        mine = int(row[i])
        if act[i] == H.PASS:
            result = "–"
        else:
            result = "richtig" if act[i] == mine else "falsch"
        lines.append((i + 1, sees, action_text(int(act[i])), mine, result))
    return tuple(lines)


def analyse_hats(n: int, strategy: str, seed: int) -> HatAnalysis:
    configs = H.all_configs(n)
    actions = H.strategy_actions(n, strategy)
    o = H.outcomes(actions, configs)
    optimum = H.wins_of_losing_set(H.load_optimum()[n], n)
    code = H.wins_of_losing_set(H.syndrome_zero_set(n), n)
    index = int(np.random.default_rng([seed, 1]).integers(0, 1 << n))
    return HatAnalysis(n, strategy, int(o["win"].sum()), 1 << n, H.count_bound(n), optimum, code, hat_outcome_classes(actions, configs),
                       hat_scene(actions, configs, index), bool(o["win"][index]), index)


def hat_table(max_n: int = C.HAT_OPTIMUM_MAX_N) -> list[dict]:
    """Tabelle n = 2 … max_n: Zählschranke, Code-Strategie, beste Strategie (Gewinnzahlen)."""
    opt = H.load_optimum()
    rows = []
    for n in range(2, max_n + 1):
        rows.append({"n": n, "total": 1 << n, "bound": H.count_bound(n), "code": H.wins_of_losing_set(H.syndrome_zero_set(n), n),
                     "best": H.wins_of_losing_set(opt[n], n), "players_used": H.active_players(n)})
    return rows


def verdict_hats(a: HatAnalysis) -> tuple[str, str]:
    """Verdikt der Kernfrage für Hüte gleichzeitig. Ein Gewinn über dem bewiesenen Optimum wäre ein Fehler und wird als solcher gemeldet."""
    t = a.total
    own = f"Die Strategie gewinnt in **{a.wins} von {t}** Hutverteilungen ({pct(a.share)})"
    if a.wins > a.optimum_wins:
        return "error", f"{own}, mehr als das Optimum von {a.optimum_wins} von {t}: das darf nicht sein, die Rechnung ist fehlerhaft."
    ceiling = f"die beste Strategie für {a.n} Spieler gewinnt {a.optimum_wins} von {t} ({pct(a.optimum_wins / t)}), keine kann mehr als {a.bound_wins} von {t} erreichen"
    if a.wins == a.optimum_wins:
        return "success", f"{own}: so viel wie die beste mögliche; {ceiling}."
    if a.wins * 2 < t:
        return "warning", f"{own}, das ist weniger als ein einzelner Spieler, der allein rät und die anderen passen lässt (die Hälfte); {ceiling}."
    return "info", f"{own}; {ceiling}."


# --- Hüte in der Reihe ------------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class LineAnalysis:
    n: int
    q: int
    exhaustive: bool
    cases: int
    counts: np.ndarray
    min_saved: int
    mean_saved: float
    chance_mean: float
    hats: tuple
    answers: tuple


def analyse_line(n: int, q: int, seed: int) -> LineAnalysis:
    stats = L.analyse_line(n, q, C.ENUM_LIMIT, C.SAMPLES, np.random.default_rng([seed, 2]))
    hats = tuple(int(x) for x in np.random.default_rng([seed, 3]).integers(0, q, size=n))
    return LineAnalysis(n, q, stats["exhaustive"], stats["cases"], stats["counts"], stats["min"], stats["mean"], n / q, hats, L.play_line(hats, q))


def line_scope_text(cases: int, exhaustive: bool, n: int, q: int) -> str:
    return f"alle {thousands(cases)} Verteilungen ({q}^{n})" if exhaustive else f"{thousands(cases)} zufällige Verteilungen (von {q}^{n}; Stichprobe, keine Aufzählung)"


def verdict_line(a: LineAnalysis) -> tuple[str, str]:
    """Verdikt für die Reihe: Mindestzahl und Mittel der Treffer gegen n − 1 und das Raten ohne Plan."""
    scope = line_scope_text(a.cases, a.exhaustive, a.n, a.q)
    base = f"Über {scope} liegen mindestens **{a.min_saved} von {a.n}** Personen richtig und im Mittel {de(a.mean_saved, 2)}; ohne Plan wären es im Mittel {de(a.chance_mean, 2)}."
    if a.min_saved == a.n - 1:
        return "success", base + f" Bewiesen für jede Verteilung: alle außer der ersten Person (n − 1 = {a.n - 1}); die erste liegt in {pct(1 / a.q, 1)} der Fälle richtig."
    if a.min_saved < a.n - 1:
        return "error", base + f" Das ist weniger als n − 1 = {a.n - 1}: die Rechnung ist fehlerhaft."
    return "info", base


# --- Summen-Hüte ------------------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class SumAnalysis:
    n: int
    q: int
    counts: np.ndarray
    total: int
    wins: int
    win_share: float
    chance_share: float
    bound: float
    hats: tuple
    tips: tuple


def analyse_sums(n: int, q: int, seed: int) -> SumAnalysis:
    r = S.analyse_sums(n, q)
    hats = tuple(int(x) for x in np.random.default_rng([seed, 4]).integers(0, q, size=n))
    tips = tuple(int(x) for x in S.guesses_batch(np.array([hats]), q)[0])
    return SumAnalysis(n, q, r["counts"], r["total"], r["wins"], r["win_share"], S.chance_win_share(n, q), S.win_bound(n, q), hats, tips)


def verdict_sums(a: SumAnalysis) -> tuple[str, str]:
    """Verdikt für Summen-Hüte. Die Aussagen „genau ein“ und „mindestens ein“ Tipp werden an der Aufzählung geprüft, nicht aus n und q angenommen."""
    base = f"Über alle {thousands(a.total)} Verteilungen ({a.q}^{a.n}) liegt mindestens ein Tipp in **{thousands(a.wins)}** richtig ({pct(a.win_share)}); beim Raten ohne Plan wären es {pct(a.chance_share)}."
    if a.win_share > a.bound + 1e-12:
        return "error", base + " Das ist mehr als die Obergrenze min(1, n/q): die Rechnung ist fehlerhaft."
    if a.n == a.q:
        if int(a.counts[1]) != a.total:
            return "error", base + " Bei n = q müsste in jeder Verteilung genau ein Tipp stimmen: die Rechnung ist fehlerhaft."
        return "success", base + " Mit genau so vielen Spielern wie Farben liegt in jeder Verteilung **genau ein** Tipp richtig."
    if a.n > a.q:
        if int(a.counts[0]) != 0:
            return "error", base + " Bei n > q müsste in jeder Verteilung mindestens ein Tipp stimmen: die Rechnung ist fehlerhaft."
        return "success", base + f" Mit mehr Spielern als Farben ({a.n} > {a.q}) liegt in jeder Verteilung mindestens ein Tipp richtig."
    return "info", base + f" Mit weniger Spielern als Farben ({a.n} < {a.q}) ist mehr als n/q = {pct(a.bound)} für keine Strategie möglich; die Summe erreicht diese Grenze."


# --- Schachbrett ------------------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class BoardAnalysis:
    m: int
    n_fields: int
    board: np.ndarray
    key: int
    flip: int
    after: np.ndarray
    read: int
    exhaustive: bool
    cases: int
    failures: int


def analyse_board(m: int, seed: int) -> BoardAnalysis:
    n_fields = 1 << m
    rng = np.random.default_rng([seed, 5])
    board = B.random_board(n_fields, rng)
    key = int(rng.integers(0, n_fields))
    flip = B.flip_field(board, key)
    after = B.apply_flip(board, flip)
    if n_fields <= C.EXHAUSTIVE_MAX_N:
        check = B.check_all(n_fields)
        exhaustive = True
    else:
        check = B.check_sample(n_fields, C.BOARD_SAMPLES, np.random.default_rng([seed, 6]))
        exhaustive = False
    return BoardAnalysis(m, n_fields, board, key, flip, after, B.read_key(after), exhaustive, check["cases"], check["failures"])


def verdict_board(a: BoardAnalysis) -> tuple[str, str]:
    bits = f"{a.m} Bit" if a.m != 1 else "1 Bit"
    head = f"Ein umgedrehtes Feld überträgt log₂({a.n_fields}) = {bits}: B liest {a.read} ab, das Schlüsselfeld war {a.key}."
    if a.failures:
        return "error", head + f" In {thousands(a.failures)} von {thousands(a.cases)} geprüften Fällen stimmt das nicht: die Rechnung ist fehlerhaft."
    if a.exhaustive:
        return "success", head + f" Geprüft: **alle** {thousands(a.cases)} Fälle (2^{a.n_fields} Bretter mal {a.n_fields} Schlüsselfelder), kein Fehler."
    return "success", (head + f" Geprüft: {thousands(a.cases)} zufällige Fälle ohne Fehler. **Nicht aufgezählt** sind alle 2^{a.n_fields} · {a.n_fields} Fälle; "
                       "dass es immer gilt, folgt aus dem XOR-Argument (siehe Mathematische Formulierung).")


def board_class_text(n_fields: int) -> str:
    """Eine Zeile zum Zählargument für die Feldzahl N (Eine perfekte Strategie braucht, dass N die Zahl 2^N teilt)."""
    num, den = B.class_size(n_fields)
    if num % den == 0:
        return f"2^{n_fields} / {n_fields} = {thousands(num // den)}: ganzzahlig."
    return f"2^{n_fields} / {n_fields} ist nicht ganzzahlig: keine perfekte Strategie."
