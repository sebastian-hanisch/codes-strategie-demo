"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): n = 2, n = 1, Grenzen inklusive, Eckwerte der Regler."""

import numpy as np
import pytest

import cod_board as B
import cod_constants as C
import cod_evaluation as ev
import cod_graph as G
import cod_hats as H
import cod_line as L
import cod_sums as S


def test_two_hat_players_win_half_with_every_best_rule():
    """n = 2: Das Optimum ist 2 von 4 (die Hälfte): m = 1 Spieler im Code, der andere passt."""
    assert H.active_players(2) == 1
    for strategy in (C.HAT_CODE, C.HAT_BEST, C.HAT_ONE):
        assert int(H.outcomes(H.strategy_actions(2, strategy), H.all_configs(2))["win"].sum()) == 2, strategy
    assert int(H.outcomes(H.strategy_actions(2, C.HAT_ALL), H.all_configs(2))["win"].sum()) == 1


def test_all_hat_sizes_at_the_slider_bounds_and_every_strategy_run():
    for n in (C.N_HUT_MIN, C.N_HUT_MAX):
        for strategy in C.HAT_STRATEGIES:
            a = ev.analyse_hats(n, strategy, 0)
            assert 0 <= a.wins <= a.optimum_wins <= a.bound_wins <= a.total


def test_line_with_two_persons_and_the_largest_enumerated_case():
    hats = L.all_hats(2, 2)
    assert L.saved_counts(hats, L.play_line_batch(hats, 2)).tolist() == [2, 1, 1, 2]       # die erste Person liegt bei (0,0) und (1,1) richtig, die zweite immer
    a = ev.analyse_line(2, 2, 0)
    assert a.exhaustive and a.cases == 4 and a.min_saved == 1 and a.mean_saved == pytest.approx(1.5)
    big = ev.analyse_line(C.N_REIHE_MAX, C.Q_REIHE_MAX, 0)
    assert not big.exhaustive and big.cases == C.SAMPLES and big.min_saved >= C.N_REIHE_MAX - 1


def test_line_enumeration_limit_is_inclusive():
    """Am Reglermaximum n = 12 mit q = 2 sind es 4 096 Verteilungen (vollständig); 6^6 = 46 656 ≤ 100 000 wird aufgezählt, 6^7 = 279 936 > 100 000 nicht."""
    assert ev.analyse_line(12, 2, 0).exhaustive and ev.analyse_line(12, 2, 0).cases == 4096
    assert ev.analyse_line(7, 6, 0).exhaustive is False         # 6^7 = 279 936 > 100 000
    assert ev.analyse_line(6, 6, 0).exhaustive is True and ev.analyse_line(6, 6, 0).cases == 46656


def test_single_player_sums_and_largest_case():
    a = S.analyse_sums(1, 2)
    assert a["wins"] == 1 and a["total"] == 2 and a["win_share"] == 0.5
    big = ev.analyse_sums(C.N_SUMME_MAX, C.Q_SUMME_MAX, 0)
    assert big.total == 6 ** 7 and big.wins == big.total


def test_sums_with_all_colors_equal_to_two_and_one_player():
    """n = 1, q = 2 ist der kleinste Fall: ein Spieler allein gewinnt die Hälfte (= n/q)."""
    assert ev.analyse_sums(1, 2, 0).win_share == pytest.approx(0.5) and ev.analyse_sums(1, 2, 0).bound == 0.5


def test_board_with_two_fields_and_with_sixty_four():
    a = ev.analyse_board(1, 0)
    assert a.n_fields == 2 and a.exhaustive and a.cases == 8 and a.failures == 0                  # 2^2 Bretter mal 2 Schlüsselfelder
    b = ev.analyse_board(6, 0)
    assert b.n_fields == 64 and not b.exhaustive and b.cases == C.BOARD_SAMPLES and b.failures == 0 and b.read == b.key


def test_board_boundary_between_exhaustive_and_sample_is_inclusive_at_16():
    assert ev.analyse_board(4, 0).exhaustive and not ev.analyse_board(5, 0).exhaustive
    assert C.EXHAUSTIVE_MAX_N == 16


def test_board_with_all_coins_equal():
    for fill in (0, 1):
        board = np.full(8, fill, dtype=np.uint8)
        for key in range(8):
            after = B.apply_flip(board, B.flip_field(board, key))
            assert B.read_key(after) == key


def test_graph_with_a_single_edge_has_value_one_half():
    """Zwei Spieler, die sich sehen: Dreier-Regel unmöglich, ein einzelner Rater gewinnt die Hälfte."""
    assert G.enumerate_best([[1], [0]]) == 2


def test_graph_builders_for_the_smallest_sizes():
    assert G.ring_graph(3) == [[1, 2], [0, 2], [0, 1]]
    assert G.chain_graph(3) == [[1], [0, 2], [1]] and G.star_graph(3) == [[1, 2], [0], [0]]
    assert G.complete_graph(3) == G.ring_graph(3)
