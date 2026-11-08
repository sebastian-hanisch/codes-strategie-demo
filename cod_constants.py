"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets.

Rechenaufwand am Slider-Maximum (DEMO-PLAYBOOK §1c):
* Hüte gleichzeitig: 2^n Hutverteilungen mal n Spieler, bei n = 8 also 2 048 Entscheidungen, O(n · 2^n).
* Hüte in der Reihe: q^n Verteilungen; bis ENUM_LIMIT wird alles aufgezählt (n · q^n Operationen), darüber werden SAMPLES Zufallsverteilungen gezogen.
* Summen-Hüte: q^n Verteilungen mal n Spieler, am Maximum (q = 6, n = 7) 6^7 = 279 936 Zeilen mal 7 Spalten.
* Schachbrett: Zeichnung und Szene O(N); die vollständige Prüfung aller 2^N Bretter mal N Schlüsselfelder läuft nur für N ≤ EXHAUSTIVE_MAX_N (16: 1 048 576 Fälle).
* E1 (alle Strategien für drei Hüte): 3^12 = 531 441 Strategien mal 8 Hutverteilungen.
* E2 (Sichtgraph): ein ganzzahliges Modell mit höchstens 5 · 2^4 · 3 Aktionsvariablen und 2^5 Gewinnvariablen, feste Zeitgrenze, ein Arbeitsthread."""

# --- Regler ---------------------------------------------------------------------------------------------------------------------------------
N_HUT_MIN, N_HUT_MAX, DEFAULT_N_HUT = 2, 8, 3          # Hüte gleichzeitig: Zahl der Spieler (2 Farben)
N_REIHE_MIN, N_REIHE_MAX, DEFAULT_N_REIHE = 2, 12, 6   # Hüte in der Reihe: Zahl der Personen
Q_REIHE_MIN, Q_REIHE_MAX, DEFAULT_Q_REIHE = 2, 6, 2    # Zahl der Farben in der Reihe
Q_SUMME_MIN, Q_SUMME_MAX, DEFAULT_Q_SUMME = 2, 6, 3    # Summen-Hüte: Zahl der Farben
N_SUMME_MIN, N_SUMME_MAX, DEFAULT_N_SUMME = 1, 7, 3    # Summen-Hüte: Zahl der Spieler
M_BRETT_MIN, M_BRETT_MAX, DEFAULT_M_BRETT = 1, 6, 3    # Schachbrett: N = 2^m Felder (2 bis 64)
SEED_MAX, DEFAULT_SEED = 999_999, 35

HAT_STRATEGIES = (
    "Code-Strategie (Summe der Positionen)",
    "Beste Strategie (Überdeckungscode, vorgerechnet)",
    "Nur Spieler 1 rät, die anderen passen",
    "Alle raten »0«",
)
HAT_CODE, HAT_BEST, HAT_ONE, HAT_ALL = HAT_STRATEGIES
DEFAULT_HAT_STRATEGY = HAT_CODE

# --- feste Annahmen -------------------------------------------------------------------------------------------------------------------------
ENUM_LIMIT = 100_000              # Reihe: bis zu so vielen Hutverteilungen wird alles aufgezählt
SAMPLES = 5_000                   # sonst so viele Zufallsverteilungen (fester Zufalls-Seed)
EXHAUSTIVE_MAX_N = 16             # Schachbrett: bis zu dieser Feldzahl werden alle Bretter und alle Schlüsselfelder geprüft
BOARD_SAMPLE_N = 64               # darüber: Zufallsbretter (Stichprobe, keine vollständige Prüfung)
BOARD_SAMPLES = 20_000
HAT_OPTIMUM_MAX_N = 8             # vorgerechnete Überdeckungscodes (data/huete_optimum.json)
GRAPH_N_MIN, GRAPH_N_MAX, DEFAULT_GRAPH_N = 3, 5, 4        # E2: Zahl der Spieler im Sichtgraphen
GRAPH_KINDS = ("Jeder sieht jeden", "Ring", "Kette", "Stern")
DEFAULT_GRAPH_KIND = GRAPH_KINDS[0]
SOLVER_SECONDS = 20.0             # Zeitgrenze des ganzzahligen Modells in E2

# --- Farben ---------------------------------------------------------------------------------------------------------------------------------
COLOR_WIN = "#2F6B65"
COLOR_LOSE_WRONG = "#C0392B"
COLOR_LOSE_SILENT = "rgba(150,150,150,0.65)"
COLOR_LINE = "#4c78a8"
COLOR_BASELINE = "rgba(150,150,150,0.75)"
HAT_COLORS = ("#d95f02", "#1b9e77", "#7570b3", "#e6ab02", "#e7298a", "#66a61e")   # bis zu 6 Hutfarben
HAT_COLOR_NAMES = ("Orange", "Grün", "Violett", "Gelb", "Pink", "Hellgrün")

# --- Presets: jedes setzt alle Regler -------------------------------------------------------------------------------------------------------
_BASE = {"n_hut": DEFAULT_N_HUT, "hat_strategy": DEFAULT_HAT_STRATEGY, "n_reihe": DEFAULT_N_REIHE, "q_reihe": DEFAULT_Q_REIHE,
         "q_summe": DEFAULT_Q_SUMME, "n_summe": DEFAULT_N_SUMME, "m_brett": DEFAULT_M_BRETT, "seed": DEFAULT_SEED}

PRESETS = {
    "Standardfall (Voreinstellung)": dict(_BASE),
    "Sieben Hüte: Hamming-Code": dict(_BASE, n_hut=7),
    "Fünf Hüte: besser als der Code": dict(_BASE, n_hut=5, hat_strategy=HAT_BEST),
    "Lange Reihe, viele Farben": dict(_BASE, n_reihe=12, q_reihe=4),
    "Zu wenige Spieler für alle Farben": dict(_BASE, q_summe=5, n_summe=3),
    "Das ganze Schachbrett (64 Felder)": dict(_BASE, m_brett=6),
}
PRESET_HELP = {
    "Standardfall (Voreinstellung)": "Die kleinsten Fassungen: drei Hüte, eine Reihe von sechs Personen mit zwei Farben, drei Spieler mit drei Farben, ein Brett mit acht Feldern.",
    "Sieben Hüte: Hamming-Code": "Sieben Spieler, zwei Farben, Code-Strategie: Die Hutverteilungen, die der Hamming-Code als Codewörter führt, sind die einzigen, bei denen das Team verliert.",
    "Fünf Hüte: besser als der Code": "Fünf Spieler: Die Code-Strategie nutzt nur drei von ihnen; die vorgerechnete beste Strategie (Überdeckungscode) gewinnt in mehr Fällen.",
    "Lange Reihe, viele Farben": "Zwölf Personen in einer Reihe, vier Farben: Die Ansage der Summe rettet alle bis auf die erste Person sicher.",
    "Zu wenige Spieler für alle Farben": "Drei Spieler, fünf Farben: Ein garantierter Treffer ist nicht möglich, der Gewinnanteil ist höchstens Spieler durch Farben.",
    "Das ganze Schachbrett (64 Felder)": "64 Felder: Ein umgedrehtes Feld überträgt sechs Bit, genug für jedes der 64 Schlüsselfelder.",
}
