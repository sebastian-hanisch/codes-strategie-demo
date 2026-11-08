"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

import cod_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def grid_shape(count: int) -> tuple[int, int]:
    """Zeilen und Spalten für `count` Zellen (eine Zweierpotenz): möglichst quadratisch, Spalten ≥ Zeilen."""
    cols = 1
    while cols * cols < count:
        cols *= 2
    return count // cols, cols


def build_hat_grid(classes: np.ndarray, n: int, marked: int):
    """Alle 2^n Hutverteilungen als Gitter: grün gewonnen, rot verloren (ein Tipp falsch), grau verloren (niemand riet). Die gezogene Verteilung ist mit einem Rahmen markiert."""
    rows, cols = grid_shape(len(classes))
    z = classes.reshape(rows, cols)
    labels = np.array([[" ".join(str((r >> i) & 1) for i in range(n)) for r in range(row * cols, (row + 1) * cols)] for row in range(rows)])
    fig = go.Figure(go.Heatmap(
        z=z, text=labels, zmin=-0.5, zmax=2.5, xgap=2, ygap=2, showscale=True,
        colorscale=[[0, C.COLOR_WIN], [1 / 3, C.COLOR_WIN], [1 / 3, C.COLOR_LOSE_WRONG], [2 / 3, C.COLOR_LOSE_WRONG], [2 / 3, C.COLOR_LOSE_SILENT], [1, C.COLOR_LOSE_SILENT]],
        colorbar=dict(tickvals=[0, 1, 2], ticktext=["gewonnen", "ein Tipp falsch", "niemand riet"], len=0.9, thickness=14),
        hovertemplate="Hüte der Spieler 1 bis " + str(n) + ": %{text}<extra></extra>"))
    mr, mc = divmod(marked, cols)
    fig.add_shape(type="rect", x0=mc - 0.5, x1=mc + 0.5, y0=mr - 0.5, y1=mr + 0.5, line=dict(color="black", width=3))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, autorange="reversed")
    return _base(fig, height=max(200, 60 * rows + 60))


def build_hat_table(rows: list[dict]):
    """Gewinnanteil je Spielerzahl: Zählschranke, Code-Strategie, beste Strategie."""
    ns = [f"n = {r['n']}" for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ns, y=[100 * r["code"] / r["total"] for r in rows], name="Code-Strategie", marker_color=C.COLOR_WIN, hovertemplate="%{x}: %{y:.1f} %<extra></extra>"))
    fig.add_trace(go.Bar(x=ns, y=[100 * r["best"] / r["total"] for r in rows], name="Beste Strategie", marker_color=C.COLOR_LINE, hovertemplate="%{x}: %{y:.1f} %<extra></extra>"))
    fig.add_trace(go.Scatter(x=ns, y=[100 * r["bound"] / r["total"] for r in rows], mode="markers", name="Obergrenze (Zählargument)",
                             marker=dict(symbol="line-ew", size=22, line=dict(width=3, color="black")), hovertemplate="%{x}: %{y:.1f} %<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Gewinnanteil (%)", range=[0, 100])
    return _base(fig)


def build_line(hats: tuple, answers: tuple, q: int):
    """Die Reihe: Person 1 steht ganz hinten (links). Farbe = Hut; ✔ oder ✘ über der Person = der Tipp war richtig oder falsch."""
    n = len(hats)
    xs = list(range(1, n + 1))
    fig = go.Figure(go.Scatter(x=xs, y=[0] * n, mode="markers+text", marker=dict(size=34, color=[C.HAT_COLORS[h] for h in hats], line=dict(width=2, color="black")),
                               text=[str(h) for h in hats], textfont=dict(color="white", size=14), textposition="middle center",
                               customdata=[(a, "richtig" if a == h else "falsch") for a, h in zip(answers, hats)],
                               hovertemplate="Person %{x}: Hut %{text}, Tipp %{customdata[0]} (%{customdata[1]})<extra></extra>"))
    for x, a, h in zip(xs, answers, hats):
        fig.add_annotation(x=x, y=0.9, text="✔ " + str(a) if a == h else "✘ " + str(a), showarrow=False, font=dict(color=C.COLOR_WIN if a == h else C.COLOR_LOSE_WRONG, size=14))
    fig.update_xaxes(range=[0.4, n + 0.6], dtick=1, title_text="Person (1 = ganz hinten, sieht alle anderen; n = ganz vorn, sieht niemanden)")
    fig.update_yaxes(range=[-1, 1.6], visible=False)
    return _base(fig, height=230)


def build_count_distribution(counts: np.ndarray, chance: np.ndarray, x_title: str):
    """Anteil der Verteilungen je Trefferzahl: Strategie gegen Raten ohne Plan."""
    ks = list(range(len(counts)))
    share = 100.0 * counts / counts.sum()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ks, y=share, name="Strategie", marker_color=C.COLOR_WIN, hovertemplate="%{x} richtig: %{y:.1f} %<extra></extra>"))
    fig.add_trace(go.Bar(x=ks, y=100.0 * chance, name="Raten ohne Plan", marker_color=C.COLOR_BASELINE, hovertemplate="%{x} richtig: %{y:.1f} %<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(title_text=x_title, dtick=1)
    fig.update_yaxes(title_text="Anteil der Verteilungen (%)", range=[0, 105])
    return _base(fig)


def build_board(board: np.ndarray, key: int, flipped: int | None, title: str):
    """Das Brett als Gitter: dunkel = Kopf (1), hell = Zahl (0), Feldnummer klein darunter. Schlüsselfeld: Stern; umgedrehtes Feld: dicker Rahmen."""
    n_fields = len(board)
    rows, cols = grid_shape(n_fields)
    z = np.array(board, dtype=int).reshape(rows, cols)
    fig = go.Figure(go.Heatmap(z=z, zmin=0, zmax=1, xgap=3, ygap=3, showscale=False, colorscale=[[0, "#E8EEF0"], [1, C.COLOR_WIN]],
                               hovertemplate="Feld %{customdata}: %{text}<extra></extra>", customdata=np.arange(n_fields).reshape(rows, cols),
                               text=np.where(z == 1, "Kopf", "Zahl")))
    for f in range(n_fields):
        r, c = divmod(f, cols)
        fig.add_annotation(x=c, y=r, text=("★ " if f == key else "") + str(f), showarrow=False, font=dict(size=12, color="white" if board[f] else "#333"))
    if flipped is not None:
        r, c = divmod(flipped, cols)
        fig.add_shape(type="rect", x0=c - 0.5, x1=c + 0.5, y0=r - 0.5, y1=r + 0.5, line=dict(color="#C0392B", width=4))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, autorange="reversed", scaleanchor="x", scaleratio=1)
    fig.update_layout(title=dict(text=title, font=dict(size=14)))
    fig.update_layout(height=max(160, 55 * rows + 50), margin=dict(l=10, r=10, t=40, b=10), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_e1_histogram(histogram: np.ndarray, best: int):
    """Zahl der Strategien je Gewinnzahl (von 8), logarithmische Achse; die beste Gewinnzahl `best` ist hervorgehoben."""
    ks = list(range(len(histogram)))
    fig = go.Figure(go.Bar(x=ks, y=histogram, marker_color=[C.COLOR_WIN if k == best else C.COLOR_LINE for k in ks], text=[f"{int(v):,}".replace(",", " ") for v in histogram],
                           textposition="outside", hovertemplate="%{x} von 8 gewonnen: %{y} Strategien<extra></extra>"))
    fig.update_xaxes(title_text="Gewonnene Hutverteilungen (von 8)", dtick=1)
    fig.update_yaxes(title_text="Zahl der Strategien (logarithmisch)", type="log", range=[-0.2, np.log10(max(1, histogram.max())) + 0.8])
    return _base(fig)
