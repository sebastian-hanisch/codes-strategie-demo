"""Codes als Strategie: Hüte, Summen und das Schachbrett - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 2 der Reihe Teamrätsel. Vier Rätsel mit demselben Trick (eine Summe modulo q, bei zwei Farben XOR): Hüte gleichzeitig (raten oder passen), Hüte in einer Reihe,
Summen-Hüte und das Schachbrett mit den 64 Münzen. Lauffähig mit: streamlit run app.py
"""

import pandas as pd
import streamlit as st

import cod_board as B
import cod_constants as C
import cod_evaluation as V
import cod_experiments as XP
import cod_line as L
import cod_sums as S
import cod_visualization as Z
from cod_layout import dunkles_design, kopf_css
from cod_pdf_export import build_pdf
from cod_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)

st.set_page_config(page_title="Codes als Strategie – Sebastian Hanisch", layout="wide")


# --- Zwischenspeicher (Schlüssel = alle Eingaben inklusive Zufalls-Seed) --------------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def _hats(n, strategy, seed):
    return V.analyse_hats(n, strategy, seed)


@st.cache_data(show_spinner=False)
def _hat_table():
    return V.hat_table()


@st.cache_data(show_spinner=False)
def _line(n, q, seed):
    return V.analyse_line(n, q, seed)


@st.cache_data(show_spinner=False)
def _sums(n, q, seed):
    return V.analyse_sums(n, q, seed)


@st.cache_data(show_spinner=False)
def _board(m, seed):
    return V.analyse_board(m, seed)


@st.cache_data(show_spinner=False)
def _e1():
    return XP.e1_all_strategies()


@st.cache_data(show_spinner=False)
def _e2(kind, n):
    return XP.e2_graph(kind, n)


@st.cache_data(show_spinner=False)
def _e3():
    return XP.e3_colorings()


def show(verdict):
    kind, text = verdict
    getattr(st, kind)(text)


def signed(x, nd=1):
    """Differenz „mein Wert minus Referenz“ mit Vorzeichen und Dezimalkomma."""
    text = V.de(x, nd)
    return text if x <= 0 or text.startswith("-") else "+" + text


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in cod_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Codes als Strategie: Hüte, Summen und das Schachbrett")
st.markdown(
    """
**Stück 2 der Reihe Teamrätsel.** Ein Team darf **vorher eine Strategie absprechen**, danach nicht mehr miteinander reden. Vier bekannte Rätsel, **ein Trick**: Das Team verabredet eine
**Prüfsumme** (eine Summe modulo q, bei zwei Farben das XOR), und jedes Mitglied rechnet aus dem, was es sieht, den einen Wert für das Unsichtbare aus, der zu seiner Zielsumme passt.
Die Frage ist jeweils: **Was bringt die Absprache gegenüber dem Raten, wo liegt eine bewiesene Grenze, und wer muss wen sehen?**

Die Rätsel sind **Lehrbuchwissen**; eigen ist hier der Vergleich der vier Kulissen und dass jede Zahl ausgezählt oder bewiesen ist (ausgenommen die ausdrücklich genannten Stichproben: 64-Felder-Brett, lange Reihen; die Aufzählung aller Strategien, das ganzzahlige Modell und die Zählargumente sind Aufzählung, Löser bzw. Beweis). Abgrenzung: Die Reihe Koordinationsspiele
(`koordinationsspiel-demo` u. a.) fragt nach Eigennutz und Gleichgewichten, hier haben alle **dasselbe Ziel** und es geht um Strategie bei begrenzter Information. **Modelle**: gleichverteilte Hutfarben,
Absprache vorab, keine Verständigung währenddessen; keine Aussage über Menschen.

Weiter unten: die Abschnitte **🔬 Experimente**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert der Trick: vier Kulissen, eine Idee", expanded=True):
    st.markdown(
        """
1. **Abgesprochen wird eine Prüfsumme.** Ein Hut hat eine Farbe 0 … q − 1; auf dem Schachbrett ist die Prüfsumme das XOR der Feldnummern aller Münzen mit Kopf. Das Team legt fest,
   welche Zielsumme zu welcher Person gehört.
2. **Jeder rechnet seinen einen Wert aus.** Wer alle anderen sieht, kennt die Summe der übrigen und kann ausrechnen, welchen Wert *er* haben müsste, damit die Gesamtsumme seine Zielsumme ist.
3. **Der Gewinn kommt aus dem Zusammenspiel, nicht aus dem Einzelnen.** Ohne Absprache wäre jeder Tipp nur mit der Wahrscheinlichkeit 1/q richtig; die Strategie bündelt die Fehler auf wenige Verteilungen (gleichzeitig) oder auf eine Person (Reihe).

| Kulisse | Prüfsumme | Wer rechnet | Ergebnis |
|---|---|---|---|
| 🎩 Hüte gleichzeitig | Syndrom des Hamming-Codes (XOR der Positionen) | jeder Spieler, rät oder passt | Code-Strategie: Team verliert nur auf den Codewörtern |
| 🧍 Hüte in der Reihe | Summe aller Hüte modulo q, vom ersten angesagt | jede Person nach dem Hören | alle außer der ersten sicher richtig |
| ➕ Summen-Hüte | Summe aller Hüte modulo q | jeder Spieler, alle raten | mit q Spielern genau ein Tipp richtig |
| ♟️ Schachbrett | XOR der Felder mit Kopf | ein Gefangener dreht, der andere liest | ein umgedrehtes Feld = log₂ N Bit |
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("🎩 Hüte gleichzeitig")
    n_hut = st.slider("Spieler n", *bounds("n_hut_slider"), key="n_hut_slider", help="Wie viele Spieler mit je einem schwarzen oder weißen Hut (zwei Farben).")
    hat_strategy = st.selectbox("Strategie", C.HAT_STRATEGIES, key="hat_strategy_select",
                                help="Die Code-Strategie nutzt den Hamming-Code der größten Länge 2^r − 1 ≤ n; die beste Strategie stammt aus einem ganzzahligen Modell (vorgerechnet).")
    st.header("🧍 Hüte in der Reihe")
    n_reihe = st.slider("Personen n", *bounds("n_reihe_slider"), key="n_reihe_slider", help="Wie viele Personen hintereinander stehen.")
    q_reihe = st.slider("Farben q", *bounds("q_reihe_slider"), key="q_reihe_slider", help="Wie viele Hutfarben es gibt.")
    st.header("➕ Summen-Hüte")
    q_summe = st.slider("Farben q", *bounds("q_summe_slider"), key="q_summe_slider", help="Wie viele Hutfarben es gibt.")
    n_summe = st.slider("Spieler n", *bounds("n_summe_slider"), key="n_summe_slider", help="Wie viele Spieler gleichzeitig tippen. Gewonnen ist, wenn mindestens ein Tipp stimmt.")
    st.header("♟️ Schachbrett")
    m_brett = st.slider("Bit m (Felder N = 2^m)", *bounds("m_brett_slider"), key="m_brett_slider", help="Das Brett hat N = 2^m Felder; ein umgedrehtes Feld überträgt m Bit.")
    st.caption(f"Das Brett hat {1 << int(m_brett)} Felder.")
    st.header("🎲 Zufall")
    seed = st.number_input("Zufalls-Seed der Szenen", *bounds("seed_input"), key="seed_input", step=1,
                           help="Bestimmt die gezogenen Hutverteilungen und das Brett in den Szenen. Die Zahlen der Auswertungen hängen davon nicht ab.")
    st.button("🎲 Neue Szenen ziehen", width="stretch", on_click=randomize_seed)

sync_query_params({"n_hut_slider": int(n_hut), "hat_strategy_select": hat_strategy, "n_reihe_slider": int(n_reihe), "q_reihe_slider": int(q_reihe), "q_summe_slider": int(q_summe),
                   "n_summe_slider": int(n_summe), "m_brett_slider": int(m_brett), "seed_input": int(seed)})
settings = V.Settings(int(n_hut), hat_strategy, int(n_reihe), int(q_reihe), int(q_summe), int(n_summe), int(m_brett), int(seed))
verdicts_for_pdf = []

# --- a) Hüte gleichzeitig ------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎩 Hüte gleichzeitig: raten oder passen")
st.markdown(
    f"""
**{settings.n_hut} Spieler**, jeder mit einem Hut in einer von **zwei Farben (0 oder 1)**, gleichverteilt und unabhängig. Jeder sieht die Hüte der anderen, nicht den eigenen. Auf ein Zeichen sagt jeder
gleichzeitig „0“, „1“ oder „passe“. **Gewonnen** ist, wenn **mindestens einer rät und alle, die raten, richtig liegen**. Ein einzelner Rater gewinnt in der Hälfte der Fälle; die Frage ist, ob das Team
mit Absprache mehr schafft. Gewählt: **{settings.hat_strategy}**.
"""
)
ha = _hats(settings.n_hut, settings.hat_strategy, settings.seed)
c1, c2, c3 = st.columns(3)
c1.metric("Gewinnanteil der Strategie", V.pct(ha.share), delta=f"{signed(100 * (ha.share - ha.optimum_wins / ha.total))} Prozentpunkte gegen die beste Strategie")
c2.metric("Beste Strategie (ganzzahliges Modell)", V.pct(ha.optimum_wins / ha.total), delta=f"{ha.optimum_wins} von {ha.total}", delta_color="off")
c3.metric("Obergrenze jeder Strategie", V.pct(ha.bound_wins / ha.total), delta=f"{ha.bound_wins} von {ha.total} (Zählargument)", delta_color="off")
st.plotly_chart(Z.build_hat_grid(ha.classes, ha.n, ha.scene_index), width="stretch", key="hat_grid")
st.caption(f"Jede Zelle ist eine der {ha.total} Hutverteilungen (Hover zeigt die Hüte der Spieler 1 bis {ha.n}). Schwarz umrahmt: die Verteilung der Szene unten.")
st.markdown(f"**Szene: Verteilung Nr. {ha.scene_index} aus dem Zufalls-Seed.** " + ("Das Team **gewinnt**." if ha.scene_win else "Das Team **verliert**."))
st.dataframe(pd.DataFrame(ha.scene, columns=["Spieler", "Sieht (Hüte der anderen)", "Sagt", "Eigener Hut", "Tipp"]), hide_index=True, width="stretch")
kind, text = V.verdict_hats(ha)
st.markdown("#### ❓ Kernfrage: Wie viel bringt die Absprache gegenüber dem Raten?")
getattr(st, kind)(text)
verdicts_for_pdf.append(("Hüte gleichzeitig", text))

st.markdown("**Alle Spielerzahlen im Vergleich** (Aufzählung aller 2^n Hutverteilungen; die beste Strategie ist vorgerechnet, siehe `data/huete_optimum.json`)")
rows = _hat_table()
st.plotly_chart(Z.build_hat_table(rows), width="stretch", key="hat_table_chart")
st.dataframe(
    pd.DataFrame([{"n": r["n"], "Verteilungen": r["total"], "Obergrenze": r["bound"], "Code-Strategie": r["code"], "Beste Strategie": r["best"], "Spieler im Code": r["players_used"],
                   "Beste in %": 100 * r["best"] / r["total"]} for r in rows]),
    hide_index=True, width="stretch", column_config={"Beste in %": st.column_config.NumberColumn("Beste Strategie in %", format="%.1f %%")},
)
st.caption("Gewonnene Hutverteilungen je Spielerzahl. „Spieler im Code“: so viele Spieler nutzen den Hamming-Code, die übrigen passen immer. Bei n = 5 und n = 6 ist die beste Strategie besser als die Code-Strategie.")

st.markdown("---")

# --- b) Hüte in der Reihe ------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🧍 Hüte in einer Reihe: die Summe ansagen")
st.markdown(
    f"""
**{settings.n_reihe} Personen** stehen hintereinander, jede trägt einen Hut in einer von **{settings.q_reihe} Farben**. Jede sieht die Hüte **vor** sich, nicht den eigenen und nicht die dahinter.
Von hinten nach vorn nennt jede laut eine Farbe als Tipp für den **eigenen** Hut; alle hören alle Tipps, erfahren aber nicht, ob einer stimmte. **Die erste Person** (ganz hinten) sagt die **Summe modulo q**
der Hüte vor ihr an; jede weitere kennt diese Summe, sieht die Hüte vor sich und hat die Tipps der Vorgänger gehört, und kann ihre eigene Farbe daraus ausrechnen.
"""
)
la = _line(settings.n_reihe, settings.q_reihe, settings.seed)
c1, c2, c3 = st.columns(3)
c1.metric("Mindestens richtig (schlechtester Fall)", f"{la.min_saved} von {la.n}", delta=f"n − 1 = {la.n - 1} bewiesen", delta_color="off")
c2.metric("Im Mittel richtig", V.de(la.mean_saved, 2), delta=f"{signed(la.mean_saved - la.chance_mean, 2)} gegen Raten ohne Plan")
c3.metric("Raten ohne Plan im Mittel", V.de(la.chance_mean, 2), delta="n / q", delta_color="off")
st.markdown("**Szene** (Zufalls-Seed): Farbe = Hut, ✔ / ✘ = Tipp der Person richtig oder falsch.")
st.plotly_chart(Z.build_line(la.hats, la.answers, la.q), width="stretch", key="line_scene")
st.caption("Farben: " + ", ".join(f"{i} = {name}" for i, name in enumerate(C.HAT_COLOR_NAMES[: la.q])) + f". Person 1 sagt die Summe der anderen {la.n - 1} Hüte modulo {la.q} an und liegt nur zufällig richtig.")
st.markdown("**Verteilung der richtigen Tipps** (" + V.line_scope_text(la.cases, la.exhaustive, la.n, la.q) + ")")
st.plotly_chart(Z.build_count_distribution(la.counts, L.binomial_distribution(la.n, la.q), "Zahl der richtigen Tipps in der Reihe"), width="stretch", key="line_dist")
kind, text = V.verdict_line(la)
st.markdown("#### ❓ Kernfrage: Wie viele lassen sich sicher retten?")
getattr(st, kind)(text)
verdicts_for_pdf.append(("Hüte in der Reihe", text))

st.markdown("---")

# --- c) Summen-Hüte ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## ➕ Summen-Hüte: genau einer liegt richtig")
st.markdown(
    f"""
**{settings.n_summe} Spieler**, jeder mit einem Hut in einer von **{settings.q_summe} Farben** (0 … {settings.q_summe - 1}). Alle tippen gleichzeitig auf die eigene Farbe; es gibt kein Passen.
**Gewonnen** ist, wenn mindestens ein Tipp stimmt. Verabredet wird: Spieler i bekommt die Zielsumme i modulo q und tippt so, dass die **Summe aller Hüte** seine Zielsumme ergäbe.
"""
)
sa = _sums(settings.n_summe, settings.q_summe, settings.seed)
c1, c2, c3 = st.columns(3)
c1.metric("Gewinnanteil der Summe", V.pct(sa.win_share), delta=f"{signed(100 * (sa.win_share - sa.chance_share))} Prozentpunkte gegen Raten ohne Plan")
c2.metric("Raten ohne Plan", V.pct(sa.chance_share), delta="1 − (1 − 1/q)^n", delta_color="off")
c3.metric("Obergrenze jeder Strategie", V.pct(sa.bound), delta="min(1, n/q)", delta_color="off")
st.markdown("**Verteilung der richtigen Tipps** (Aufzählung aller " + V.thousands(sa.total) + " Verteilungen)")
st.plotly_chart(Z.build_count_distribution(sa.counts, S.chance_distribution(sa.n, sa.q), "Zahl der richtigen Tipps"), width="stretch", key="sums_dist")
scene_rows = [(i + 1, i % sa.q, sum(sa.hats) - sa.hats[i], sa.tips[i], sa.hats[i], "richtig" if sa.tips[i] == sa.hats[i] else "falsch") for i in range(sa.n)]
st.markdown("**Szene** (Zufalls-Seed): Die Summe aller Hüte ist **" + str(sum(sa.hats)) + f"**, modulo {sa.q} also **{sum(sa.hats) % sa.q}**.")
st.dataframe(pd.DataFrame(scene_rows, columns=["Spieler", "Zielsumme", "Summe der anderen Hüte", "Tipp", "Eigener Hut", "Ergebnis"]), hide_index=True, width="stretch")
kind, text = V.verdict_sums(sa)
st.markdown("#### ❓ Kernfrage: Wie viele Spieler braucht man, damit ein Treffer sicher ist?")
getattr(st, kind)(text)
verdicts_for_pdf.append(("Summen-Hüte", text))

st.markdown("---")

# --- d) Schachbrett ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## ♟️ Das Schachbrett: ein Umdrehen überträgt log₂ N Bit")
ba = _board(settings.m_brett, settings.seed)
st.markdown(
    f"""
Auf **{ba.n_fields} Feldern** liegt je eine Münze (dunkel = Kopf, hell = Zahl). Gefangener A kennt das **Schlüsselfeld** (★) und **muss genau eine Münze umdrehen**; Gefangener B sieht nur das Brett
und muss das Schlüsselfeld nennen. Verabredet wird die Zahl **S = XOR der Nummern aller Felder mit Kopf**. A dreht das Feld **S ⊕ Schlüssel** um, danach ist S gleich dem Schlüssel.
"""
)
s_before = int(B.board_code(ba.board)[0])
width_bits = max(1, ba.m)
c1, c2, c3 = st.columns(3)
c1.metric("S vor dem Umdrehen", f"{s_before}", delta=f"binär {s_before:0{width_bits}b}", delta_color="off")
c2.metric("A dreht das Feld", f"{ba.flip}", delta=f"S ⊕ {ba.key} = {s_before} ⊕ {ba.key}", delta_color="off")
c3.metric("B liest ab", f"{ba.read}", delta=f"Schlüsselfeld war {ba.key}", delta_color="off")
col_a, col_b = st.columns(2)
col_a.plotly_chart(Z.build_board(ba.board, ba.key, ba.flip, "Vorher (A dreht das rot umrahmte Feld)"), width="stretch", key="board_before")
col_b.plotly_chart(Z.build_board(ba.after, ba.key, None, "Nachher (B liest S ab)"), width="stretch", key="board_after")
kind, text = V.verdict_board(ba)
st.markdown("#### ❓ Kernfrage: Reicht ein einziges umgedrehtes Feld für jedes Schlüsselfeld?")
getattr(st, kind)(text)
verdicts_for_pdf.append(("Schachbrett", text))
st.caption("Warum nur Zweierpotenzen: " + V.board_class_text(ba.n_fields) + " (Zählargument und Aufzählung in Experiment 3.)")

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Alle Strategien für drei Hüte")
st.markdown("Für drei Spieler ist jede Strategie eine Tabelle: je Spieler und jede der vier Sichten (zwei sichtbare Hüte) eine der Aktionen „0“, „1“, „passe“, das sind 3^12 Strategien. **Alle** werden gespielt.")
if st.button("▶️ Alle 531 441 Strategien durchrechnen", key="e1_button", help="3^12 Strategien mal 8 Hutverteilungen; rechnet wenige Sekunden."):
    st.session_state["e1_done"] = True
if st.session_state.get("e1_done"):
    with st.spinner("Rechne 531 441 Strategien (wenige Sekunden) …"):
        e1 = _e1()
    st.plotly_chart(Z.build_e1_histogram(e1["histogram"], e1["best"]), width="stretch", key="e1_chart")
    show(XP.verdict_e1(e1))

st.markdown("---")
st.subheader("🔬 Experiment 2: Wer sieht wen?")
st.markdown("Bisher sieht jeder jeden. Jetzt sieht jeder nur seine **Nachbarn** im Sichtgraphen. Das ganzzahlige Modell (CP-SAT) sucht die beste Strategie für diesen Graphen.")
g1, g2 = st.columns(2)
graph_kind = g1.selectbox("Sichtgraph", C.GRAPH_KINDS, key="graph_kind_select")
graph_n = g2.slider("Spieler im Graphen", C.GRAPH_N_MIN, C.GRAPH_N_MAX, C.DEFAULT_GRAPH_N, key="graph_n_slider")
if st.button("▶️ Beste Strategie für diesen Sichtgraphen suchen", key="e2_button", help=f"Ganzzahliges Modell mit Zeitgrenze {int(C.SOLVER_SECONDS)} Sekunden."):
    st.session_state["e2_signature"] = (graph_kind, int(graph_n))
if st.session_state.get("e2_signature") == (graph_kind, int(graph_n)):
    with st.spinner(f"Löse das Modell (höchstens {int(C.SOLVER_SECONDS)} Sekunden) …"):
        e2 = _e2(graph_kind, int(graph_n))
    show(XP.verdict_e2(e2))
    st.caption(f"{e2['edges']} Sichtverbindungen, {V.thousands(e2['n_strategies'])} Strategien im Graphen, Rechenzeit {V.de(e2['seconds'], 1)} s (ein Arbeitsthread).")

st.markdown("---")
st.subheader("🔬 Experiment 3: Gibt es auch Bretter mit 3 oder 6 Feldern?")
st.markdown("Eine perfekte Strategie färbt die 2^N Bretter mit N Farben so, dass unter den N Nachbarn jedes Bretts jede Farbe genau einmal vorkommt. **Gezählt wird durch Aufzählung aller Färbungen.**")
e3 = _e3()
show(XP.verdict_e3(e3))
st.dataframe(pd.DataFrame([{"Felder N": d["n_fields"], "2^N / N": d["quotient"], "ganzzahlig": "ja" if d["integer"] else "nein"} for d in e3["divisibility"]]), hide_index=True, width="stretch",
             column_config={"2^N / N": st.column_config.NumberColumn("2^N / N", format="%.1f")})

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Hutfarben gleichverteilt und unabhängig** | Die Gewinnanteile gelten für diese Verteilung. Bei anderer Verteilung (z. B. ein Hut viel wahrscheinlicher) kann „alle raten die häufige Farbe“ besser sein als jeder Code; nicht gerechnet. | – |
| **Absprache vorab, nichts währenddessen** | Wer sich währenddessen verständigen darf, spielt ein anderes Rätsel; die Reihe nutzt gerade die laut gesprochenen Tipps als einzigen Kanal. | – |
| **Gewinn heißt: mindestens ein Rater, alle Rater richtig** | Bei anderer Gewinnregel (z. B. alle müssen raten und richtig liegen, nach dem Gedächtnis die Regel bei Riis, ungeprüft) ändern sich die Werte und der Graph-Teil; hier nicht gerechnet. | Literatur zu „guessing games“ |
| **Alle Mitglieder rechnen fehlerfrei und kennen dieselbe Verabredung** | Eine einzige falsche Rechnung macht in der Reihe alle Folgenden falsch (folgt aus der Formel, nicht gemessen). | – |
| **Zählschranke der Hüte (Obergrenze n/(n+1))** | Gilt für zwei Farben und gleichverteilte Hüte; die Zahl der Verteilungen ist bei n = 2, 3, 4 und 7 erreicht, bei n = 5, 6 und 8 liegt die beste Strategie darunter (Tabelle oben). | – |
| **Sichtgraph aus Experiment 2** | Nur für die gezeigten Graphen mit höchstens fünf Spielern gerechnet; eine allgemeine Aussage über Graphen ist das nicht. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben und gesucht.** Gegeben $n$ Spieler und eine verabredete Strategie; gesucht ist der Anteil der Hutverteilungen, die das Team gewinnt, und eine Obergrenze für jede Strategie.

| Symbol | Bedeutung |
|---|---|
| $n$, $q$ | Zahl der Spieler (Personen), Zahl der Farben |
| $h_i \in \{0,\dots,q-1\}$ | Hut von Spieler $i$ |
| $S=\sum_i h_i \bmod q$ | Prüfsumme aller Hüte |
| $m = 2^r-1$ | Länge des Hamming-Codes, $m \le n$ |
| $N = 2^m$ | Felder des Schachbretts (hier $m$ Bit, im Hut-Teil $m$ Spieler) |

**Hüte gleichzeitig, Obergrenze.** Bei gleichverteilten Hüten ist jeder Tipp mit Wahrscheinlichkeit $1/2$ richtig. Zählt man über alle $2^n$ Verteilungen, gibt es genauso viele richtige wie falsche Tipps. In einer gewonnenen
Verteilung gibt es mindestens einen richtigen und keinen falschen Tipp, in einer verlorenen höchstens $n$ falsche. Mit $W$ gewonnenen und $L$ verlorenen Verteilungen folgt

$$W \le \#\text{richtig} = \#\text{falsch} \le nL \quad\Rightarrow\quad \frac{W}{W+L} \le \frac{n}{n+1}.$$

**Hamming-Code.** Für $m = 2^r-1$ sei $s(x)=\bigoplus_{p:\,x_p=1} p$ das Syndrom. Die Codewörter sind die Verteilungen mit $s(x)=0$; sie sind $2^{m-r}$ von $2^m$. Spieler $p$ betrachtet die zwei Verteilungen, die zu dem passen, was er sieht (eigener Hut 0 oder 1). Ist eine davon ein Codewort, rät er die Farbe der anderen, sonst passt er. Auf jedem Nicht-Codewort $x$ rät genau der Spieler $p=s(x)$ und liegt richtig; auf Codewörtern liegen alle
Rater falsch. Das Team gewinnt also in $1-2^{-r}=m/(m+1)$ der Fälle, das ist die Obergrenze: der Code ist **perfekt**.

**Beste Strategie.** Das Team verliert genau auf einer Menge $D$ von Verteilungen; die Strategie funktioniert genau dann, wenn jede Verteilung in $D$ liegt oder einen Nachbarn (ein Hut anders) in $D$ hat, also $D$ eine
dominierende Menge des Würfelgraphen $Q_n$ ist (Überdeckungscode vom Radius 1). Die Gewinnzahl ist $2^n-|D|$; ein kleinstes $D$ ist ein ganzzahliges Modell (vorgerechnet).

**Reihe.** Person 1 sagt $a_1 = \sum_{j\ge 2} h_j \bmod q$. Person $k\ge 2$ kennt $a_1$, sieht $h_{k+1},\dots,h_n$ und hat $a_2,\dots,a_{k-1}$ gehört (die, wenn richtig, $h_2,\dots,h_{k-1}$ sind):

$$a_k = a_1 - \sum_{j>k} h_j - \sum_{j=2}^{k-1} a_j \bmod q.$$

Sind $a_2,\dots,a_{k-1}$ richtig, gilt $a_k = h_k$. Die erste Person ist für jede Sicht in genau einem von $q$ Fällen richtig. Für jede Sicht der ersten Person gibt es eine Farbe, bei der sie falsch liegt (schlechtester Fall höchstens $n-1$), und im Mittel liegt sie mit $1/q$ richtig (Mittel höchstens $n-1+1/q$); die Summe erreicht beides.

**Summen-Hüte.** Spieler $i$ tippt $g_i = (i - \sum_{j\ne i} h_j) \bmod q$, richtig genau dann, wenn $S \equiv i \pmod q$. Für $n \ge q$ gibt es zu jedem Rest einen Spieler, also mindestens einen Treffer. Für $n \le q$: Der Erwartungswert der Zahl richtiger
Tipps ist jeweils $n/q$ und der Gewinnanteil höchstens dieser Erwartungswert, also

$$P(\text{Gewinn}) \le \min\!\left(1,\ \frac{n}{q}\right);$$

die Summe erreicht das. Bei $n=q$ ist der Erwartungswert 1 und es gibt immer mindestens einen Treffer, also **genau einen**.

**Schachbrett.** Mit $S(b)=\bigoplus_{f:\,b_f=1} f$ gilt $S(b \oplus e_j) = S(b) \oplus j$ (Umdrehen von Feld $j$ ändert $S$ um $j$). A dreht $j=S(b)\oplus k$ und erhält $S = k$. Das geht für $N=2^m$, weil die Nummern $0,\dots,N-1$
genau die $m$-Bit-Zahlen sind. Notwendig: Eine perfekte Strategie färbt die $2^N$ Bretter mit $N$ Farben (Farbe = Gelesenes), und jedes Brett hat unter seinen $N$ Nachbarn jede Farbe genau einmal. Zählt man die Kanten zwischen einer Farbklasse $K$ und
allen Brettern, so hat jedes Brett genau einen Nachbarn in $K$ und jedes Brett aus $K$ genau $N$ Nachbarn:

$$|K| \cdot N = 2^N \quad\Rightarrow\quad N \mid 2^N,$$

das gilt genau für die Zweierpotenzen.

**Literatur.** Lenstra, Seroussi: *On Hats and other Covers* (arXiv cs/0509045, 2005): Bei zwei Farben entsprechen die Strategien dem Überdeckungscode vom Radius 1; der Zusammenhang mit Hamming-Codes
für $n=2^m-1$ war schon vorher bekannt (laut Zusammenfassung). Riis: *Information flows, graphs and their guessing numbers* (Electronic Journal of Combinatorics 14, 2007, R44): Rateaufgaben auf Graphen (nur Titel und Angabe geprüft; die
Gewinnregel dort ist aus dem Gedächtnis und ungeprüft). Die Hüte in der Reihe, die Summen-Hüte und das Schachbrett gelten als Sammlungswissen ohne einzelne Quelle (ungeprüft).
        """
    )

st.markdown("---")

st.subheader("📄 Ergebnisse als PDF")
if st.button("PDF erstellen", key="pdf_button"):
    st.session_state["pdf_bytes"] = build_pdf(settings, verdicts_for_pdf)
if st.session_state.get("pdf_bytes"):
    st.download_button("⬇️ PDF herunterladen", st.session_state["pdf_bytes"], file_name="codes-strategie.pdf", mime="application/pdf", key="pdf_download")

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
