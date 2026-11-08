"""Hüte gleichzeitig (cod_hats): jede Einheit gegen Handrechnung, die vorgerechneten Überdeckungscodes auf Gültigkeit, Zweig-Tests."""

import json

import numpy as np
import pytest

import cod_constants as C
import cod_hats as H


def test_all_configs_has_bit_i_of_r_in_column_i():
    c = H.all_configs(3)
    assert c.shape == (8, 3)
    assert c[6].tolist() == [0, 1, 1]            # r = 6 = 0b110
    assert H.config_index(c).tolist() == list(range(8))


def test_active_players_is_the_largest_two_power_minus_one():
    assert [H.active_players(n) for n in range(1, 11)] == [1, 1, 3, 3, 3, 3, 7, 7, 7, 7]


def test_syndrome_by_hand():
    # Hüte 1 an den Positionen 1 und 6 (Spieler 0 und 5), m = 7: 1 ^ 6 = 7
    c = np.zeros((1, 7), dtype=np.uint8)
    c[0, 0] = c[0, 5] = 1
    assert H.syndrome(c, 7).tolist() == [7]
    # drei Einsen an den Positionen 1, 2, 3: 1 ^ 2 ^ 3 = 0 (Codewort der Länge 3)
    c3 = np.array([[1, 1, 1]], dtype=np.uint8)
    assert H.syndrome(c3, 3).tolist() == [0]


def test_syndrome_zero_set_has_the_expected_size():
    for n, expected in ((3, 2), (4, 4), (7, 16), (8, 32)):
        assert int(H.syndrome_zero_set(n).sum()) == expected, n


def test_code_strategy_hand_cases_for_three_players(hand_hats3):
    actions = H.losing_set_strategy(H.syndrome_zero_set(3), 3)
    for r, expected in hand_hats3.items():
        assert tuple(int(a) for a in actions[r]) == expected, r


def test_outcomes_on_hand_cases():
    configs = H.all_configs(3)
    actions = H.losing_set_strategy(H.syndrome_zero_set(3), 3)
    o = H.outcomes(actions, configs)
    assert o["win"].tolist() == [False, True, True, True, True, True, True, False]       # verloren nur auf 000 und 111
    assert o["guessers"][[0, 1, 3]].tolist() == [3, 1, 1] and o["wrong"][[0, 1, 3]].tolist() == [3, 0, 0]


def test_the_strategy_reads_only_the_hats_of_the_others():
    """Ändert man nur den eigenen Hut eines Spielers, ändert sich seine Aktion nicht."""
    for n in (3, 5, 7):
        configs = H.all_configs(n)
        for strategy in C.HAT_STRATEGIES:
            actions = H.strategy_actions(n, strategy)
            for i in range(n):
                flipped = np.arange(len(configs)) ^ (1 << i)
                assert (actions[:, i] == actions[flipped, i]).all(), (n, strategy, i)


def test_count_bound_by_hand():
    assert [H.count_bound(n) for n in (2, 3, 4, 5, 6, 7, 8)] == [2, 6, 12, 26, 54, 112, 227]


def test_wins_of_losing_set_equal_two_to_n_minus_size_for_dominating_sets():
    for n in (3, 4, 7):
        d = H.syndrome_zero_set(n)
        assert H.wins_of_losing_set(d, n) == (1 << n) - int(d.sum())


def test_non_dominating_set_wins_less_than_the_formula():
    """D = nur Verteilung 000 bei n = 3 überdeckt nicht jede Verteilung: 111 hat keinen Nachbarn in D. Die Strategie gewinnt dann nur auf den 3 Nachbarn von 000."""
    d = np.zeros(8, dtype=bool)
    d[0] = True
    assert H.wins_of_losing_set(d, 3) == 3 < 8 - 1


def test_fixed_strategies_by_hand():
    n = 3
    configs = H.all_configs(n)
    one = H.outcomes(H.strategy_actions(n, C.HAT_ONE), configs)["win"]
    assert one.sum() == 4 and one[configs[:, 0] == 0].all()               # Spieler 1 sagt immer 0: gewinnt bei Hut 0
    everyone = H.outcomes(H.strategy_actions(n, C.HAT_ALL), configs)["win"]
    assert everyone.sum() == 1 and everyone[0]                              # alle sagen 0: nur bei 000


def test_unknown_strategy_name_is_rejected():
    with pytest.raises(ValueError):
        H.strategy_actions(3, "gibt es nicht")


def test_stored_optimum_codes_are_dominating_and_have_the_stored_size():
    raw = json.loads(H.DATA_FILE.read_text(encoding="utf-8"))["codes"]
    assert sorted(int(k) for k in raw) == list(range(2, C.HAT_OPTIMUM_MAX_N + 1))
    for key, entry in raw.items():
        n = int(key)
        d = H.load_optimum()[n]
        assert int(d.sum()) == entry["size"] == len(entry["losing"]) and entry["wins"] == (1 << n) - entry["size"]
        covered = d.copy()                                     # jede Verteilung liegt in D oder hat einen Nachbarn in D
        for j in range(n):
            covered |= d[np.arange(1 << n) ^ (1 << j)]
        assert covered.all(), n
        assert H.wins_of_losing_set(d, n) == entry["wins"], n


def test_best_strategy_differs_from_the_code_strategy_for_five_and_six_players():
    """Zweig-Test: Die Wahl „Beste Strategie“ ändert das Ergebnis genau dort, wo der Code nicht optimal ist (n = 5: 25 statt 24; n = 6: 52 statt 48)."""
    for n, best, code in ((5, 25, 24), (6, 52, 48), (3, 6, 6), (7, 112, 112)):
        configs = H.all_configs(n)
        assert int(H.outcomes(H.strategy_actions(n, C.HAT_BEST), configs)["win"].sum()) == best
        assert int(H.outcomes(H.strategy_actions(n, C.HAT_CODE), configs)["win"].sum()) == code


def test_enumerate_all_strategies_n3_total_and_best():
    r = H.enumerate_all_strategies_n3()
    assert r["total"] == 3 ** 12 == len(r["wins"])
    assert int(r["wins"].max()) == 6 and int((r["wins"] == 6).sum()) == 4
