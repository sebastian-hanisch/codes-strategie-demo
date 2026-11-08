"""Eigenschaftstests (ORACLE-PLAYBOOK §5.2, metamorph): Aussagen über die Verfahren, die ohne Kenntnis des richtigen Ergebnisses gelten müssen.

* Umnummerieren der Spieler (andere Positionen im Hamming-Code) ändert die Gewinnzahl der Code-Strategie nicht.
* Bei n = 3 und n = 7 enthält der Hamming-Code den Vektor aus lauter Einsen: die Gewinnmenge ist unter dem Vertauschen beider Farben (alle Hüte umdrehen) invariant.
* Mit mehr Spielern gewinnt die beste Strategie nie weniger (ein zusätzlicher Spieler kann immer passen).
* Summen-Hüte: Eine gemeinsame Verschiebung aller Zielsummen ändert die Verteilung der Trefferzahlen nicht.
* Schachbrett: Das Umdrehen von Feld j ändert S um genau j (die Lemma-Zeile des Beweises), für beliebige Bretter mit 64 Feldern.
* Gleicher Zufalls-Seed gibt in einem zweiten Prozess (andere Hash-Randomisierung) dieselbe Ausgabe."""

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

import cod_board as B
import cod_evaluation as V
import cod_hats as H
import cod_sums as S

ROOT = Path(__file__).resolve().parent.parent


def test_renumbering_the_players_keeps_the_win_count():
    rng = np.random.default_rng(7)
    for n in (3, 5, 7, 8):
        m = H.active_players(n)
        configs = H.all_configs(n)
        for _ in range(5):
            perm = rng.permutation(n)
            permuted = configs[:, perm]                                  # Spieler i bekommt die Position von Spieler perm[i]
            d = H.syndrome(permuted[:, :], m) == 0
            assert H.wins_of_losing_set(d, n) == {3: 6, 5: 24, 7: 112, 8: 224}[n], (n, perm.tolist())


def test_complementing_all_hats_keeps_the_winning_set_for_three_and_seven_players():
    for n in (3, 7):
        win = H.outcomes(H.losing_set_strategy(H.syndrome_zero_set(n), n), H.all_configs(n))["win"]
        complement = np.arange(1 << n) ^ ((1 << n) - 1)
        assert (win == win[complement]).all(), n


def test_more_players_never_lower_the_best_value():
    shares = [r["best"] / r["total"] for r in V.hat_table()]
    assert all(b >= a for a, b in zip(shares, shares[1:]))


def test_shifting_all_target_sums_keeps_the_distribution_of_hits(monkeypatch):
    base = {(n, q): S.analyse_sums(n, q)["counts"].tolist() for n, q in ((3, 3), (2, 4), (4, 3), (3, 5))}
    for c in (1, 2):
        monkeypatch.setattr(S, "residue_of", lambda player, q, c=c: (player + c) % q)
        for (n, q), counts in base.items():
            assert S.analyse_sums(n, q)["counts"].tolist() == counts, (n, q, c)


def test_flipping_field_j_changes_the_code_by_exactly_j_on_random_boards():
    rng = np.random.default_rng(5)
    boards = rng.integers(0, 2, size=(2000, 64), dtype=np.uint8)
    code = B.board_code(boards)
    for j in range(64):
        flipped = boards.copy()
        flipped[:, j] ^= 1
        assert (B.board_code(flipped) == code ^ j).all(), j


def test_board_strategy_reaches_every_key_from_every_board_with_one_flip():
    """Zu jedem Brett und jedem Schlüssel gibt es genau ein Feld, das umgedreht werden muss (64 verschiedene Felder für 64 Schlüssel)."""
    rng = np.random.default_rng(9)
    for _ in range(50):
        board = B.random_board(64, rng)
        fields = {B.flip_field(board, key) for key in range(64)}
        assert fields == set(range(64))


_SCRIPT = """
import json, sys
sys.path.insert(0, {root!r})
import cod_evaluation as V
h = V.analyse_hats(7, "Code-Strategie (Summe der Positionen)", 35)
l = V.analyse_line(8, 3, 35)
s = V.analyse_sums(4, 3, 35)
b = V.analyse_board(5, 35)
print(json.dumps([h.wins, h.scene, h.scene_index, l.min_saved, l.mean_saved, list(l.hats), list(l.answers), s.wins, list(s.hats), b.key, b.flip, b.failures, list(map(int, b.board))]))
"""


def _run(hashseed: str) -> str:
    env = dict(os.environ, PYTHONHASHSEED=hashseed)
    done = subprocess.run([sys.executable, "-c", _SCRIPT.format(root=str(ROOT))], capture_output=True, text=True, env=env, timeout=120)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def test_same_seed_gives_the_same_output_in_two_processes_with_different_hash_seeds():
    a, b = _run("1"), _run("2")
    assert a == b
    assert json.loads(a)[0] == 112
