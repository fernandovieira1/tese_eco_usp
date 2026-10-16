"""Módulo de métricas de Dados em Painel: Decomposição Overall/Between/Within, VIF, Correlações e Transformações Within."""

from __future__ import annotations

from typing import Iterable, List, Literal, Optional

import numpy as np
import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant

from .data_loader import get_column_block


def compute_panel_descriptive_table(
    df: pd.DataFrame,
    columns: Iterable[str],
    entity_col: str = "codigo_ibge",
    time_col: str = "ano",
) -> pd.DataFrame:
    """Calcula a Tabela Descritiva de Dados em Painel reportando:
    - Bloco Teórico
    - Variável
    - N Válido
    - % Missing
    - Média
    - Mediana
    - Min
    - Max
    - DP Overall
    - DP Between (entre municípios `codigo_ibge`)
    - DP Within (variação intra-município ao longo de `ano`: x_it - x_bar_i + x_bar)
    - Natureza da Variação (Invariante no Tempo, Comum no Espaço ou Painel Completo)
    """
    total_rows = len(df)
    records = []

    for col in columns:
        if col not in df.columns or col in {entity_col, time_col, "bioma_dominante", "municipio_nome", "municipio_label"}:
            continue

        s_raw = df[col]
        # Converter booleanos ou numéricos para float para decomposição de variância
        if pd.api.types.is_bool_dtype(s_raw) or str(s_raw.dtype) == "boolean":
            s_num = s_raw.astype("float64")
        else:
            s_num = pd.to_numeric(s_raw, errors="coerce").astype("float64")

        n_valid = int(s_num.notna().sum())
        pct_missing = 100.0 * (total_rows - n_valid) / total_rows if total_rows > 0 else np.nan

        if n_valid == 0:
            records.append({
                "Bloco": get_column_block(col),
                "Variável": col,
                "N Válido": 0,
                "% Missing": round(pct_missing, 2),
                "Média": np.nan,
                "Mediana": np.nan,
                "Min": np.nan,
                "Max": np.nan,
                "DP Overall": np.nan,
                "DP Between": np.nan,
                "DP Within": np.nan,
                "Razão Within/Overall": np.nan,
                "Estrutura no Painel": "100% Missing",
            })
            continue

        sub = pd.DataFrame({
            entity_col: df[entity_col],
            time_col: df[time_col],
            "val": s_num,
        }).dropna(subset=["val"])

        overall_mean = float(sub["val"].mean())
        overall_median = float(sub["val"].median())
        overall_min = float(sub["val"].min())
        overall_max = float(sub["val"].max())
        dp_overall = float(sub["val"].std(ddof=1)) if len(sub) > 1 else 0.0

        # Média por município (Between)
        entity_means = sub.groupby(entity_col, observed=True)["val"].mean()
        dp_between = float(entity_means.std(ddof=1)) if len(entity_means) > 1 else 0.0

        # Transformação Within clássica (Stata xtsum): x_it - x_bar_i + x_bar
        entity_mean_broadcast = sub.groupby(entity_col, observed=True)["val"].transform("mean")
        within_vals = sub["val"] - entity_mean_broadcast + overall_mean
        dp_within = float(within_vals.std(ddof=1)) if len(within_vals) > 1 else 0.0

        # Identificar invariância temporal ou espacial e zerar ruído numérico de ponto flutuante
        tol = 1e-10
        if dp_overall <= tol:
            estrutura = "Constante (DP = 0)"
            dp_overall = 0.0
            dp_between = 0.0
            dp_within = 0.0
        elif dp_within <= tol * max(1.0, abs(overall_mean), dp_overall):
            estrutura = "Invariante no Tempo (DP Within = 0)"
            dp_within = 0.0
        elif dp_between <= tol * max(1.0, abs(overall_mean), dp_overall):
            estrutura = "Invariante entre Municípios (Choque Macro)"
            dp_between = 0.0
        else:
            estrutura = "Variação Município × Ano"

        ratio_within = (dp_within / dp_overall) if dp_overall > tol else 0.0

        records.append({
            "Bloco": get_column_block(col),
            "Variável": col,
            "N Válido": n_valid,
            "% Missing": round(pct_missing, 2),
            "Média": overall_mean,
            "Mediana": overall_median,
            "Min": overall_min,
            "Max": overall_max,
            "DP Overall": dp_overall,
            "DP Between": dp_between,
            "DP Within": dp_within,
            "Razão Within/Overall": round(ratio_within, 4),
            "Estrutura no Painel": estrutura,
        })

    return pd.DataFrame(records)


def export_descriptive_to_latex(
    desc_df: pd.DataFrame,
    caption: str = "Estatísticas Descritivas e Decomposição de Variância do Painel Municipal (Mato Grosso, 2001--2024)",
    label: str = "tab:desc_painel_chap1",
) -> str:
    """Exporta a Tabela Descritiva de Painel em formato LaTeX padrão `booktabs`."""
    if desc_df.empty:
        return "% Tabela vazia"

    cols_to_export = [
        "Variável",
        "N Válido",
        "% Missing",
        "Média",
        "Mediana",
        "Min",
        "Max",
        "DP Overall",
        "DP Between",
        "DP Within",
    ]
    available_cols = [c for c in cols_to_export if c in desc_df.columns]
    sub = desc_df[available_cols].copy()

    def _escape_latex(text: str) -> str:
        return (
            str(text)
            .replace("\\", "\\textbackslash{}")
            .replace("_", "\\_")
            .replace("%", "\\%")
            .replace("&", "\\&")
            .replace("#", "\\#")
        )

    def _fmt(val: float) -> str:
        if pd.isna(val):
            return "--"
        abs_v = abs(val)
        if abs_v == 0:
            return "0.000"
        if abs_v < 0.001 or abs_v >= 1_000_000:
            return f"{val:.3e}"
        if abs_v < 1:
            return f"{val:.4f}"
        return f"{val:,.3f}"

    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        "\\footnotesize",
        "\\begin{tabular}{lrrrrrrrrr}",
        "\\toprule",
        "Variável & $N$ & \\% Miss. & Média & Mediana & Mín. & Máx. & DP Overall & DP Between & DP Within \\\\",
        "\\midrule",
    ]

    for _, row in sub.iterrows():
        var_tex = _escape_latex(row["Variável"])
        n_val = f"{int(row['N Válido']):,}" if pd.notna(row["N Válido"]) else "0"
        pct_m = f"{row['% Missing']:.1f}\\%" if pd.notna(row["% Missing"]) else "--"
        line = (
            f"{var_tex} & {n_val} & {pct_m} & "
            f"{_fmt(row['Média'])} & {_fmt(row['Mediana'])} & "
            f"{_fmt(row['Min'])} & {_fmt(row['Max'])} & "
            f"{_fmt(row['DP Overall'])} & {_fmt(row['DP Between'])} & {_fmt(row['DP Within'])} \\\\"
        )
        lines.append(line)

    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        "\\begin{tablenotes}[flushleft]",
        "\\footnotesize",
        "\\item \\textit{Nota:} Painel municipal de Mato Grosso ($N = 3.384$, 141 municípios $\\times$ 24 anos, 2001--2024). "
        "DP Between mede o desvio-padrão das médias municipais ($\\bar{x}_i$); "
        "DP Within mede a variação intra-município ao longo do tempo ($x_{it} - \\bar{x}_i + \\bar{x}$).",
        "\\end{tablenotes}",
        "\\end{table}",
    ])
    return "\n".join(lines)


def transform_within(
    df: pd.DataFrame,
    columns: Iterable[str],
    mode: Literal["pooled", "within_entity", "double_demeaned"] = "within_entity",
    entity_col: str = "codigo_ibge",
    time_col: str = "ano",
    add_grand_mean: bool = False,
    max_iter: int = 100,
    tol: float = 1e-10,
) -> pd.DataFrame:
    """Realiza transformação de dados em painel:
    - `pooled`: retorna os valores em nível sem transformação.
    - `within_entity`: Demeaned por município (x_it - x_bar_i [+ x_bar se add_grand_mean=True]).
    - `double_demeaned`: Double-Demeaned por município + ano (projeção iterativa exata sobre
      efeitos fixos de município e ano, válida inclusive para subamostras desbalanceadas).
    """
    cols = [c for c in columns if c in df.columns]
    out = df[[entity_col, time_col] + (["bioma_dominante"] if "bioma_dominante" in df.columns else []) + cols].copy()

    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce").astype("float64")

    if mode == "pooled":
        return out

    if mode == "within_entity":
        for c in cols:
            valid = out[c].notna()
            if not valid.any():
                continue
            grand_mean = float(out.loc[valid, c].mean()) if add_grand_mean else 0.0
            entity_means = out.loc[valid].groupby(entity_col, observed=True)[c].transform("mean")
            out.loc[valid, c] = out.loc[valid, c] - entity_means + grand_mean
        return out

    if mode == "double_demeaned":
        # Projeção alternada (Método de Gauss-Seidel / Frisch-Waugh-Lovell iterativo)
        # Garante ortogonalidade exata aos FEs de município e ano mesmo com missings.
        for c in cols:
            valid = out[c].notna()
            if not valid.any():
                continue
            sub_idx = out.index[valid]
            grand_mean = float(out.loc[sub_idx, c].mean()) if add_grand_mean else 0.0
            vals = out.loc[sub_idx, c].to_numpy(dtype="float64", copy=True)
            ent_ids = out.loc[sub_idx, entity_col].to_numpy()
            time_ids = out.loc[sub_idx, time_col].to_numpy()

            work_df = pd.DataFrame({"e": ent_ids, "t": time_ids, "v": vals})
            for _ in range(max_iter):
                prev = work_df["v"].to_numpy( copy=True)
                work_df["v"] = work_df["v"] - work_df.groupby("e", observed=True)["v"].transform("mean")
                work_df["v"] = work_df["v"] - work_df.groupby("t", observed=True)["v"].transform("mean")
                if np.max(np.abs(work_df["v"].to_numpy() - prev)) < tol:
                    break
            out.loc[sub_idx, c] = work_df["v"].to_numpy() + grand_mean
        return out

    raise ValueError(f"Modo de transformação desconhecido: {mode}")


def compute_correlation_matrix(
    df: pd.DataFrame,
    columns: Iterable[str],
    method: Literal["pearson", "spearman"] = "pearson",
) -> pd.DataFrame:
    """Calcula a matriz de correlação (Pearson ou Spearman) para as colunas selecionadas."""
    cols = [c for c in columns if c in df.columns]
    if not cols:
        return pd.DataFrame()
    num_df = df[cols].apply(pd.to_numeric, errors="coerce").astype("float64")
    return num_df.corr(method=method)


def compute_vif_table(
    df: pd.DataFrame,
    columns: Iterable[str],
    demean_mode: Literal["pooled", "within_entity", "double_demeaned"] = "pooled",
) -> pd.DataFrame:
    """Calcula o Variance Inflation Factor (VIF) e a Tolerância (1/VIF) para as variáveis candidatas."""
    cols = [c for c in columns if c in df.columns]
    if len(cols) < 2:
        return pd.DataFrame(columns=["Variável", "VIF", "Tolerância (1/VIF)", "R² Auxiliar", "Diagnóstico", "N Amostral"])

    work_df = transform_within(df, cols, mode=demean_mode) if demean_mode != "pooled" else df[cols].copy()
    num_df = work_df[cols].apply(pd.to_numeric, errors="coerce").astype("float64").dropna()

    n_sample = len(num_df)
    if n_sample < len(cols) + 2:
        return pd.DataFrame([{
            "Variável": c,
            "VIF": np.nan,
            "Tolerância (1/VIF)": np.nan,
            "R² Auxiliar": np.nan,
            "Diagnóstico": f"Amostra insuficiente após dropna (N={n_sample})",
            "N Amostral": n_sample,
        } for c in cols])

    # Separar colunas com variância zero (ex.: variáveis invariantes no tempo após Within)
    stds = num_df.std(ddof=1)
    zero_var_cols = stds[stds <= 1e-10].index.tolist()
    active_cols = [c for c in cols if c not in zero_var_cols]

    rows = []
    for c in zero_var_cols:
        rows.append({
            "Variável": c,
            "VIF": np.inf,
            "Tolerância (1/VIF)": 0.0,
            "R² Auxiliar": 1.0,
            "Diagnóstico": "Absorvida pelo Efeito Fixo (Variância Zero)",
            "N Amostral": n_sample,
        })

    if len(active_cols) >= 2:
        X = add_constant(num_df[active_cols], has_constant="add")
        X_mat = X.to_numpy(dtype="float64")
        col_names = list(X.columns)

        for idx, col_name in enumerate(col_names):
            if col_name == "const":
                continue
            try:
                vif_val = float(variance_inflation_factor(X_mat, idx))
            except Exception:
                vif_val = np.inf

            if np.isinf(vif_val) or vif_val > 1e6:
                tol_val = 0.0
                r2_aux = 1.0
                diag = "Colinearidade Perfeita / Extrema (VIF > 100)"
            else:
                tol_val = 1.0 / vif_val if vif_val > 0 else np.nan
                r2_aux = 1.0 - tol_val if pd.notna(tol_val) else np.nan
                if vif_val >= 10.0:
                    diag = "Alta Multicolinearidade (VIF >= 10)"
                elif vif_val >= 5.0:
                    diag = "Atenção / Moderada (5 <= VIF < 10)"
                else:
                    diag = "Baixa Colinearidade (VIF < 5)"

            rows.append({
                "Variável": col_name,
                "VIF": round(vif_val, 3) if np.isfinite(vif_val) else np.inf,
                "Tolerância (1/VIF)": round(tol_val, 4) if pd.notna(tol_val) else 0.0,
                "R² Auxiliar": round(r2_aux, 4) if pd.notna(r2_aux) else 1.0,
                "Diagnóstico": diag,
                "N Amostral": n_sample,
            })
    elif len(active_cols) == 1:
        rows.append({
            "Variável": active_cols[0],
            "VIF": 1.0,
            "Tolerância (1/VIF)": 1.0,
            "R² Auxiliar": 0.0,
            "Diagnóstico": "Única variável ativa com variância > 0",
            "N Amostral": n_sample,
        })

    return pd.DataFrame(rows).sort_values("VIF", ascending=False).reset_index(drop=True)


def compute_missing_summary_by_year(
    df: pd.DataFrame,
    columns: Iterable[str],
    time_col: str = "ano",
) -> pd.DataFrame:
    """Calcula a porcentagem de valores ausentes (% Missing) por ano para cada variável selecionada."""
    cols = [c for c in columns if c in df.columns]
    if not cols:
        return pd.DataFrame()
    grouped = df.groupby(time_col, observed=True)[cols].apply(lambda g: 100.0 * g.isna().mean())
    return grouped.T


def compute_sample_loss_comparison(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Compara a perda amostral entre famílias de proxies chave do Capítulo 1:
    - Conversão Bruta (MapBiomas)
    - Capacidade Produtiva Histórica PAM (1991-2000, min 7 anos) vs. GAEZ v4 (1961-1990)
    - Produtividade Contemporânea PAM (Soja vs. Milho)
    - IBAMA Autos e Multas (Informada vs. Espacial; Antes vs. Depois da Imputação pela Flag)
    """
    from .data_loader import apply_ibama_imputation

    total_n = len(df_raw)
    df_imp = apply_ibama_imputation(df_raw, impute_zeros=True, apply_log1p=False)

    comparisons = [
        (
            "[Y] Taxa de Conversão -> Agricultura (MapBiomas)",
            df_raw["taxa_conversao__agricultura"],
            "Perda em municípios com transição espacial incompleta (y_cobertura_completa=False)",
        ),
        (
            "[Y] Taxa de Conversão -> Pastagem (MapBiomas)",
            df_raw["taxa_conversao__pastagem"],
            "Perda em municípios com transição espacial incompleta (y_cobertura_completa=False)",
        ),
        (
            "[X2] Capacidade PAM Soja (1991-2000, mín. 7 anos)",
            df_raw["capacidade_z__soja__pam_1991_2000_min7"],
            "Alta perda amostral (2.256 missings / 94 municípios sem histórico mínimo de soja nos anos 90)",
        ),
        (
            "[X2] Capacidade PAM Milho (1991-2000, mín. 7 anos)",
            df_raw["capacidade_z__milho__pam_1991_2000_min7"],
            "Perda moderada (576 missings / 24 municípios sem histórico mínimo de milho nos anos 90)",
        ),
        (
            "[X2] Capacidade GAEZ Soja (sxHr0 / sxLr0 / yxHr0 / yxLr0)",
            df_raw["capacidade_z__soja__gaez_yxHr0_soy"],
            "Cobertura plena (0 missings nos 141 municípios × 24 anos)",
        ),
        (
            "[X2] Capacidade GAEZ Milho (sxHr0 / sxLr0 / yxHr0 / yxLr0)",
            df_raw["capacidade_z__milho__gaez_yxHr0_mze"],
            "Cobertura plena (0 missings nos 141 municípios × 24 anos)",
        ),
        (
            "[X3] IBAMA Autos Desmatamento Informada (Sem Imputação)",
            df_raw["n_autos_desmatamento__ibama_informada"],
            "Mistura 1.100 pares sem registro identificado + 573 missings estruturais (tema parcial)",
        ),
        (
            "[X3] IBAMA Autos Desmatamento Informada (Pós-Imputação Flag)",
            df_imp["n_autos_desmatamento__ibama_informada"],
            "Recupera 1.100 zeros legítimos; preserva 573 missings estruturais reais",
        ),
        (
            "[X3] IBAMA Autos Flora Informada (Sem Imputação)",
            df_raw["n_autos_flora__ibama_informada"],
            "Mistura 1.100 pares sem registro identificado + 140 missings estruturais (tema parcial)",
        ),
        (
            "[X3] IBAMA Autos Flora Informada (Pós-Imputação Flag)",
            df_imp["n_autos_flora__ibama_informada"],
            "Recupera 1.100 zeros legítimos; preserva 140 missings estruturais reais",
        ),
        (
            "[X3] IBAMA Autos Desmatamento Espacial (Sem Imputação)",
            df_raw["n_autos_desmatamento__ibama_espacial"],
            "Mistura 1.556 pares sem coordenada/auto identificado + 144 missings estruturais",
        ),
        (
            "[X3] IBAMA Autos Desmatamento Espacial (Pós-Imputação Flag)",
            df_imp["n_autos_desmatamento__ibama_espacial"],
            "Recupera 1.556 zeros pela flag espacial; preserva 144 missings estruturais",
        ),
    ]

    rows = []
    for label, series, note in comparisons:
        n_val = int(series.notna().sum())
        n_miss = total_n - n_val
        n_muni = int(df_raw.loc[series.notna(), "codigo_ibge"].nunique())
        rows.append({
            "Medida / Cenário": label,
            "N Válido": n_val,
            "N Missing": n_miss,
            "% Cobertura": round(100.0 * n_val / total_n, 2),
            "% Perda Amostral": round(100.0 * n_miss / total_n, 2),
            "Municípios Cobertos (de 141)": n_muni,
            "Diagnóstico Metodológico": note,
        })
    return pd.DataFrame(rows)


def _gini_coefficient(values: np.ndarray) -> float:
    """Calcula o índice de Gini para valores não-negativos."""
    x = np.asarray(values, dtype="float64")
    x = x[np.isfinite(x) & (x >= 0)]
    if len(x) == 0:
        return np.nan
    total = np.sum(x)
    if total <= 0:
        return 0.0
    x_sorted = np.sort(x)
    n = len(x_sorted)
    idx = np.arange(1, n + 1, dtype="float64")
    return float((2.0 * np.sum(idx * x_sorted) / (n * total)) - (n + 1.0) / n)


def compute_univariate_deep_profile(
    df: pd.DataFrame,
    columns: Iterable[str],
    entity_col: str = "codigo_ibge",
) -> pd.DataFrame:
    """Gera perfil univariado avançado com intuição econômica:
    - Margem extensiva (% Zeros vs. % Estritamente Positivos)
    - Média incondicional vs. Média condicional aos positivos E[X | X > 0]
    - Assimetria (Skewness), Curtose (Excesso), Coeficiente de Variação (CV)
    - Quantis detalhados (P01, P05, P10, P25, P50, P75, P90, P95, P99)
    - Índice de Gini Municipal e concentração no Top 10% e Top 20% dos municípios.
    """
    rows = []
    n_total = len(df)

    for col in columns:
        if col not in df.columns:
            continue
        s = pd.to_numeric(df[col], errors="coerce").astype("float64")
        v = s.dropna()
        n_val = len(v)
        if n_val == 0:
            continue

        n_zeros = int((v == 0).sum())
        n_pos = int((v > 0).sum())
        n_neg = int((v < 0).sum())
        pct_zeros = 100.0 * n_zeros / n_val
        pct_pos = 100.0 * n_pos / n_val

        mean_all = float(v.mean())
        std_all = float(v.std(ddof=1)) if n_val > 1 else 0.0
        cv_val = (std_all / abs(mean_all)) if abs(mean_all) > 1e-12 else np.nan
        mean_pos = float(v[v > 0].mean()) if n_pos > 0 else np.nan
        median_pos = float(v[v > 0].median()) if n_pos > 0 else np.nan

        qs = v.quantile([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99])
        iqr_val = float(qs.loc[0.75] - qs.loc[0.25])
        p50 = float(qs.loc[0.50])
        ratio_p90_p50 = float(qs.loc[0.90] / p50) if abs(p50) > 1e-12 else np.nan

        # Concentração espacial entre os municípios (média municipal no período)
        muni_means = df.assign(_v=s).groupby(entity_col, observed=True)["_v"].mean().dropna()
        if len(muni_means) > 0 and (muni_means >= 0).all() and muni_means.sum() > 0:
            gini_muni = _gini_coefficient(muni_means.to_numpy())
            muni_sorted = muni_means.sort_values(ascending=False)
            k10 = max(1, int(round(0.10 * len(muni_sorted))))
            k20 = max(1, int(round(0.20 * len(muni_sorted))))
            top10_pct = float(100.0 * muni_sorted.iloc[:k10].sum() / muni_sorted.sum())
            top20_pct = float(100.0 * muni_sorted.iloc[:k20].sum() / muni_sorted.sum())
        else:
            gini_muni = np.nan
            top10_pct = np.nan
            top20_pct = np.nan

        rows.append({
            "Bloco": get_column_block(col),
            "Variável": col,
            "N Válido": n_val,
            "% Missing": round(100.0 * (n_total - n_val) / n_total, 2),
            "% Zeros (X=0)": round(pct_zeros, 2),
            "% Positivos (X>0)": round(pct_pos, 2),
            "N Negativos": n_neg,
            "Média Geral": mean_all,
            "Média Positivos (X>0)": mean_pos,
            "Mediana Positivos (X>0)": median_pos,
            "DP Overall": std_all,
            "CV (DP/|Média|)": round(cv_val, 3) if pd.notna(cv_val) else np.nan,
            "Assimetria (Skew)": round(float(v.skew()), 3) if n_val > 2 else np.nan,
            "Curtose (Excesso)": round(float(v.kurt()), 3) if n_val > 3 else np.nan,
            "Min": float(v.min()),
            "P01": float(qs.loc[0.01]),
            "P05": float(qs.loc[0.05]),
            "P10": float(qs.loc[0.10]),
            "P25": float(qs.loc[0.25]),
            "Mediana (P50)": p50,
            "P75": float(qs.loc[0.75]),
            "P90": float(qs.loc[0.90]),
            "P95": float(qs.loc[0.95]),
            "P99": float(qs.loc[0.99]),
            "Max": float(v.max()),
            "IQR (P75-P25)": iqr_val,
            "Razão P90/P50": round(ratio_p90_p50, 2) if pd.notna(ratio_p90_p50) else np.nan,
            "Gini Municipal": round(gini_muni, 3) if pd.notna(gini_muni) else np.nan,
            "Top 10% Munis (%)": round(top10_pct, 1) if pd.notna(top10_pct) else np.nan,
            "Top 20% Munis (%)": round(top20_pct, 1) if pd.notna(top20_pct) else np.nan,
        })
    return pd.DataFrame(rows)


def compute_lorenz_curves(
    df: pd.DataFrame,
    columns: Iterable[str],
    agg_mode: Literal["sum", "mean"] = "sum",
    entity_col: str = "codigo_ibge",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calcula as coordenadas da Curva de Lorenz municipal e tabela de concentração espacial (Gini e Pareto)."""
    curve_rows = []
    summary_rows = []

    for col in columns:
        if col not in df.columns:
            continue
        s = pd.to_numeric(df[col], errors="coerce").astype("float64")
        tmp = pd.DataFrame({entity_col: df[entity_col], "val": s}).dropna(subset=["val"])
        if tmp.empty:
            continue
        if agg_mode == "sum":
            muni_s = tmp.groupby(entity_col, observed=True)["val"].sum(min_count=1).dropna()
        else:
            muni_s = tmp.groupby(entity_col, observed=True)["val"].mean().dropna()

        muni_s = muni_s.clip(lower=0.0)
        total_val = float(muni_s.sum())
        if total_val <= 0 or len(muni_s) < 2:
            continue

        asc = np.sort(muni_s.to_numpy(dtype="float64"))
        n = len(asc)
        pop_cum = np.concatenate([[0.0], np.arange(1, n + 1, dtype="float64") / n]) * 100.0
        val_cum = np.concatenate([[0.0], np.cumsum(asc) / total_val]) * 100.0

        for px_v, py_v in zip(pop_cum, val_cum):
            curve_rows.append({
                "Variável": col,
                "% Acumulado de Municípios": float(px_v),
                "% Acumulado do Valor Estadual": float(py_v),
            })

        desc_s = muni_s.sort_values(ascending=False)
        k5 = max(1, int(round(0.05 * n)))
        k10 = max(1, int(round(0.10 * n)))
        k20 = max(1, int(round(0.20 * n)))
        k50 = max(1, int(round(0.50 * n)))

        summary_rows.append({
            "Variável": col,
            "Agregação Municipal": "Soma no Período" if agg_mode == "sum" else "Média Anual",
            "Municípios Válidos": n,
            "Índice de Gini Municipal": round(_gini_coefficient(asc), 3),
            "Top 5% (7 Munis) %": round(100.0 * float(desc_s.iloc[:k5].sum()) / total_val, 1),
            "Top 10% (14 Munis) %": round(100.0 * float(desc_s.iloc[:k10].sum()) / total_val, 1),
            "Top 20% (28 Munis) %": round(100.0 * float(desc_s.iloc[:k20].sum()) / total_val, 1),
            "Bottom 50% (70 Munis) %": round(100.0 * float(asc[:k50].sum()) / total_val, 1),
            "Total Estadual Acumulado": total_val,
        })

    return pd.DataFrame(curve_rows), pd.DataFrame(summary_rows)


def compute_municipal_ranking(
    df: pd.DataFrame,
    col: str,
    rank_by: Literal["sum", "mean"] = "sum",
) -> pd.DataFrame:
    """Constrói o ranking completo dos 141 municípios para qualquer variável selecionada."""
    if col not in df.columns:
        return pd.DataFrame()

    work = df[["codigo_ibge", "municipio_nome", "municipio_label", "bioma_dominante", "ano", col]].copy()
    work["val"] = pd.to_numeric(work[col], errors="coerce").astype("float64")

    grouped = (
        work.groupby(["codigo_ibge", "municipio_nome", "municipio_label", "bioma_dominante"], observed=True)
        .agg(
            anos_validos=("val", "count"),
            anos_positivos=("val", lambda s: int((s.dropna() > 0).sum())),
            soma_periodo=("val", lambda s: s.sum(min_count=1)),
            media_anual=("val", "mean"),
            mediana_anual=("val", "median"),
            dp_intra_muni=("val", "std"),
            maximo_anual=("val", "max"),
        )
        .reset_index()
    )

    sort_col = "soma_periodo" if rank_by == "sum" else "media_anual"
    grouped = grouped.sort_values(sort_col, ascending=False, na_position="last").reset_index(drop=True)
    grouped["Posição"] = np.arange(1, len(grouped) + 1)

    total_pos = float(grouped[sort_col].clip(lower=0).sum())
    if total_pos > 0:
        grouped["% do Total Estadual"] = 100.0 * grouped[sort_col].clip(lower=0) / total_pos
        grouped["% Acumulado (Pareto)"] = grouped["% do Total Estadual"].cumsum()
    else:
        grouped["% do Total Estadual"] = np.nan
        grouped["% Acumulado (Pareto)"] = np.nan

    return grouped[[
        "Posição",
        "municipio_nome",
        "codigo_ibge",
        "municipio_label",
        "bioma_dominante",
        "anos_validos",
        "anos_positivos",
        "soma_periodo",
        "media_anual",
        "mediana_anual",
        "dp_intra_muni",
        "maximo_anual",
        "% do Total Estadual",
        "% Acumulado (Pareto)",
    ]].rename(columns={
        "municipio_nome": "Município",
        "codigo_ibge": "Código IBGE",
        "bioma_dominante": "Bioma Dominante",
        "anos_validos": "Anos Válidos",
        "anos_positivos": "Anos (X > 0)",
        "soma_periodo": "Soma no Período",
        "media_anual": "Média Anual",
        "mediana_anual": "Mediana Anual",
        "dp_intra_muni": "DP Intra-Município",
        "maximo_anual": "Máximo Anual",
    })


def compute_structural_land_transition(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Constrói a síntese multivariada da Transição Estrutural do Uso da Terra em Mato Grosso:
    - Série anual (2001-2024): Estoques (% e Mha de Vegetação Nativa, Pastagem e Agricultura),
      Fluxos de Conversão Bruta (ha e % Agricultura no total convertido),
      Intensificação Pecuária (Lotação cab/ha e Rebanho em milhões de cabeças)
      e Preços Relativos Crop-to-Beef (Razão Soja/Carne e Milho/Carne, índice 2001=100).
    - Tabela síntese por Bioma comparando 2001 vs. 2024 e o balanço acumulado de conversão.
    """
    annual_rows = []
    for ano_val, grp in df.groupby("ano", observed=True):
        conv_ag = float(pd.to_numeric(grp["conversao_ha__agricultura"], errors="coerce").sum(min_count=1))
        conv_pa = float(pd.to_numeric(grp["conversao_ha__pastagem"], errors="coerce").sum(min_count=1))
        conv_tot = (conv_ag if pd.notna(conv_ag) else 0.0) + (conv_pa if pd.notna(conv_pa) else 0.0)
        share_conv_ag = (100.0 * conv_ag / conv_tot) if conv_tot > 0 else np.nan

        p_soja = float(pd.to_numeric(grp["preco_real_usd2024_media_anual__soja"], errors="coerce").mean())
        p_milho = float(pd.to_numeric(grp["preco_real_usd2024_media_anual__milho"], errors="coerce").mean())
        p_carne = float(pd.to_numeric(grp["preco_real_usd2024_media_anual__carne_bovina"], errors="coerce").mean())

        annual_rows.append({
            "ano": int(ano_val),
            "Nativa Share Médio (%)": 100.0 * float(pd.to_numeric(grp["nativa_share"], errors="coerce").mean()),
            "Pastagem Share Médio (%)": 100.0 * float(pd.to_numeric(grp["pastagem_share"], errors="coerce").mean()),
            "Agricultura Share Médio (%)": 100.0 * float(pd.to_numeric(grp["agricultura_share"], errors="coerce").mean()),
            "Estoque Nativa (Mha)": float(pd.to_numeric(grp["nativa_ha"], errors="coerce").sum()) / 1e6,
            "Estoque Pastagem (Mha)": float(pd.to_numeric(grp["pastagem_ha"], errors="coerce").sum()) / 1e6,
            "Estoque Agricultura (Mha)": float(pd.to_numeric(grp["agricultura_ha"], errors="coerce").sum()) / 1e6,
            "Conversão Bruta -> Agricultura (mil ha)": conv_ag / 1000.0 if pd.notna(conv_ag) else np.nan,
            "Conversão Bruta -> Pastagem (mil ha)": conv_pa / 1000.0 if pd.notna(conv_pa) else np.nan,
            "% Agricultura na Conversão Bruta Total": share_conv_ag,
            "Lotação Bovina Média (cab/ha)": float(pd.to_numeric(grp["lotacao_cabecas_ha"], errors="coerce").mean()),
            "Rebanho Bovino Total (milhões cab.)": float(pd.to_numeric(grp["efetivo_bovino"], errors="coerce").sum()) / 1e6,
            "Preço Real Soja (USD/t)": p_soja,
            "Preço Real Milho (USD/t)": p_milho,
            "Preço Real Carne (USD/kg)": p_carne,
            "Razão Preço Soja/Carne": p_soja / p_carne if p_carne > 0 else np.nan,
            "Razão Preço Milho/Carne": p_milho / p_carne if p_carne > 0 else np.nan,
        })

    annual_df = pd.DataFrame(annual_rows).sort_values("ano").reset_index(drop=True)
    if not annual_df.empty:
        base_sc = float(annual_df["Razão Preço Soja/Carne"].iloc[0])
        base_mc = float(annual_df["Razão Preço Milho/Carne"].iloc[0])
        annual_df["Índice Relativo Soja/Carne (Ano Inicial=100)"] = (
            100.0 * annual_df["Razão Preço Soja/Carne"] / base_sc if base_sc > 0 else np.nan
        )
        annual_df["Índice Relativo Milho/Carne (Ano Inicial=100)"] = (
            100.0 * annual_df["Razão Preço Milho/Carne"] / base_mc if base_mc > 0 else np.nan
        )

    # Resumo Estrutural por Bioma (Primeiro Ano vs. Último Ano da amostra ativa)
    y_first = int(df["ano"].min())
    y_last = int(df["ano"].max())
    biome_rows = []
    groups = [("Mato Grosso (Total)", df)] + [
        (str(b), df.loc[df["bioma_dominante"] == b])
        for b in ["Amazônia", "Cerrado", "Pantanal"]
        if (df["bioma_dominante"] == b).any()
    ]

    for g_label, g_df in groups:
        g_t0 = g_df.loc[g_df["ano"] == y_first]
        g_t1 = g_df.loc[g_df["ano"] == y_last]
        conv_ag_sum = float(pd.to_numeric(g_df["conversao_ha__agricultura"], errors="coerce").sum())
        conv_pa_sum = float(pd.to_numeric(g_df["conversao_ha__pastagem"], errors="coerce").sum())
        conv_total = conv_ag_sum + conv_pa_sum

        nat_t0 = 100.0 * float(g_t0["nativa_share"].mean()) if len(g_t0) else np.nan
        nat_t1 = 100.0 * float(g_t1["nativa_share"].mean()) if len(g_t1) else np.nan
        pas_t0 = 100.0 * float(g_t0["pastagem_share"].mean()) if len(g_t0) else np.nan
        pas_t1 = 100.0 * float(g_t1["pastagem_share"].mean()) if len(g_t1) else np.nan
        agr_t0 = 100.0 * float(g_t0["agricultura_share"].mean()) if len(g_t0) else np.nan
        agr_t1 = 100.0 * float(g_t1["agricultura_share"].mean()) if len(g_t1) else np.nan
        lot_t0 = float(g_t0["lotacao_cabecas_ha"].mean()) if len(g_t0) else np.nan
        lot_t1 = float(g_t1["lotacao_cabecas_ha"].mean()) if len(g_t1) else np.nan

        biome_rows.append({
            "Recorte Territorial": g_label,
            "Municípios": int(g_df["codigo_ibge"].nunique()),
            f"Nativa {y_first} (%)": round(nat_t0, 1),
            f"Nativa {y_last} (%)": round(nat_t1, 1),
            "Δ Nativa (p.p.)": round(nat_t1 - nat_t0, 1),
            f"Pastagem {y_first} (%)": round(pas_t0, 1),
            f"Pastagem {y_last} (%)": round(pas_t1, 1),
            "Δ Pastagem (p.p.)": round(pas_t1 - pas_t0, 1),
            f"Agricultura {y_first} (%)": round(agr_t0, 1),
            f"Agricultura {y_last} (%)": round(agr_t1, 1),
            "Δ Agricultura (p.p.)": round(agr_t1 - agr_t0, 1),
            "Conv. Bruta Agricultura (ha)": round(conv_ag_sum, 0),
            "Conv. Bruta Pastagem (ha)": round(conv_pa_sum, 0),
            "% Pastagem na Conv. Bruta": round(100.0 * conv_pa_sum / conv_total, 1) if conv_total > 0 else np.nan,
            f"Lotação {y_first} (cab/ha)": round(lot_t0, 2),
            f"Lotação {y_last} (cab/ha)": round(lot_t1, 2),
            "Δ Lotação (%)": round(100.0 * (lot_t1 - lot_t0) / lot_t0, 1) if lot_t0 and lot_t0 > 0 else np.nan,
        })

    return annual_df, pd.DataFrame(biome_rows)


def compute_multivariate_regimes_h1(
    df: pd.DataFrame,
    y_col: str,
    cap_col: str,
    price_col: str,
    ibama_col: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Cruza Tercis de Capacidade Produtiva (X2) × Regimes de Choque de Preços (X1) × Fiscalização IBAMA (X3),
    comparando Nível Bruto (Pooled) vs. Variação Intra-Município e Intra-Ano (Double-Demeaned)."""
    needed = ["codigo_ibge", "ano", "bioma_dominante", y_col, cap_col, price_col, ibama_col]
    sub = df[[c for c in needed if c in df.columns]].copy()
    for c in [y_col, cap_col, price_col, ibama_col]:
        sub[c] = pd.to_numeric(sub[c], errors="coerce").astype("float64")
    sub = sub.dropna(subset=[y_col, cap_col, price_col]).reset_index(drop=True)
    if len(sub) < 30:
        return pd.DataFrame(), pd.DataFrame()

    # Transformação Double-Demeaned para isolar a variação Within (livre de FE município e FE ano)
    dm = transform_within(sub, [y_col], mode="double_demeaned", add_grand_mean=True)
    sub["y_within_fe"] = dm[y_col]

    # Tercis de capacidade produtiva local (X2)
    try:
        sub["tercil_capacidade"] = pd.qcut(
            sub[cap_col],
            q=3,
            labels=["1. Baixa Capacidade (T1)", "2. Média Capacidade (T2)", "3. Alta Capacidade (T3)"],
            duplicates="drop",
        )
    except ValueError:
        sub["tercil_capacidade"] = pd.cut(
            sub[cap_col],
            bins=3,
            labels=["1. Baixa Capacidade (T1)", "2. Média Capacidade (T2)", "3. Alta Capacidade (T3)"],
        )

    # Regime de Preço/Choque (X1 >= Mediana vs. < Mediana)
    p_med = float(sub[price_col].median())
    sub["regime_preco"] = np.where(
        sub[price_col] >= p_med,
        "Choque / Preço Alto (>= Mediana)",
        "Choque / Preço Baixo (< Mediana)",
    )

    # Regime de Fiscalização IBAMA (X3 > Mediana dos positivos vs. Baixa/Zero)
    ib_valid = sub[ibama_col].dropna()
    if len(ib_valid) > 0:
        ib_cut = float(ib_valid.median())
        if ib_cut == 0:
            sub["regime_ibama"] = np.where(
                sub[ibama_col] > 0,
                "Fiscalização Ativa (Autos/Multas > 0)",
                "Sem Autuação (X3 = 0)",
            )
        else:
            sub["regime_ibama"] = np.where(
                sub[ibama_col] > ib_cut,
                "Fiscalização Alta (> Mediana)",
                "Fiscalização Baixa/Zero (<= Mediana)",
            )
    else:
        sub["regime_ibama"] = "Indisponível"

    scale = 100.0 if y_col.startswith("taxa_") else 1.0
    unit_lbl = "% a.a." if y_col.startswith("taxa_") else "ha"

    # Tabela 1: H1-a (Tercil Capacidade × Regime Preço)
    h1a_tbl = (
        sub.groupby(["tercil_capacidade", "regime_preco"], observed=True)
        .agg(
            n_obs=(y_col, "count"),
            n_munis=("codigo_ibge", "nunique"),
            media_pooled=(y_col, lambda s: float(s.mean()) * scale),
            mediana_pooled=(y_col, lambda s: float(s.median()) * scale),
            media_within_fe=("y_within_fe", lambda s: float(s.mean()) * scale),
        )
        .reset_index()
        .rename(columns={
            "tercil_capacidade": "Tercil de Capacidade Produtiva (X2)",
            "regime_preco": "Regime de Preço / Choque (X1)",
            "n_obs": "N Observações",
            "n_munis": "Municípios",
            "media_pooled": f"Média Bruta Pooled ({unit_lbl})",
            "mediana_pooled": f"Mediana Bruta ({unit_lbl})",
            "media_within_fe": f"Média Ajustada por FE ({unit_lbl})",
        })
    )

    # Tabela 2: H1-b (Tercil Capacidade × Regime Preço × Regime IBAMA)
    sub_ib = sub.dropna(subset=[ibama_col])
    h1b_tbl = (
        sub_ib.groupby(["tercil_capacidade", "regime_preco", "regime_ibama"], observed=True)
        .agg(
            n_obs=(y_col, "count"),
            media_pooled=(y_col, lambda s: float(s.mean()) * scale),
            media_within_fe=("y_within_fe", lambda s: float(s.mean()) * scale),
            ibama_medio=(ibama_col, "mean"),
        )
        .reset_index()
        .rename(columns={
            "tercil_capacidade": "Tercil de Capacidade (X2)",
            "regime_preco": "Regime de Preço (X1)",
            "regime_ibama": "Regime Institucional IBAMA (X3)",
            "n_obs": "N Observações",
            "media_pooled": f"Média Bruta Pooled ({unit_lbl})",
            "media_within_fe": f"Média Ajustada por FE ({unit_lbl})",
            "ibama_medio": "Média de X3 no Grupo",
        })
    )

    return h1a_tbl, h1b_tbl


def compute_municipal_pca_typology(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float]]:
    """Executa Análise de Componentes Principais (PCA via SVD) sobre o perfil estrutural
    dos 141 municípios de Mato Grosso para identificar clusters e padrões multivariados."""
    feature_map = {
        "taxa_conversao__agricultura": "Taxa Conv. Agricultura",
        "taxa_conversao__pastagem": "Taxa Conv. Pastagem",
        "capacidade_z__soja__gaez_yxHr0_soy": "Aptidão GAEZ Soja",
        "capacidade_z__milho__gaez_yxHr0_mze": "Aptidão GAEZ Milho",
        "nativa_share": "Estoque Vegetação Nativa (%)",
        "agricultura_share": "Área de Lavoura (%)",
        "pastagem_share": "Área de Pastagem (%)",
        "lotacao_cabecas_ha": "Lotação Bovina (cab/ha)",
        "n_autos_desmatamento__ibama_informada": "Autos Desmatamento IBAMA",
        "precip_mm_anual": "Chuva Anual (mm)",
        "elevation_mean_m": "Elevação Média (m)",
    }
    avail_cols = [c for c in feature_map if c in df.columns]
    muni_df = (
        df.groupby(["codigo_ibge", "municipio_nome", "municipio_label", "bioma_dominante"], observed=True)[avail_cols]
        .mean()
        .reset_index()
        .dropna(subset=avail_cols)
        .reset_index(drop=True)
    )

    if len(muni_df) < 5 or len(avail_cols) < 3:
        return pd.DataFrame(), pd.DataFrame(), {"PC1": 0.0, "PC2": 0.0, "PC3": 0.0}

    X = muni_df[avail_cols].to_numpy(dtype="float64")
    means = np.mean(X, axis=0)
    stds = np.std(X, axis=0, ddof=1)
    stds = np.where(stds <= 1e-10, 1.0, stds)
    Z = (X - means) / stds

    U, S, Vt = np.linalg.svd(Z, full_matrices=False)
    eigvals = (S ** 2) / (len(Z) - 1)
    var_ratios = eigvals / np.sum(eigvals)

    scores = Z @ Vt.T
    muni_df["PC1"] = scores[:, 0]
    muni_df["PC2"] = scores[:, 1]
    muni_df["PC3"] = scores[:, 2] if scores.shape[1] > 2 else 0.0

    loadings_rows = []
    for idx, col in enumerate(avail_cols):
        loadings_rows.append({
            "Coluna": col,
            "Indicador": feature_map[col],
            "Carga PC1": float(Vt[0, idx]),
            "Carga PC2": float(Vt[1, idx]),
            "Carga PC3": float(Vt[2, idx]) if Vt.shape[0] > 2 else 0.0,
            "Comunalidade (PC1+PC2)": float(Vt[0, idx] ** 2 + Vt[1, idx] ** 2),
        })
    loadings_df = pd.DataFrame(loadings_rows)

    explained = {
        "PC1": float(100.0 * var_ratios[0]),
        "PC2": float(100.0 * var_ratios[1]),
        "PC3": float(100.0 * var_ratios[2]) if len(var_ratios) > 2 else 0.0,
    }
    return muni_df, loadings_df, explained

