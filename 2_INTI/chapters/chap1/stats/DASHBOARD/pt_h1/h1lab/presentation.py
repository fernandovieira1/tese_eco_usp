"""Formatting and plot preparation; no source data are written by the dashboard."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm

from .panel_metrics import within_transform

COLORS = {"Amazônia": "#128275", "Cerrado": "#d89430", "Pantanal": "#496bb4", "Todos": "#128275"}
MODES = {"Nível (Pooled)": "pooled", "Within Município": "entity", "Double Demeaned (Município + Ano)": "twoway"}
INTERACTION_PREFIX = "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__"


def label(name: str) -> str:
    """Compact, still unique labels; full identifiers are retained in downloads."""
    replacements = {
        INTERACTION_PREFIX: "ln preço(t−1) × z | ",
        "taxa_conversao__": "Taxa de conversão | ",
        "conversao_ha__": "Conversão (ha) | ",
        "capacidade_valor__": "Capacidade | ",
        "capacidade_z__": "Capacidade z | ",
        "log1p__": "log(1 + x) | ",
        "preco_real_usd2024_media_anual": "Preço real USD 2024",
        "ln_preco_real_usd2024_media_anual": "ln preço real",
        "dln_preco_real_usd2024_media_anual": "Δln preço real",
    }
    for old in sorted(replacements, key=len, reverse=True):
        name = name.replace(old, replacements[old])
    return name.replace("__", " · ").replace("_lag1", " (t−1)").replace("_", " ")


def latex_escape(value: object) -> str:
    mapping = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
               "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    # Group labels and economic units use mathematical Unicode that the
    # document's text font may not contain. Emit portable LaTeX math instead.
    mapping.update({"≤": r"$\leq$", "≥": r"$\geq$", "−": r"$-$", "×": r"$\times$",
                    "Δ": r"$\Delta$", "²": r"$^2$", "→": r"$\to$"})
    return "".join(mapping.get(char, char) for char in str(value))


def booktabs(frame: pd.DataFrame, caption: str, note: str = "") -> str:
    """Standalone UTF-8 table fragment, requiring only booktabs in the document."""
    data = frame.reset_index()
    def cell(value):
        if value is None or (not isinstance(value, str) and pd.isna(value)):
            return "--"
        if isinstance(value, (float, np.floating)):
            return f"{value:.6g}" if np.isfinite(value) else r"$\infty$"
        return latex_escape(value)
    lines = ["% Requer \\usepackage{booktabs}; arquivo UTF-8.", r"\begin{table}[htbp]", r"\centering",
             r"\caption{" + latex_escape(caption) + "}", r"\scriptsize",
             r"\begin{tabular}{" + "l" * len(data.columns) + "}", r"\toprule",
             " & ".join(latex_escape(c) for c in data.columns) + r" \\", r"\midrule"]
    lines.extend(" & ".join(cell(v) for v in row) + r" \\" for row in data.itertuples(index=False, name=None))
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    if note:
        lines.extend([r"\par\smallskip", r"\parbox{0.98\linewidth}{\scriptsize " + latex_escape(note) + "}"])
    lines.append(r"\end{table}")
    return "\n".join(lines)


def style_figure(fig: go.Figure, height: int = 430) -> go.Figure:
    fig.update_layout(template="plotly_white", height=height, margin=dict(l=20, r=20, t=45, b=30),
                      font=dict(family="Arial, sans-serif", size=12),
                      legend=dict(orientation="h", y=-0.2, x=0), hovermode="closest")
    return fig


def annual_conversion(df: pd.DataFrame, destinations: list[str], metric: str, weighted: bool) -> pd.DataFrame:
    rows = []
    for (biome, year), group in df.groupby(["bioma_dominante", "ano"], observed=True):
        for destination in destinations:
            col = ("taxa_conversao__" if metric == "Taxa (%)" else "conversao_ha__") + destination
            valid = group[col].notna()
            sample = group.loc[valid]
            if sample.empty:
                value = np.nan
            elif metric == "Taxa (%)":
                if weighted:
                    denom = sample["y_nativa_inicial_ha"].sum(min_count=1)
                    value = 100 * sample[f"conversao_ha__{destination}"].sum(min_count=1) / denom if denom > 0 else np.nan
                else:
                    value = 100 * sample[col].mean()
            else:
                value = sample[col].sum(min_count=1)
            rows.append({"bioma": str(biome), "ano": year, "destino": destination, "valor": value,
                         "N municípios válidos": int(valid.sum()), "N municípios no filtro": len(group)})
    return pd.DataFrame(rows)


def binscatter_data(df: pd.DataFrame, y: str, x: str, mode: str, bins: int = 20,
                    stratify: bool = True, trim_pct: float = 0, leverage: bool = False):
    """Trim only for this plot, reproject on retained sample, fit OLS on observations."""
    cols = list(dict.fromkeys([y, x]))
    base = df.replace([np.inf, -np.inf], np.nan).dropna(subset=cols + ["codigo_ibge", "ano"]).copy()
    transformed = within_transform(base, cols, mode=mode)
    keep = pd.Series(True, index=transformed.index)
    if trim_pct > 0:
        for col in cols:
            distance = (transformed[col] - transformed[col].median()).abs()
            keep &= distance.le(distance.quantile(1 - trim_pct / 100))
    if leverage and len(transformed) > 2:
        z = transformed[x] - transformed[x].mean()
        denom = float(z.pow(2).sum())
        if denom > 0:
            h = 1 / len(z) + z.pow(2) / denom
            keep &= h.le(4 / len(z))
    removed = int((~keep).sum())
    retained = base.loc[keep]
    transformed = within_transform(retained, cols, mode=mode)
    transformed["grupo"] = retained["bioma_dominante"].astype("string") if stratify else "Todos"
    bin_rows, line_rows, summary = [], [], []
    for name, group in transformed.groupby("grupo", observed=True):
        if len(group) < 3 or group[x].std() <= 1e-12:
            summary.append({"Grupo": name, "N": len(group), "Bins": 0, "Inclinação OLS": np.nan,
                            "Situação": "X sem variação suficiente após transformação"})
            continue
        codes = pd.qcut(group[x], q=min(bins, len(group)), duplicates="drop")
        for _, chunk in group.groupby(codes, observed=True):
            bin_rows.append({"Grupo": str(name), "x": chunk[x].mean(), "y": chunk[y].mean(), "N no bin": len(chunk)})
        result = sm.OLS(group[y].to_numpy(), sm.add_constant(group[x].to_numpy(), has_constant="add")).fit()
        xx = np.linspace(group[x].min(), group[x].max(), 80)
        line_rows.extend({"Grupo": str(name), "x": v, "y": result.params[0] + result.params[1] * v} for v in xx)
        summary.append({"Grupo": str(name), "N": len(group), "Bins": codes.nunique(),
                        "Inclinação OLS": float(result.params[1]), "Situação": "OK"})
    return pd.DataFrame(bin_rows), pd.DataFrame(line_rows), pd.DataFrame(summary), removed


def comparison_table(coefficients: pd.DataFrame, diagnostics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in coefficients.itertuples():
        if row.status == "estimated":
            value = f"{row.coefficient:.5g} ({row.std_error:.4g})"
        else:
            value = {"absorbed": "Absorvida pelos EF", "collinear": "Colinear"}.get(row.status, row.status)
        rows.append({"Termo": row.term, "Modelo": row.model, "Estimativa (EP)": value})
    table = pd.DataFrame(rows).pivot(index="Termo", columns="Modelo", values="Estimativa (EP)") if rows else pd.DataFrame()
    for field, title in [("nobs", "N"), ("n_entities", "Clusters (municípios)"), ("n_years", "Anos"),
                         ("r2_within", "R² Within município"), ("r2_twfe", "R² Within município + ano")]:
        if field in diagnostics:
            for _, row in diagnostics.iterrows():
                value = row[field]
                table.loc[title, row["model"]] = f"{value:.5g}" if pd.notna(value) else "--"
    return table.fillna("—")
