"""Gemeinsame Fixtures: Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def hamming3_losing():
    """Hutverteilungen für n = 3 als Nummer r (Spieler i hat das Bit i). Handrechnung: Syndrom = XOR der Positionen (Spieler + 1) mit Hut 1; null nur für 000 (r = 0) und 111 (r = 7), da 1 ^ 2 ^ 3 = 0."""
    return {0, 7}


@pytest.fixture
def hand_hats3():
    """Von Hand durchgespielte Fälle n = 3 mit der Code-Strategie: (r, Aktionen der Spieler 1 bis 3 mit 2 = passt).
    r = 1 (Hüte 1,0,0): Syndrom 1; Spieler 1 sieht Syndrom 0 der anderen und rät 1 (richtig), Spieler 2 und 3 sehen 1 ≠ 2, 3 und passen.
    r = 3 (Hüte 1,1,0): Syndrom 3; nur Spieler 3 sieht 3 = seine Position und rät 0 (richtig).
    r = 0 (Hüte 0,0,0): Codewort, alle sehen Syndrom 0 und raten 1: alle falsch."""
    return {1: (1, 2, 2), 3: (2, 2, 0), 0: (1, 1, 1)}
