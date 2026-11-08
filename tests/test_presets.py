"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, Wirkung jedes Presets."""

import cod_constants as C
import cod_evaluation as ev
import cod_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds_and_choices():
    for name, preset in C.PRESETS.items():
        assert C.N_HUT_MIN <= preset["n_hut"] <= C.N_HUT_MAX and preset["hat_strategy"] in C.HAT_STRATEGIES, name
        assert C.N_REIHE_MIN <= preset["n_reihe"] <= C.N_REIHE_MAX and C.Q_REIHE_MIN <= preset["q_reihe"] <= C.Q_REIHE_MAX, name
        assert C.Q_SUMME_MIN <= preset["q_summe"] <= C.Q_SUMME_MAX and C.N_SUMME_MIN <= preset["n_summe"] <= C.N_SUMME_MAX, name
        assert C.M_BRETT_MIN <= preset["m_brett"] <= C.M_BRETT_MAX and 0 <= preset["seed"] <= C.SEED_MAX, name


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS["Standardfall (Voreinstellung)"]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_every_preset_differs_from_the_default_in_the_setting_its_name_promises():
    base = C.PRESETS["Standardfall (Voreinstellung)"]
    changed = {name: {k for k, v in preset.items() if v != base[k]} for name, preset in C.PRESETS.items() if name != "Standardfall (Voreinstellung)"}
    assert changed["Sieben Hüte: Hamming-Code"] == {"n_hut"}
    assert changed["Fünf Hüte: besser als der Code"] == {"n_hut", "hat_strategy"}
    assert changed["Lange Reihe, viele Farben"] == {"n_reihe", "q_reihe"}
    assert changed["Zu wenige Spieler für alle Farben"] == {"q_summe"}                       # n = 3 Spieler wie im Standard, nur die Farbenzahl steigt von 3 auf 5
    assert changed["Das ganze Schachbrett (64 Felder)"] == {"m_brett"}


def test_preset_helps_name_what_the_presets_set():
    """Die Hilfetexte nennen Zahlen der Presets: Sieben Spieler, fünf Spieler, zwölf Personen mit vier Farben, drei Spieler mit fünf Farben, 64 Felder."""
    p = C.PRESETS
    assert p["Sieben Hüte: Hamming-Code"]["n_hut"] == 7 and "Sieben" in C.PRESET_HELP["Sieben Hüte: Hamming-Code"]
    assert p["Fünf Hüte: besser als der Code"]["n_hut"] == 5 and "Fünf" in C.PRESET_HELP["Fünf Hüte: besser als der Code"]
    assert (p["Lange Reihe, viele Farben"]["n_reihe"], p["Lange Reihe, viele Farben"]["q_reihe"]) == (12, 4)
    assert "Zwölf" in C.PRESET_HELP["Lange Reihe, viele Farben"] and "vier Farben" in C.PRESET_HELP["Lange Reihe, viele Farben"]
    assert (p["Zu wenige Spieler für alle Farben"]["n_summe"], p["Zu wenige Spieler für alle Farben"]["q_summe"]) == (3, 5)
    assert "Drei Spieler, fünf Farben" in C.PRESET_HELP["Zu wenige Spieler für alle Farben"]
    assert 1 << p["Das ganze Schachbrett (64 Felder)"]["m_brett"] == 64 and "64 Felder" in C.PRESET_HELP["Das ganze Schachbrett (64 Felder)"]
    assert "acht Felder" in C.PRESET_HELP["Standardfall (Voreinstellung)"] and 1 << p["Standardfall (Voreinstellung)"]["m_brett"] == 8
