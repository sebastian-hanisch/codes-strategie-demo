"""Orakel-Tests (DEMO-PLAYBOOK §12): jede Kernroutine gegen einen anderen Rechenweg.

* Hüte gleichzeitig: reine Python-Schleifen mit einer Parity-Check-Matrix (statt XOR der Positionen) gegen die vektorisierte Code-Strategie; für drei Spieler die Gewinnzahl von
  Strategien aus der Aufzählung aller 3^12 Strategien in Schleifenfassung (Stichprobe + alle Beststrategien), das Optimum n = 2 … 5 als CP-SAT-Strategiemodell (anderes Modell als
  die dominierende Menge), n = 2 … 7 als HiGHS-Überdeckungsmodell und n ≤ 4 durch Aufzählung aller Teilmengen.
* Reihe und Summen-Hüte: Aufzählung ALLER Strategien für kleine (n, q) in Schleifenfassung: bester schlechtester Fall, bestes Mittel bzw. beste Gewinnzahl.
* Schachbrett: Schleifen für alle Bretter bis N = 8; die Nicht-Existenz für N = 3, 5, 6, 7 und die Existenz für N = 2, 4 als CP-SAT-Modell der Färbung.
* Sichtgraph: Aufzählung aller Strategien in Schleifenfassung gegen die vektorisierte Aufzählung und gegen das ganzzahlige Modell.
Das Orakel steht in den Tests, nicht im Kern. Der volle Lauf (alle 531 441 Strategien in Python-Schleifen und q^n-Läufe weit über die Suite hinaus) stand im Scratch-Lauf `teamraetsel-planung/vormessung/`."""

import itertools
import random

import numpy as np
import pytest

import cod_board as B
import cod_constants as C
import cod_evaluation as V
import cod_graph as G
import cod_hats as H
import cod_line as L
import cod_sums as S

PASS = 2


# --- Hüte gleichzeitig ------------------------------------------------------------------------------------------------------------------------
def parity_check_columns(m):
    """Spalten der Parity-Check-Matrix des Hamming-Codes der Länge m = 2^r − 1: Spalte p (1 … m) ist die Binärdarstellung von p."""
    r = m.bit_length()
    return [[(p >> k) & 1 for k in range(r)] for p in range(1, m + 1)]


def is_codeword(vector, m):
    cols = parity_check_columns(m)
    r = len(cols[0])
    return all(sum(vector[p] * cols[p][k] for p in range(m)) % 2 == 0 for k in range(r))


def hamming_decision(n, i, others):
    """Regel von Hand: Spieler i prüft beide Ergänzungen seines Huts auf Codewort-Eigenschaft (Matrixprodukt mod 2)."""
    m = H.active_players(n)
    if i >= m:
        return PASS
    full = [list(others[:i]) + [b] + list(others[i:]) for b in (0, 1)]
    cw = [is_codeword(f[:m], m) for f in full]
    if cw[0] and not cw[1]:
        return 1
    if cw[1] and not cw[0]:
        return 0
    return PASS


def scalar_wins(n, decide):
    wins = 0
    for r in range(1 << n):
        bits = [(r >> i) & 1 for i in range(n)]
        acts = [decide(i, tuple(bits[j] for j in range(n) if j != i)) for i in range(n)]
        guesses = [(a, b) for a, b in zip(acts, bits) if a != PASS]
        wins += bool(guesses) and all(a == b for a, b in guesses)
    return wins


@pytest.mark.parametrize("n", range(2, 9))
def test_code_strategy_equals_the_scalar_matrix_rule_for_every_hat_distribution(n):
    actions = H.strategy_actions(n, C.HAT_CODE)
    for r in range(1 << n):
        bits = [(r >> i) & 1 for i in range(n)]
        for i in range(n):
            assert actions[r, i] == hamming_decision(n, i, tuple(bits[j] for j in range(n) if j != i)), (n, r, i)


def test_code_strategy_win_counts_and_perfection():
    expected = {2: 2, 3: 6, 4: 12, 5: 24, 6: 48, 7: 112, 8: 224}
    for n, wins in expected.items():
        assert scalar_wins(n, lambda i, o, n=n: hamming_decision(n, i, o)) == wins, n
    for m in (3, 7):
        codewords = [v for v in itertools.product((0, 1), repeat=m) if is_codeword(v, m)]
        assert len(codewords) == 2 ** (m - m.bit_length())
        # perfekt: jedes Nicht-Codewort hat genau ein Codewort im Abstand 1
        for v in itertools.product((0, 1), repeat=m):
            if v not in codewords:
                assert sum(1 for c in codewords if sum(a != b for a, b in zip(v, c)) == 1) == 1


def decode_strategy(index):
    """Strategie-Nummer der Aufzählung für drei Spieler → Tabellen: Ziffer 4·i + Sicht (zur Basis 3) ist die Aktion des Spielers i bei der Sicht = erster sichtbarer Hut + 2 · zweiter."""
    digits = [(index // 3 ** k) % 3 for k in range(12)]
    return [digits[4 * i: 4 * i + 4] for i in range(3)]


def scalar_wins_of_tables(tables):
    def decide(i, others):
        return tables[i][others[0] + 2 * others[1]]
    return scalar_wins(3, decide)


def test_three_players_every_sampled_strategy_matches_and_nothing_beats_six():
    r = H.enumerate_all_strategies_n3()
    rng = random.Random(5)
    best_indices = np.flatnonzero(r["wins"] == 6).tolist()
    sample = [rng.randrange(r["total"]) for _ in range(1500)] + best_indices
    for idx in sample:
        assert scalar_wins_of_tables(decode_strategy(idx)) == int(r["wins"][idx]), idx
    assert len(best_indices) == 4 and max(scalar_wins_of_tables(decode_strategy(i)) for i in best_indices) == 6
    assert int(r["wins"].max()) == 6                     # die vollständige Aufzählung: keine Strategie gewinnt mehr als 6 von 8


def test_cpsat_strategy_model_gives_the_stored_optimum():
    pytest.importorskip("ortools")
    stored = H.load_optimum()
    for n in range(2, 6):
        res = G.solve_best(G.complete_graph(n), 60.0)
        assert res["status"] == "OPTIMAL", n
        assert res["wins"] == H.wins_of_losing_set(stored[n], n), n


def test_highs_covering_model_gives_the_stored_sizes():
    scipy_opt = pytest.importorskip("scipy.optimize")
    sparse = pytest.importorskip("scipy.sparse")
    for n in range(2, 8):
        size = 1 << n
        a = sparse.lil_matrix((size, size))
        for v in range(size):
            a[v, v] = 1
            for j in range(n):
                a[v, v ^ (1 << j)] = 1
        res = scipy_opt.milp(c=np.ones(size), constraints=scipy_opt.LinearConstraint(a.tocsr(), lb=np.ones(size)), integrality=np.ones(size), bounds=scipy_opt.Bounds(0, 1))
        assert res.status == 0
        assert int(round(res.fun)) == int(H.load_optimum()[n].sum()), n


def test_brute_force_smallest_dominating_set_for_up_to_four_players():
    for n, expected in ((2, 2), (3, 2), (4, 4)):
        size = 1 << n
        found = None
        for k in range(1, size + 1):
            for d in itertools.combinations(range(size), k):
                s = set(d)
                if all(v in s or any(v ^ (1 << j) in s for j in range(n)) for v in range(size)):
                    found = k
                    break
            if found:
                break
        assert found == expected and int(H.load_optimum()[n].sum()) == expected, n


def test_counting_bound_is_never_exceeded_by_the_tables():
    for row in V.hat_table():
        assert row["code"] <= row["best"] <= row["bound"], row


# --- Reihe ------------------------------------------------------------------------------------------------------------------------------------
def line_strategy_values(n, q):
    """ALLE Strategien: Person k hat als Eingabe die Hüte vor ihr und die gehörten Tipps und liefert eine Farbe. Rückgabe: bester schlechtester Fall, bestes Mittel."""
    contexts = [list(itertools.product(range(q), repeat=n - 1)) for _ in range(n)]       # Länge (n − 1 − k) + k = n − 1 für jede Person
    functions = [list(itertools.product(range(q), repeat=len(c))) for c in contexts]
    lookup = [{c: i for i, c in enumerate(cs)} for cs in contexts]
    configs = list(itertools.product(range(q), repeat=n))
    best_worst, best_mean = -1, -1.0
    for choice in itertools.product(*[range(len(f)) for f in functions]):
        worst, total = n, 0
        for hats in configs:
            spoken = []
            right = 0
            for k in range(n):
                tip = functions[k][choice[k]][lookup[k][tuple(hats[k + 1:]) + tuple(spoken)]]
                spoken.append(tip)
                right += tip == hats[k]
            worst = min(worst, right)
            total += right
        best_worst, best_mean = max(best_worst, worst), max(best_mean, total / len(configs))
    return best_worst, best_mean


@pytest.mark.parametrize("n,q", [(2, 2), (3, 2), (2, 3)])
def test_no_line_strategy_beats_the_sum_announcement(n, q):
    worst, mean = line_strategy_values(n, q)
    assert worst == n - 1 and mean == pytest.approx(n - 1 + 1 / q)
    hats = L.all_hats(n, q)
    saved = L.saved_counts(hats, L.play_line_batch(hats, q))
    assert saved.min() == worst and saved.mean() == pytest.approx(mean)           # die Summen-Ansage erreicht beides


# --- Summen-Hüte ------------------------------------------------------------------------------------------------------------------------------
def best_sum_strategy_wins(n, q):
    views = list(itertools.product(range(q), repeat=n - 1))
    functions = list(itertools.product(range(q), repeat=len(views)))
    configs = list(itertools.product(range(q), repeat=n))
    view_idx = [[views.index(tuple(h[j] for j in range(n) if j != i)) for h in configs] for i in range(n)]
    best = 0
    for choice in itertools.product(range(len(functions)), repeat=n):
        wins = sum(1 for c, h in enumerate(configs) if any(functions[choice[i]][view_idx[i][c]] == h[i] for i in range(n)))
        best = max(best, wins)
    return best, len(configs)


@pytest.mark.parametrize("n,q", [(2, 2), (2, 3), (3, 2), (1, 2), (1, 3), (2, 4)])
def test_no_strategy_beats_the_bound_min_one_n_over_q(n, q):
    best, total = best_sum_strategy_wins(n, q)
    assert best == min(total, total * n // q) and best / total == pytest.approx(min(1.0, n / q))
    assert S.analyse_sums(n, q)["wins"] == best                         # die Summen-Strategie erreicht das Optimum


# --- Schachbrett ------------------------------------------------------------------------------------------------------------------------------
def scalar_code(board):
    x = 0
    for field, coin in enumerate(board):
        if coin:
            x ^= field
    return x


@pytest.mark.parametrize("n_fields", [2, 4, 8])
def test_scalar_exhaustive_check_agrees(n_fields):
    for bits in range(1 << n_fields):
        board = [(bits >> i) & 1 for i in range(n_fields)]
        for key in range(n_fields):
            flip = scalar_code(board) ^ key
            new = list(board)
            new[flip] ^= 1
            assert scalar_code(new) == key
    assert B.check_all(n_fields)["failures"] == 0


def test_sixteen_fields_exhaustive_in_the_module():
    r = B.check_all(16)
    assert r == {"cases": 16 * 65536, "failures": 0}


def perfect_colouring_exists(n_fields):
    cp_model = pytest.importorskip("ortools.sat.python.cp_model")
    size = 1 << n_fields
    m = cp_model.CpModel()
    c = [[m.NewBoolVar(f"c{v}_{k}") for k in range(n_fields)] for v in range(size)]
    for v in range(size):
        m.AddExactlyOne(c[v])
        for k in range(n_fields):
            m.AddExactlyOne([c[v ^ (1 << j)][k] for j in range(n_fields)])
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60
    solver.parameters.num_workers = 1
    status = solver.Solve(m)
    assert solver.StatusName(status) in ("OPTIMAL", "INFEASIBLE"), n_fields
    return solver.StatusName(status) == "OPTIMAL"


def test_perfect_strategy_exists_exactly_for_powers_of_two_up_to_seven():
    exists = {n: perfect_colouring_exists(n) for n in range(2, 8)}
    assert exists == {2: True, 3: False, 4: True, 5: False, 6: False, 7: False}
    assert {n: B.is_power_of_two(n) for n in range(2, 8)} == exists
    assert B.count_perfect_colorings(3) == 0 and B.count_perfect_colorings(2) == 4


# --- Sichtgraph -------------------------------------------------------------------------------------------------------------------------------
def scalar_graph_best(nbrs):
    """Beste Gewinnzahl über alle Strategien in Schleifenfassung (nur für wenige Strategien)."""
    n = len(nbrs)
    tables_per_player = [list(itertools.product((0, 1, PASS), repeat=1 << len(nb))) for nb in nbrs]
    best = 0
    for choice in itertools.product(*tables_per_player):
        wins = 0
        for r in range(1 << n):
            bits = [(r >> i) & 1 for i in range(n)]
            acts = [choice[i][sum(bits[j] << k for k, j in enumerate(nbrs[i]))] for i in range(n)]
            guesses = [(a, b) for a, b in zip(acts, bits) if a != PASS]
            wins += bool(guesses) and all(a == b for a, b in guesses)
        best = max(best, wins)
    return best


@pytest.mark.parametrize("kind,n,expected,loops", [("Jeder sieht jeden", 3, 6, False), ("Ring", 3, 6, False), ("Kette", 3, 4, True), ("Stern", 3, 4, True)])
def test_graph_enumeration_in_loops_vectorised_and_solver_agree_for_three_players(kind, n, expected, loops):
    """Die Schleifenfassung läuft nur dort, wo es wenige Strategien gibt (Kette und Stern: 6 561); beim Dreieck (531 441 Strategien) zählt die vektorisierte Aufzählung."""
    nbrs = G.make_graph(kind, n, C.GRAPH_KINDS)
    if loops:
        assert G.strategy_count(nbrs) == 6561 and scalar_graph_best(nbrs) == expected
    assert G.enumerate_best(nbrs) == expected
    pytest.importorskip("ortools")
    assert G.solve_best(nbrs, 30.0)["wins"] == expected


def test_vectorised_enumeration_and_solver_agree_for_the_four_player_chain():
    nbrs = G.chain_graph(4)
    assert G.strategy_count(nbrs) == 531441
    best = G.enumerate_best(nbrs)
    assert best == 8
    pytest.importorskip("ortools")
    res = G.solve_best(nbrs, 30.0)
    assert res["status"] == "OPTIMAL" and res["wins"] == best


def test_hat_game_is_the_complete_graph():
    """Der Sichtgraph „Jeder sieht jeden“ ist das Spiel aus cod_hats: die beste Strategie des Moduls, als Tabellen gespielt, gewinnt so oft wie gezählt."""
    n = 4
    nbrs = G.complete_graph(n)
    configs = H.all_configs(n)
    actions = H.strategy_actions(n, C.HAT_CODE)
    # Tabelle je Spieler aus den Aktionen lesen (Sicht → Aktion) und wieder anwenden
    tables = []
    for i in range(n):
        table = np.full(1 << (n - 1), PASS, dtype=np.uint8)
        views = G.view_index(configs, nbrs[i])
        table[views] = actions[:, i]
        tables.append(table)
    again = G.actions_from_tables(tables, nbrs, configs)
    assert (again == actions).all() and int(G.win_flags(again, configs).sum()) == 12
