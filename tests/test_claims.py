"""Jede Zahl aus der README und den Hilfetexten, nachgerechnet (DEMO-PLAYBOOK §4 und §11a).

Alle Zahlen dieser Demo sind Aufzählungen oder Beweise, keine Zufallsmessungen: die Tests rechnen sie exakt nach (ganze Zahlen, Brüche); nur die Stichproben am 64-Felder-Brett (20 000 Fälle) und bei den langen Reihen
sind Stichproben und stehen in der README als solche. Keine Zeit-Assertion, keine Gleitkommagleichheit außer mit `approx`.
Die Zählungen („in k von m Kombinationen“) stehen als Zählungen im Test, nicht als Urteilswort."""

import json
import math
from fractions import Fraction

import numpy as np
import pytest

import cod_board as B
import cod_constants as C
import cod_evaluation as V
import cod_experiments as XP
import cod_graph as G
import cod_hats as H
import cod_line as L
import cod_sums as S


def wins_of(n, strategy):
    return int(H.outcomes(H.strategy_actions(n, strategy), H.all_configs(n))["win"].sum())


# --- Hüte gleichzeitig ------------------------------------------------------------------------------------------------------------------------
def test_claim_three_players_all_531441_strategies():
    r = XP.e1_all_strategies()
    assert r["total"] == 531441 == 3 ** 12
    assert r["best"] == 6 and r["n_best"] == 4 and V.pct(r["best"] / 8) == "75,0 %"
    assert r["n_at_least_half"] == 26550
    assert r["histogram"].tolist() == [16335, 120736, 228780, 139040, 25922, 624, 4, 0, 0]
    assert int(r["histogram"].sum()) == 531441


def test_claim_table_bound_code_and_best_for_two_to_eight_players():
    rows = {r["n"]: r for r in V.hat_table()}
    assert [rows[n]["bound"] for n in range(2, 9)] == [2, 6, 12, 26, 54, 112, 227]
    assert [rows[n]["code"] for n in range(2, 9)] == [2, 6, 12, 24, 48, 112, 224]
    assert [rows[n]["best"] for n in range(2, 9)] == [2, 6, 12, 25, 52, 112, 224]
    assert [rows[n]["total"] for n in range(2, 9)] == [4, 8, 16, 32, 64, 128, 256]
    assert [rows[n]["players_used"] for n in range(2, 9)] == [1, 3, 3, 3, 3, 7, 7]


def test_claim_best_beats_code_in_exactly_two_of_seven_sizes_with_the_stated_percentages():
    rows = V.hat_table()
    better = [r["n"] for r in rows if r["best"] > r["code"]]
    assert better == [5, 6] and len(rows) == 7
    assert (V.pct(25 / 32), V.pct(24 / 32), V.pct(52 / 64), V.pct(48 / 64)) == ("78,1 %", "75,0 %", "81,2 %", "75,0 %")


def test_claim_the_integer_bound_is_reached_at_n_2_3_4_7_and_missed_at_5_6_8():
    rows = {r["n"]: r for r in V.hat_table()}
    assert [n for n in range(2, 9) if rows[n]["best"] == rows[n]["bound"]] == [2, 3, 4, 7]
    assert [n for n in range(2, 9) if rows[n]["best"] < rows[n]["bound"]] == [5, 6, 8]
    assert (rows[8]["best"], rows[8]["bound"]) == (224, 227)


def test_claim_hamming_codes_are_perfect_for_three_and_seven_players():
    assert (wins_of(3, C.HAT_CODE), wins_of(7, C.HAT_CODE)) == (6, 112)
    assert Fraction(6, 8) == Fraction(3, 4) and Fraction(112, 128) == Fraction(7, 8)
    assert V.pct(6 / 8) == "75,0 %" and V.pct(112 / 128) == "87,5 %"
    for n in (3, 7):
        assert wins_of(n, C.HAT_CODE) == H.count_bound(n)                # genau die Obergrenze: perfekt
    assert wins_of(8, C.HAT_CODE) == 224 < H.count_bound(8) == 227        # nicht perfekt bei n = 8: ein Spieler passt immer


def test_claim_overview_comparison_with_single_guesser_and_everyone_guessing():
    for n in range(2, 9):
        assert wins_of(n, C.HAT_ONE) == 1 << (n - 1)                      # einer rät allein: die Hälfte
        assert wins_of(n, C.HAT_ALL) == 1                                 # alle sagen 0: nur bei lauter Nullen
    assert wins_of(3, C.HAT_CODE) > wins_of(3, C.HAT_ONE) and wins_of(7, C.HAT_CODE) == 112 and wins_of(7, C.HAT_ONE) == 64


def test_claim_optimum_sizes_of_dominating_sets():
    sizes = {n: int(H.load_optimum()[n].sum()) for n in range(2, 9)}
    assert sizes == {2: 2, 3: 2, 4: 4, 5: 7, 6: 12, 7: 16, 8: 32}
    assert {n: (1 << n) - s for n, s in sizes.items()} == {2: 2, 3: 6, 4: 12, 5: 25, 6: 52, 7: 112, 8: 224}


def test_claim_counting_bound_argument_by_enumeration_for_three_players():
    """W ≤ #richtig = #falsch ≤ n · L: für jede der 531 441 Strategien gilt W/(W + L) ≤ n/(n + 1) = 3/4, also W ≤ 6."""
    wins = H.enumerate_all_strategies_n3()["wins"]
    assert int(wins.max()) <= H.count_bound(3) == 6


# --- Reihe ------------------------------------------------------------------------------------------------------------------------------------
def test_claim_line_all_enumerated_combinations_give_n_minus_one_and_the_mean():
    combos = [(n, q) for n in range(C.N_REIHE_MIN, C.N_REIHE_MAX + 1) for q in range(C.Q_REIHE_MIN, C.Q_REIHE_MAX + 1)]
    enumerated = [(n, q) for n, q in combos if q ** n <= C.ENUM_LIMIT]
    assert (len(enumerated), len(combos)) == (38, 55)
    for n, q in enumerated:
        a = L.analyse_line(n, q, C.ENUM_LIMIT, C.SAMPLES, np.random.default_rng(0))
        assert a["exhaustive"] and a["min"] == n - 1 and a["mean"] == pytest.approx(n - 1 + 1 / q), (n, q)


def test_claim_line_example_twelve_persons_two_colors():
    a = V.analyse_line(12, 2, 35)
    assert a.exhaustive and a.cases == 4096 and a.min_saved == 11
    assert V.de(a.mean_saved, 2) == "11,50" and V.de(a.chance_mean, 2) == "6,00"


def test_claim_line_with_the_sample_cases_still_has_n_minus_one():
    for q in (4, 5, 6):
        a = V.analyse_line(12, q, 35)
        assert not a.exhaustive and a.cases == 5000 and a.min_saved == 11


def test_claim_line_first_person_is_right_in_one_over_q_of_all_distributions():
    for n, q in ((4, 2), (4, 3), (3, 5)):
        h = L.all_hats(n, q)
        first_right = (L.play_line_batch(h, q)[:, 0] == h[:, 0]).mean()
        assert first_right == pytest.approx(1 / q)


# --- Summen-Hüte ------------------------------------------------------------------------------------------------------------------------------
def test_claim_sums_exactly_one_right_for_n_equals_q_two_to_six():
    for q in range(2, 7):
        a = S.analyse_sums(q, q)
        assert a["counts"][1] == q ** q == a["total"] and a["wins"] == a["total"]


def test_claim_sums_chance_values_and_the_limit():
    assert V.pct(S.chance_win_share(3, 3)) == "70,4 %" and V.pct(S.chance_win_share(6, 6)) == "66,5 %"
    assert Fraction(19, 27) == 1 - Fraction(8, 27)
    assert abs(1 - (1 - 1 / 1000) ** 1000 - (1 - math.exp(-1))) < 1e-3                         # für n = q → ∞ nähert sich der Anteil 1 − 1/e = 63,2 % (Hinweis in der README, nicht in der App)
    assert V.pct(1 - math.exp(-1)) == "63,2 %"


def test_claim_sums_three_players_five_colors():
    a = S.analyse_sums(3, 5)
    assert (a["wins"], a["total"]) == (75, 125) and V.pct(a["win_share"]) == "60,0 %"
    assert V.pct(S.win_bound(3, 5)) == "60,0 %"


def test_claim_sums_more_players_than_colors_always_at_least_one():
    for n, q in ((4, 3), (5, 3), (7, 2), (6, 4), (7, 6)):
        a = S.analyse_sums(n, q)
        assert a["counts"][0] == 0 and a["wins"] == a["total"], (n, q)


def test_claim_sums_win_share_never_decreases_with_more_players():
    for q in range(2, 7):
        shares = [S.analyse_sums(n, q)["win_share"] for n in range(1, 8)]
        assert all(b >= a - 1e-12 for a, b in zip(shares, shares[1:])), q


# --- Schachbrett ------------------------------------------------------------------------------------------------------------------------------
def test_claim_board_exhaustive_case_counts():
    for n, cases in ((2, 8), (4, 64), (8, 2048), (16, 1048576)):
        r = B.check_all(n)
        assert r == {"cases": cases, "failures": 0} and cases == n * 2 ** n


def test_claim_board_sixty_four_is_a_sample_of_twenty_thousand():
    a = V.analyse_board(6, 35)
    assert not a.exhaustive and a.cases == 20000 == C.BOARD_SAMPLES and a.failures == 0 and a.n_fields == 64


def test_claim_board_bits_and_class_sizes():
    assert [(1 << m).bit_length() - 1 for m in range(1, 7)] == [1, 2, 3, 4, 5, 6]
    assert V.board_class_text(8) == "2^8 / 8 = 32: ganzzahlig." and V.board_class_text(64).startswith("2^64 / 64 =")
    assert [n for n in range(2, 17) if (1 << n) % n == 0] == [2, 4, 8, 16]


def test_claim_board_only_powers_of_two_by_enumeration_and_counting():
    r = XP.e3_colorings()
    assert r["counts"] == {2: 4, 3: 0}
    assert [d["n_fields"] for d in r["divisibility"] if d["integer"]] == [2, 4, 8, 16]
    assert Fraction(2 ** 3, 3).denominator == 3 and Fraction(2 ** 6, 6).denominator == 3


def test_claim_board_class_size_argument_for_N_4_by_the_xor_strategy():
    """Bei N = 4 hat jede Farbklasse (Wert S) genau 2^4 / 4 = 4 Bretter."""
    boards = B.all_boards(4)
    codes = B.board_code(boards)
    assert np.bincount(codes, minlength=4).tolist() == [4, 4, 4, 4]


# --- Sichtgraph -------------------------------------------------------------------------------------------------------------------------------
def test_claim_graph_values_for_three_to_five_players():
    pytest.importorskip("ortools")
    expected = {
        ("Jeder sieht jeden", 3): 6, ("Jeder sieht jeden", 4): 12, ("Jeder sieht jeden", 5): 25,
        ("Ring", 3): 6, ("Ring", 4): 8, ("Ring", 5): 16,
        ("Kette", 3): 4, ("Kette", 4): 8, ("Kette", 5): 16,
        ("Stern", 3): 4, ("Stern", 4): 8, ("Stern", 5): 16,
    }
    for (kind, n), wins in expected.items():
        r = XP.e2_graph(kind, n)
        assert r["status"] == "OPTIMAL" and r["wins"] == wins and r["total"] == 1 << n, (kind, n)


def test_claim_graphs_without_triangle_are_at_one_half_and_with_triangle_at_least_three_quarters():
    pytest.importorskip("ortools")
    no_triangle = [("Ring", 4), ("Ring", 5), ("Kette", 3), ("Kette", 4), ("Kette", 5), ("Stern", 3), ("Stern", 4), ("Stern", 5)]
    for kind, n in no_triangle:
        r = XP.e2_graph(kind, n)
        assert not r["triangle"] and r["status"] == "OPTIMAL" and Fraction(r["wins"], r["total"]) == Fraction(1, 2), (kind, n)
    assert len(no_triangle) == 8
    for kind, n in (("Jeder sieht jeden", 3), ("Jeder sieht jeden", 4), ("Jeder sieht jeden", 5), ("Ring", 3)):
        r = XP.e2_graph(kind, n)
        assert r["triangle"] and Fraction(r["wins"], r["total"]) >= Fraction(3, 4), (kind, n)


def test_claim_embedding_a_triangle_gives_three_quarters_in_any_graph():
    """Ein Dreieck unter den Spielern plus Passen der übrigen: 3/4 der Verteilungen, gezählt an einem Graphen mit 5 Spielern (Dreieck 0, 1, 2; 3 und 4 passen)."""
    configs = H.all_configs(5)
    actions = np.full((32, 5), H.PASS, dtype=np.uint8)
    actions[:, :3] = H.losing_set_strategy(H.syndrome_zero_set(3), 3)[configs[:, 0] + 2 * configs[:, 1] + 4 * configs[:, 2], :]
    assert int(G.win_flags(actions, configs).sum()) == 24 and Fraction(24, 32) == Fraction(3, 4)


def test_claim_a_single_guesser_wins_half_in_every_graph():
    for kind in C.GRAPH_KINDS:
        for n in range(C.GRAPH_N_MIN, C.GRAPH_N_MAX + 1):
            nbrs = G.make_graph(kind, n, C.GRAPH_KINDS)
            configs = H.all_configs(n)
            actions = np.full((1 << n, n), H.PASS, dtype=np.uint8)
            actions[:, 0] = 0
            assert int(G.win_flags(actions, configs).sum()) == 1 << (n - 1), (kind, n)
            assert len(nbrs) == n


def test_claim_stored_data_file_matches_the_constants():
    raw = json.loads(H.DATA_FILE.read_text(encoding="utf-8"))["codes"]
    assert max(int(k) for k in raw) == C.HAT_OPTIMUM_MAX_N == 8
