"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier."""

import numpy as np

import cod_evaluation as ev
import cod_experiments as xp


def _hat(wins, total=8, optimum=6, bound=6, n=3):
    return ev.HatAnalysis(n, "Code-Strategie (Summe der Positionen)", wins, total, bound, optimum, optimum, np.zeros(total, dtype=np.int8), (), True, 0)


def test_hats_verdict_best_is_success_and_names_all_numbers():
    kind, text = ev.verdict_hats(_hat(6))
    assert kind == "success"
    assert "**6 von 8**" in text and "(75,0 %)" in text and "so viel wie die beste mögliche" in text
    assert "gewinnt 6 von 8 (75,0 %)" in text and "mehr als 6 von 8" in text


def test_hats_verdict_below_best_is_info_and_at_most_half_is_not_warned_at_exactly_half():
    kind, text = ev.verdict_hats(_hat(5, optimum=6, bound=6))
    assert kind == "info" and "**5 von 8**" in text and "(62,5 %)" in text
    assert ev.verdict_hats(_hat(4))[0] == "info"                  # genau die Hälfte: noch nicht schlechter als ein einzelner Rater
    kind, text = ev.verdict_hats(_hat(3))
    assert kind == "warning" and "weniger als ein einzelner Spieler" in text


def test_hats_verdict_above_the_optimum_is_an_error():
    kind, text = ev.verdict_hats(_hat(7))
    assert kind == "error" and "das darf nicht sein" in text and "6 von 8" in text


def _line(min_saved, n=6, q=2, exhaustive=True, cases=64, mean=5.5):
    return ev.LineAnalysis(n, q, exhaustive, cases, np.zeros(n + 1, dtype=int), min_saved, mean, n / q, (), ())


def test_line_verdict_success_error_and_info():
    kind, text = ev.verdict_line(_line(5))
    assert kind == "success" and "alle 64 Verteilungen (2^6)" in text and "mindestens **5 von 6**" in text
    assert "im Mittel 5,50" in text and "ohne Plan wären es im Mittel 3,00" in text and "(n − 1 = 5)" in text and "50,0 %" in text
    kind, text = ev.verdict_line(_line(4))
    assert kind == "error" and "weniger als n − 1 = 5" in text
    assert ev.verdict_line(_line(6))[0] == "info"                  # mehr als n − 1 in der Stichprobe ist erlaubt (Treffer der ersten Person), aber keine Beweisaussage


def test_line_verdict_names_a_sample_when_not_exhaustive():
    kind, text = ev.verdict_line(_line(11, n=12, q=6, exhaustive=False, cases=5000, mean=11.17))
    assert kind == "success" and "5 000 zufällige Verteilungen (von 6^12; Stichprobe, keine Aufzählung)" in text and "(n − 1 = 11)" in text and "16,7 %" in text


def _sums(n, q, win_share, bound=None, counts=None):
    total = q ** n
    wins = int(round(win_share * total))
    if counts is None:                                   # Aufzählung passend zur Gewinnzahl: nur Treffer 0 (verloren) und 1 (gewonnen)
        counts = np.zeros(n + 1, dtype=int)
        counts[0], counts[1] = total - wins, wins
    return ev.SumAnalysis(n, q, np.array(counts), total, wins, win_share, 0.25, min(1.0, n / q) if bound is None else bound, (), ())


def test_sums_verdict_branches():
    kind, text = ev.verdict_sums(_sums(3, 3, 1.0))
    assert kind == "success" and "**genau ein** Tipp" in text and "27 Verteilungen (3^3)" in text and "in **27** richtig (100,0 %)" in text and "25,0 %" in text
    kind, text = ev.verdict_sums(_sums(4, 3, 1.0))
    assert kind == "success" and "mindestens ein Tipp richtig" in text and "(4 > 3)" in text
    kind, text = ev.verdict_sums(_sums(3, 5, 0.6))
    assert kind == "info" and "(3 < 5)" in text and "n/q = 60,0 %" in text
    kind, text = ev.verdict_sums(_sums(3, 5, 0.7))
    assert kind == "error" and "Obergrenze min(1, n/q)" in text


def test_sums_verdict_checks_the_counts_before_saying_exactly_one_or_at_least_one():
    """„genau ein“ (n = q) und „mindestens ein“ (n > q) kommen nur, wenn die Aufzählung sie trägt."""
    kind, text = ev.verdict_sums(_sums(3, 3, 1.0, counts=[0, 20, 7, 0]))                 # alle gewinnen, aber nicht immer genau einer
    assert kind == "error" and "Bei n = q müsste in jeder Verteilung genau ein Tipp stimmen" in text
    kind, text = ev.verdict_sums(_sums(4, 3, 26 / 27 * 1.0, bound=1.0, counts=[3, 78, 0, 0, 0]))   # in 3 von 81 Verteilungen stimmt kein Tipp
    assert kind == "error" and "Bei n > q müsste in jeder Verteilung mindestens ein Tipp stimmen" in text


def _board(m, failures=0, exhaustive=True, cases=None):
    n = 1 << m
    return ev.BoardAnalysis(m, n, np.zeros(n, dtype=np.uint8), 3 % n, 1, np.zeros(n, dtype=np.uint8), 3 % n, exhaustive, cases or n * 2 ** n, failures)


def test_board_verdict_branches():
    kind, text = ev.verdict_board(_board(3))
    assert kind == "success" and "log₂(8) = 3 Bit" in text and "**alle** 2 048 Fälle (2^8 Bretter mal 8 Schlüsselfelder)" in text
    kind, text = ev.verdict_board(_board(1))
    assert "log₂(2) = 1 Bit" in text
    kind, text = ev.verdict_board(_board(6, exhaustive=False, cases=20000))
    assert kind == "success" and "20 000 zufällige Fälle" in text and "**Nicht aufgezählt**" in text and "2^64 · 64" in text
    kind, text = ev.verdict_board(_board(3, failures=5))
    assert kind == "error" and "5 von 2 048" in text


def test_board_class_text():
    assert ev.board_class_text(8) == "2^8 / 8 = 32: ganzzahlig."
    assert ev.board_class_text(6) == "2^6 / 6 ist nicht ganzzahlig: keine perfekte Strategie."


def test_experiment_verdicts():
    kind, text = xp.verdict_e1({"total": 531441, "histogram": np.zeros(9), "best": 6, "n_best": 4, "n_at_least_half": 1000})
    assert kind == "success" and "531 441 Strategien" in text and "**6 von 8** Hutverteilungen (75,0 %)" in text and "4 Strategien erreichen" in text and "1 000 gewinnen mindestens die Hälfte" in text
    optimal = {"kind": "Ring", "n": 4, "wins": 8, "total": 16, "status": "OPTIMAL", "bound": 8, "triangle": False}
    kind, text = xp.verdict_e2(optimal)
    assert kind == "info" and "**8 von 16** (50,0 %)" in text and "als optimal bewiesen" in text and "Kein Dreieck" in text and "gewinnt ohnehin 8 von 16" in text
    kind, text = xp.verdict_e2(dict(optimal, triangle=True, status="FEASIBLE", bound=10))
    assert kind == "warning" and "die Schranke des Lösers liegt bei 10" in text and "**nicht** als optimal bewiesen" in text and "mindestens 3/4" in text
    kind, text = xp.verdict_e3({"counts": {2: 4, 3: 0}, "divisibility": [{"n_fields": n, "integer": n in (2, 4, 8, 16)} for n in range(2, 17)]})
    assert kind == "info" and "für N = 2 gibt es 4" in text and "N = 3 gibt es **0**" in text and "2, 4, 8, 16" in text


def test_has_triangle():
    assert xp.has_triangle([[1, 2], [0, 2], [0, 1]]) and not xp.has_triangle([[1], [0, 2], [1]])
    assert not xp.has_triangle([[1, 3], [0, 2], [1, 3], [0, 2]])        # Viereck-Ring
    assert xp.has_triangle([[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]])


def test_formatting_helpers():
    assert ev.de(0.5, 2) == "0,50" and ev.pct(0.78125) == "78,1 %" and ev.thousands(531441) == "531 441"
