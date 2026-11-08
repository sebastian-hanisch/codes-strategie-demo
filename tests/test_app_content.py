"""Inhalt der App (AppTest): Verdikte je Kulisse, jede Strategie-Auswahl, Experimente-Knöpfe, PDF, Permalink, Eckwerte der Regler."""

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import cod_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _app(**state) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in state.items():
        at.session_state[key] = value
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _alerts(at):
    return [e.value for e in list(at.success) + list(at.info) + list(at.warning) + list(at.error)]


def test_default_view_shows_one_verdict_per_scene_with_the_expected_numbers():
    texts = _alerts(_app())
    assert any("**6 von 8**" in t and "75,0 %" in t for t in texts)                         # Hüte gleichzeitig
    assert any("mindestens **5 von 6**" in t and "alle 64 Verteilungen (2^6)" in t for t in texts)   # Reihe
    assert any("Über alle 27 Verteilungen (3^3)" in t and "**genau ein** Tipp" in t for t in texts)  # Summen
    assert any("log₂(8) = 3 Bit" in t and "**alle** 2 048 Fälle" in t for t in texts)         # Schachbrett
    assert not [e for e in _app().error]


@pytest.mark.parametrize("strategy,expected", [(C.HAT_CODE, "**6 von 8**"), (C.HAT_BEST, "**6 von 8**"), (C.HAT_ONE, "**4 von 8**"), (C.HAT_ALL, "**1 von 8**")])
def test_every_hat_strategy_runs_and_names_its_own_win_count(strategy, expected):
    at = _app(hat_strategy_select=strategy)
    assert any(expected in t for t in _alerts(at)), strategy


def test_the_best_strategy_differs_from_the_code_strategy_at_five_players_in_the_app():
    code = _app(n_hut_slider=5, hat_strategy_select=C.HAT_CODE)
    best = _app(n_hut_slider=5, hat_strategy_select=C.HAT_BEST)
    assert any("**24 von 32**" in e.value for e in code.info) and not any("so viel wie die beste mögliche" in t for t in _alerts(code))
    assert any("**25 von 32**" in t and "so viel wie die beste mögliche" in t for t in _alerts(best))


def test_extreme_regler_combinations_do_not_raise():
    low = dict(n_hut_slider=C.N_HUT_MIN, n_reihe_slider=C.N_REIHE_MIN, q_reihe_slider=C.Q_REIHE_MIN, q_summe_slider=C.Q_SUMME_MIN, n_summe_slider=C.N_SUMME_MIN, m_brett_slider=C.M_BRETT_MIN)
    high = dict(n_hut_slider=C.N_HUT_MAX, n_reihe_slider=C.N_REIHE_MAX, q_reihe_slider=C.Q_REIHE_MAX, q_summe_slider=C.Q_SUMME_MAX, n_summe_slider=C.N_SUMME_MAX, m_brett_slider=C.M_BRETT_MAX)
    for combo in (low, high):
        at = _app(**combo)
        assert len(_alerts(at)) >= 4


def test_experiment_buttons_show_their_results():
    at = _app()
    at.button(key="e1_button").click().run(timeout=TIMEOUT)
    assert not at.exception
    assert any("531 441 Strategien" in t and "**6 von 8**" in t for t in _alerts(at))
    at.button(key="e2_button").click().run(timeout=TIMEOUT)
    assert not at.exception
    assert any("Sichtgraph „Jeder sieht jeden“ mit 4 Spielern" in t and "**12 von 16**" in t for t in _alerts(at))


def test_experiment_three_is_always_shown():
    assert any("für N = 2 gibt es 4" in t and "N = 3 gibt es **0**" in t for t in _alerts(_app()))


def test_pdf_button_makes_a_download():
    at = _app()
    at.button(key="pdf_button").click().run(timeout=TIMEOUT)
    assert not at.exception
    assert isinstance(at.session_state["pdf_bytes"], bytes) and at.session_state["pdf_bytes"][:4] == b"%PDF"


@pytest.mark.parametrize("strategy", C.HAT_STRATEGIES)
def test_pdf_builder_handles_every_strategy_name_and_the_special_characters(strategy):
    import cod_evaluation as V
    from cod_pdf_export import build_pdf

    s = V.Settings(hat_strategy=strategy)
    data = build_pdf(s, [("Schachbrett", V.verdict_board(V.analyse_board(3, 1))[1]), ("Reihe", V.verdict_line(V.analyse_line(4, 2, 1))[1])])
    assert data[:4] == b"%PDF" and len(data) > 1000
