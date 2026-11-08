"""PDF-Export (fpdf2, Kernschriften): Einstellungen, Kennzahlen und die Verdikte der vier Kulissen. Erst nach Klick erzeugt (DEMO-PLAYBOOK §1c)."""

from __future__ import annotations

from fpdf import FPDF

import cod_evaluation as V

_REPLACE = {"–": "-", "—": "-", "≤": "<=", "≥": ">=", "≠": "!=", "²": "2", "₂": "2", "⊕": "xor", "·": "*", "−": "-", "„": '"', "“": '"', "”": '"', "»": '"', "«": '"', "→": "->",
            "×": "x", "…": "...", "★": "*", "✔": "ok", "✘": "falsch", "‚": ",", "‘": "'", "’": "'", "⌊": "[", "⌋": "]", "Σ": "Summe", "½": "1/2"}


def _latin(text: str) -> str:
    """Kernschriften kennen nur Latin-1: Sonderzeichen ersetzen, Markdown-Sterne entfernen."""
    for a, b in _REPLACE.items():
        text = text.replace(a, b)
    return text.replace("**", "").replace("`", "").encode("latin-1", "replace").decode("latin-1")


def build_pdf(s: V.Settings, verdicts: list[tuple[str, str]]) -> bytes:
    """`verdicts` = Überschrift und Text je Kulisse (die Texte der Verdikt-Funktionen)."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _latin("Codes als Strategie: Hüte, Summen und das Schachbrett"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, _latin(
        f"Hüte gleichzeitig: {s.n_hut} Spieler, Strategie: {s.hat_strategy}. Hüte in der Reihe: {s.n_reihe} Personen, {s.q_reihe} Farben. Summen-Hüte: {s.n_summe} Spieler, "
        f"{s.q_summe} Farben. Schachbrett: {1 << s.m_brett} Felder. Zufalls-Seed {s.seed}."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    for heading, text in verdicts:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, _latin(heading), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, _latin(text), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _latin("Alle Zahlen sind eigene Rechnung: vollständige Aufzählung, wo angegeben, sonst Stichprobe. Die Rätsel sind Modelle mit festen Annahmen "
                                "(gleichverteilte Hutfarben, Absprache vorab, keine Verständigung während des Spiels), keine Aussagen über Menschen."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
