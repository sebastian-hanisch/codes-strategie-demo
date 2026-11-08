"""Hüte in der Reihe, Summen-Hüte, Schachbrett: jede Einheit gegen Handrechnung (DEMO-PLAYBOOK §1b)."""

import numpy as np
import pytest

import cod_board as B
import cod_line as L
import cod_sums as S


# --- Reihe ------------------------------------------------------------------------------------------------------------------------------------
def test_line_hand_case_two_colors():
    """Hüte (hinten nach vorn) 1, 0, 1, 1: Person 1 sieht 0 + 1 + 1 = 2, sagt 2 mod 2 = 0 an (ihr Hut ist 1: falsch).
    Person 2 sieht 1, 1 (Summe 2), kennt a1 = 0: 0 − 2 − (nichts gehört) = 0 mod 2 = 0: richtig (Hut 0).
    Person 3 sieht 1, kennt a1 = 0, hat a2 = 0 gehört: 0 − 1 − 0 = −1 mod 2 = 1: richtig. Person 4 sieht nichts: 0 − 0 − (0 + 1) = −1 mod 2 = 1: richtig."""
    assert L.play_line((1, 0, 1, 1), 2) == (0, 0, 1, 1)


def test_line_hand_case_three_colors():
    """Hüte 2, 1, 2 bei q = 3: a1 = (1 + 2) mod 3 = 0 (Hut 2: falsch). Person 2 sieht 2: 0 − 2 = −2 mod 3 = 1 (richtig). Person 3: 0 − 0 − 1 = −1 mod 3 = 2 (richtig)."""
    assert L.play_line((2, 1, 2), 3) == (0, 1, 2)


def test_first_and_later_answer_units():
    assert L.first_answer((1, 1, 1), 2) == 1 and L.first_answer((), 5) == 0
    assert L.later_answer((1,), (0, 0), 2) == 1          # 0 − 1 − 0 mod 2
    assert L.later_answer((), (3, 1, 2), 4) == 0         # 3 − 0 − (1 + 2) mod 4


def test_batch_equals_scalar_protocol():
    rng = np.random.default_rng(3)
    for n, q in ((2, 2), (5, 3), (7, 4)):
        hats = rng.integers(0, q, size=(60, n), dtype=np.int8)
        batch = L.play_line_batch(hats, q)
        for row, answers in zip(hats, batch):
            assert tuple(int(a) for a in answers) == L.play_line(tuple(int(x) for x in row), q)


def test_everyone_but_the_first_is_right_for_all_small_cases():
    for n, q in ((2, 2), (3, 2), (4, 3), (5, 4), (6, 2)):
        hats = L.all_hats(n, q)
        saved = L.saved_counts(hats, L.play_line_batch(hats, q))
        assert saved.min() == n - 1 and (saved[:] >= n - 1).all()
        assert (L.play_line_batch(hats, q)[:, 1:] == hats[:, 1:]).all()


def test_all_hats_shape_and_distinctness():
    h = L.all_hats(3, 3)
    assert h.shape == (27, 3) and len({tuple(r) for r in h.tolist()}) == 27


def test_binomial_distribution_by_hand():
    assert L.binomial_distribution(2, 2).tolist() == [0.25, 0.5, 0.25]
    assert L.binomial_distribution(3, 3).sum() == pytest.approx(1.0) and L.binomial_distribution(3, 3)[0] == pytest.approx(8 / 27)


def test_analyse_line_uses_all_cases_up_to_the_limit_inclusive_and_samples_above():
    rng = np.random.default_rng(1)
    a = L.analyse_line(4, 3, 81, 50, rng)            # 3^4 = 81 = Grenze: vollständig
    assert a["exhaustive"] and a["cases"] == 81
    b = L.analyse_line(4, 3, 80, 50, np.random.default_rng(1))   # 81 > 80: Stichprobe
    assert not b["exhaustive"] and b["cases"] == 50
    assert b["min"] >= 3


# --- Summen-Hüte ------------------------------------------------------------------------------------------------------------------------------
def test_sums_hand_case():
    """q = 3, Hüte (2, 0, 1): Summe 3 ≡ 0. Spieler 0 (Ziel 0) sieht 0 + 1 = 1 und tippt −1 mod 3 = 2 (richtig). Spieler 1 (Ziel 1) sieht 3 und tippt (1 − 3) mod 3 = 1 (Hut 0: falsch).
    Spieler 2 (Ziel 2) sieht 2 und tippt 0 (Hut 1: falsch). Genau ein Treffer."""
    hats = np.array([[2, 0, 1]])
    assert S.guesses_batch(hats, 3).tolist() == [[2, 1, 0]]
    assert S.right_counts(hats, S.guesses_batch(hats, 3)).tolist() == [1]


def test_sums_units():
    assert S.residue_of(4, 3) == 1 and S.guess(0, 4, 3) == 2 and S.guess(2, 0, 5) == 2


def test_exactly_one_right_when_players_equal_colors():
    for q in range(2, 7):
        a = S.analyse_sums(q, q)
        assert a["counts"].tolist() == [0, q ** q] + [0] * (q - 1) and a["wins"] == q ** q


def test_bound_and_values_for_other_player_numbers():
    assert S.win_bound(2, 5) == pytest.approx(0.4) and S.win_bound(6, 4) == 1.0
    for n, q in ((1, 3), (2, 3), (2, 4), (3, 4), (4, 3), (5, 2), (7, 3)):
        assert S.analyse_sums(n, q)["win_share"] == pytest.approx(min(1.0, n / q)), (n, q)


def test_chance_values_by_hand():
    assert S.chance_win_share(2, 2) == pytest.approx(0.75) and S.chance_win_share(3, 3) == pytest.approx(1 - 8 / 27)
    assert S.chance_distribution(2, 2).tolist() == [0.25, 0.5, 0.25]


# --- Schachbrett ------------------------------------------------------------------------------------------------------------------------------
def test_board_code_by_hand():
    """Köpfe auf den Feldern 1, 2, 5 bei N = 8: 1 ^ 2 ^ 5 = 6."""
    board = np.zeros(8, dtype=np.uint8)
    board[[1, 2, 5]] = 1
    assert B.board_code(board).tolist() == [6]
    assert B.board_code(np.zeros(8, dtype=np.uint8)).tolist() == [0]


def test_board_walkthrough_by_hand():
    """Brett wie oben (S = 6), Schlüsselfeld 3: A dreht Feld 6 ^ 3 = 5 um (Kopf → Zahl); danach Köpfe auf 1, 2: S = 3."""
    board = np.zeros(8, dtype=np.uint8)
    board[[1, 2, 5]] = 1
    flip = B.flip_field(board, 3)
    assert flip == 5
    after = B.apply_flip(board, flip)
    assert after.tolist() == [0, 1, 1, 0, 0, 0, 0, 0] and B.read_key(after) == 3
    assert board.tolist()[5] == 1                       # das Original bleibt unverändert


def test_apply_flip_changes_exactly_one_field():
    board = np.array([1, 0, 1, 1], dtype=np.uint8)
    after = B.apply_flip(board, 2)
    assert int((board != after).sum()) == 1 and after[2] == 0


def test_check_all_small_boards_have_no_failures():
    for n in (2, 4, 8):
        r = B.check_all(n)
        assert r["cases"] == (1 << n) * n and r["failures"] == 0


def test_check_all_rejects_non_powers_of_two():
    with pytest.raises(ValueError):
        B.check_all(3)


def test_check_sample_counts_and_is_clean():
    r = B.check_sample(64, 300, np.random.default_rng(2))
    assert r == {"cases": 300, "failures": 0}


def test_is_power_of_two():
    assert [n for n in range(0, 70) if B.is_power_of_two(n)] == [1, 2, 4, 8, 16, 32, 64]


def test_class_size_and_perfect_colourings_by_hand():
    assert B.class_size(8) == (256, 8) and B.class_size(3) == (8, 3)
    # N = 2: Nachbarn von 0 sind 1 und 2, von 3 sind 2 und 1: gefordert c1 ≠ c2 und c0 ≠ c3 → 2 · 2 = 4 Färbungen
    assert B.count_perfect_colorings(2) == 4
    assert B.count_perfect_colorings(3) == 0
