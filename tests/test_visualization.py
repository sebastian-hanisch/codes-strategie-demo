"""Abbildungen: alle Achsen gesperrt (fixedrange), richtige Zahl von Spuren und Zellen, Unterscheidungen wie versprochen."""

import numpy as np
import pytest

import cod_constants as C
import cod_evaluation as V
import cod_hats as H
import cod_visualization as Z


def _locked(fig):
    return fig.layout.xaxis.fixedrange is True and fig.layout.yaxis.fixedrange is True


def test_every_figure_has_locked_axes():
    a = V.analyse_hats(5, C.HAT_CODE, 1)
    line = V.analyse_line(6, 3, 1)
    sums = V.analyse_sums(3, 3, 1)
    board = V.analyse_board(3, 1)
    figs = [Z.build_hat_grid(a.classes, 5, a.scene_index), Z.build_hat_table(V.hat_table()), Z.build_line(line.hats, line.answers, 3),
            Z.build_count_distribution(sums.counts, np.array([0.3, 0.4, 0.3, 0.0]), "x"), Z.build_board(board.board, board.key, board.flip, "t"),
            Z.build_e1_histogram(np.array([5, 4, 3, 2, 1, 1, 1, 0, 0]), 6)]
    assert all(_locked(f) for f in figs)


def test_grid_shape_is_near_square_and_covers_all_cells():
    assert [Z.grid_shape(c) for c in (2, 4, 8, 16, 32, 64, 128, 256)] == [(1, 2), (2, 2), (2, 4), (4, 4), (4, 8), (8, 8), (8, 16), (16, 16)]


@pytest.mark.parametrize("n", [2, 5, 8])
def test_hat_grid_has_one_cell_per_distribution_and_three_classes_are_distinguishable(n):
    a = V.analyse_hats(n, C.HAT_ONE, 3)
    fig = Z.build_hat_grid(a.classes, n, a.scene_index)
    z = np.array(fig.data[0].z)
    assert z.size == 1 << n and set(np.unique(z)) <= {0, 1, 2}
    assert int((z == V.OUTCOME_WIN).sum()) == a.wins


def test_hat_classes_split_losses_into_wrong_guess_and_silence():
    """Alle sagen 0: gewonnen nur bei lauter Nullen; sonst verloren, und zwar immer mit falschem Tipp (es raten ja alle)."""
    a = V.analyse_hats(3, C.HAT_ALL, 0)
    assert a.classes.tolist() == [V.OUTCOME_WIN] + [V.OUTCOME_WRONG] * 7
    # Syndrom-Strategie bei n = 4: Spieler 4 passt immer; Verteilungen, bei denen niemand rät, gibt es nicht (jede hat ein Syndrom ≠ 0 mit Rater oder ist ein Codewort mit Ratern)
    b = V.analyse_hats(4, C.HAT_CODE, 0)
    assert (b.classes == V.OUTCOME_SILENT).sum() == 0


def test_board_figure_marks_key_and_flip_and_numbers_every_field():
    board = np.zeros(16, dtype=np.uint8)
    fig = Z.build_board(board, key=5, flipped=9, title="t")
    texts = [a.text for a in fig.layout.annotations]
    assert len(texts) == 16 and "★ 5" in texts and sum("★" in t for t in texts) == 1
    assert len(fig.layout.shapes) == 1
    assert len(Z.build_board(board, key=5, flipped=None, title="t").layout.shapes) == 0


def test_line_figure_marks_right_and_wrong_tips():
    fig = Z.build_line((1, 0, 1), (0, 0, 1), 2)
    texts = [a.text for a in fig.layout.annotations]
    assert texts == ["✘ 0", "✔ 0", "✔ 1"]
    assert list(fig.data[0].marker.color) == [C.HAT_COLORS[1], C.HAT_COLORS[0], C.HAT_COLORS[1]]


def test_count_distribution_shows_shares_in_percent():
    fig = Z.build_count_distribution(np.array([0, 4, 0]), np.array([0.25, 0.5, 0.25]), "x")
    assert list(fig.data[0].y) == [0.0, 100.0, 0.0] and list(fig.data[1].y) == [25.0, 50.0, 25.0]


def test_hat_table_chart_uses_percent_of_all_distributions():
    rows = V.hat_table()
    fig = Z.build_hat_table(rows)
    assert [round(y, 3) for y in fig.data[1].y][:4] == [50.0, 75.0, 75.0, 78.125]
    assert fig.data[2].y[3] == 100 * H.count_bound(5) / 32
