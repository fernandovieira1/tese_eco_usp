"""Laboratório Econométrico de Dados em Painel: Efeitos Fixos Two-Way, Clusterização por Município, Horse Race e Exportação LaTeX."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy import stats

try:
    from linearmodels.panel import PanelOLS
    HAS_LINEARMODELS = True
except ImportError:
    HAS_LINEARMODELS = False

import statsmodels.api as sm
from .panel_metrics import transform_within


@dataclass
class SpecificationConfig:
    """Configuração de uma especificação econométrica candidata para o Horse Race."""
    name: str
    dep_var: str
    x1x2_vars: List[str]
    x3_vars: List[str]
    triple_interactions: List[Tuple[str, str]]  # pares (col_x1x2, col_x3) para gerar (X1*X2)*X3
    control_vars: List[str]
    entity_effects: bool = True
    time_effects: bool = True
    standardize_x3_in_triple: bool = False


def build_triple_interaction_column(
    df: pd.DataFrame,
    x1x2_col: str,
    x3_col: str,
    standardize_x3: bool = False,
) -> Tuple[pd.Series, str]:
    """Constrói a interação tripla (X1 * X2) * X3 para testar o condicionamento institucional (H1-b)."""
    s12 = pd.to_numeric(df[x1x2_col], errors="coerce").astype("float64")
    s3 = pd.to_numeric(df[x3_col], errors="coerce").astype("float64")

    if standardize_x3:
        mean_3 = s3.mean()
        std_3 = s3.std(ddof=1)
        if pd.notna(std_3) and std_3 > 1e-10:
            s3 = (s3 - mean_3) / std_3
        suffix_x3 = f"{x3_col}_z"
    else:
        suffix_x3 = x3_col

    short_12 = (
        x1x2_col
        .replace("interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__", "int_p_cap__")
        .replace("exposicao_real_x_", "exp_")
    )
    short_3 = suffix_x3.replace("__ibama_", "_")
    col_name = f"tripla__{short_12}__X__{short_3}"
    return s12 * s3, col_name


def estimate_twoway_fe(
    df: pd.DataFrame,
    dep_var: str,
    exog_vars: Sequence[str],
    entity_col: str = "codigo_ibge",
    time_col: str = "ano",
    entity_effects: bool = True,
    time_effects: bool = True,
    spec_name: str = "Model 1",
) -> Dict[str, object]:
    """Estima modelo de Efeitos Fixos (Two-Way FE: Município + Ano) com erros-padrão
    clusterizados ao nível de município (`codigo_ibge`).

    Utiliza `linearmodels.panel.PanelOLS` como motor primário e dispõe de fallback
    analítico exato via transformação Double-Demeaned + `statsmodels.OLS` com correção
    exata dos graus de liberdade dos efeitos fixos absorvidos.
    """
    exog_unique = list(dict.fromkeys([c for c in exog_vars if c in df.columns and c != dep_var]))
    if dep_var not in df.columns:
        raise ValueError(f"Variável dependente '{dep_var}' não encontrada no DataFrame.")
    if not exog_unique:
        raise ValueError("Selecione ao menos uma variável explicativa válida.")

    needed_cols = [entity_col, time_col, dep_var] + exog_unique
    sub = df[needed_cols].copy()
    sub[dep_var] = pd.to_numeric(sub[dep_var], errors="coerce").astype("float64")
    for c in exog_unique:
        sub[c] = pd.to_numeric(sub[c], errors="coerce").astype("float64")

    sub = sub.dropna(subset=[dep_var] + exog_unique).reset_index(drop=True)
    n_obs = len(sub)
    n_entities = int(sub[entity_col].nunique())
    n_times = int(sub[time_col].nunique())

    if n_obs < len(exog_unique) + 5 or n_entities < 2:
        raise ValueError(
            f"Amostra insuficiente para estimação em '{spec_name}' "
            f"(N={n_obs}, Municípios={n_entities})."
        )

    if HAS_LINEARMODELS:
        panel_df = sub.set_index([entity_col, time_col])
        y_s = panel_df[dep_var]
        X_df = panel_df[exog_unique]

        model = PanelOLS(
            dependent=y_s,
            exog=X_df,
            entity_effects=entity_effects,
            time_effects=time_effects,
            drop_absorbed=True,
            check_rank=False,
        )
        res = model.fit(cov_type="clustered", cluster_entity=True)

        params = res.params
        std_errors = res.std_errors
        tstats = res.tstats
        pvalues = res.pvalues
        ci = res.conf_int(level=0.95)

        kept_vars = list(params.index)
        absorbed_vars = [c for c in exog_unique if c not in kept_vars]

        coef_rows = []
        for var in kept_vars:
            coef_rows.append({
                "Especificação": spec_name,
                "Variável Dependente": dep_var,
                "Variável": var,
                "Coeficiente": float(params[var]),
                "Erro-Padrão (Cluster)": float(std_errors[var]),
                "Estatística t": float(tstats[var]),
                "p-valor": float(pvalues[var]),
                "IC 95% Inf": float(ci.loc[var, "lower"]),
                "IC 95% Sup": float(ci.loc[var, "upper"]),
                "N": int(res.nobs),
                "Municípios (Clusters)": n_entities,
                "Anos": n_times,
                "R² Within": float(res.rsquared_within),
                "R² Overall": float(res.rsquared_overall),
                "R² Between": float(res.rsquared_between),
                "F-Stat": float(res.f_statistic.stat) if res.f_statistic is not None else np.nan,
                "F p-valor": float(res.f_statistic.pval) if res.f_statistic is not None else np.nan,
            })

        return {
            "spec_name": spec_name,
            "dep_var": dep_var,
            "coef_df": pd.DataFrame(coef_rows),
            "nobs": int(res.nobs),
            "n_entities": n_entities,
            "n_times": n_times,
            "r2_within": float(res.rsquared_within),
            "r2_overall": float(res.rsquared_overall),
            "r2_between": float(res.rsquared_between),
            "f_stat": float(res.f_statistic.stat) if res.f_statistic is not None else np.nan,
            "f_pval": float(res.f_statistic.pval) if res.f_statistic is not None else np.nan,
            "entity_effects": entity_effects,
            "time_effects": time_effects,
            "absorbed_vars": absorbed_vars,
        }

    # Fallback via Double-Demeaned + statsmodels.OLS com ajuste exato de graus de liberdade
    mode = (
        "double_demeaned"
        if (entity_effects and time_effects)
        else ("within_entity" if entity_effects else "pooled")
    )
    dm = transform_within(sub, [dep_var] + exog_unique, mode=mode, entity_col=entity_col, time_col=time_col)

    stds = dm[exog_unique].std(ddof=1)
    kept_vars = [c for c in exog_unique if stds[c] > 1e-10]
    absorbed_vars = [c for c in exog_unique if c not in kept_vars]

    y_dm = dm[dep_var].to_numpy(dtype="float64")
    X_dm = dm[kept_vars].to_numpy(dtype="float64")

    ols_mod = sm.OLS(y_dm, X_dm)
    # Ajuste de graus de liberdade para os efeitos fixos absorvidos
    n_fe = (n_entities if entity_effects else 0) + (n_times - 1 if time_effects else 0)
    ols_Mod_df_resid = max(1, n_obs - len(kept_vars) - n_fe)
    ols_mod.df_resid = ols_Mod_df_resid

    res = ols_mod.fit(cov_type="cluster", cov_kwds={"groups": sub[entity_col].to_numpy()})

    # Cálculo manual de R² Within
    tss_w = float(np.sum((y_dm - np.mean(y_dm)) ** 2))
    rss_w = float(np.sum(res.resid ** 2))
    r2_within = 1.0 - (rss_w / tss_w) if tss_w > 0 else np.nan

    t_crit = stats.t.ppf(0.975, df=max(1, n_entities - 1))
    coef_rows = []
    for idx, var in enumerate(kept_vars):
        b = float(res.params[idx])
        se = float(res.bse[idx])
        t_val = float(res.tvalues[idx])
        p_val = float(res.pvalues[idx])
        coef_rows.append({
            "Especificação": spec_name,
            "Variável Dependente": dep_var,
            "Variável": var,
            "Coeficiente": b,
            "Erro-Padrão (Cluster)": se,
            "Estatística t": t_val,
            "p-valor": p_val,
            "IC 95% Inf": b - t_crit * se,
            "IC 95% Sup": b + t_crit * se,
            "N": n_obs,
            "Municípios (Clusters)": n_entities,
            "Anos": n_times,
            "R² Within": r2_within,
            "R² Overall": np.nan,
            "R² Between": np.nan,
            "F-Stat": np.nan,
            "F p-valor": np.nan,
        })

    return {
        "spec_name": spec_name,
        "dep_var": dep_var,
        "coef_df": pd.DataFrame(coef_rows),
        "nobs": n_obs,
        "n_entities": n_entities,
        "n_times": n_times,
        "r2_within": r2_within,
        "r2_overall": np.nan,
        "r2_between": np.nan,
        "f_stat": np.nan,
        "f_pval": np.nan,
        "entity_effects": entity_effects,
        "time_effects": time_effects,
        "absorbed_vars": absorbed_vars,
    }


def _stars(pval: float) -> str:
    if pd.isna(pval):
        return ""
    if pval < 0.01:
        return "***"
    if pval < 0.05:
        return "**"
    if pval < 0.10:
        return "*"
    return ""


def _fmt_num(val: float, digits: int = 4) -> str:
    if pd.isna(val):
        return "--"
    abs_v = abs(val)
    if abs_v == 0:
        return f"{0.0:.{digits}f}"
    if abs_v < 1e-4 or abs_v >= 1e5:
        return f"{val:.3e}"
    return f"{val:.{digits}f}"


def run_horse_race(
    df: pd.DataFrame,
    specs: Sequence[SpecificationConfig],
    entity_col: str = "codigo_ibge",
    time_col: str = "ano",
) -> Tuple[pd.DataFrame, pd.DataFrame, List[Dict[str, object]]]:
    """Executa uma bateria ("Horse Race") de especificações de Efeitos Fixos lado a lado.

    Retorna:
    1. `long_df`: DataFrame empilhado com todos os coeficientes, erros-padrão, estatística t,
       p-valor, IC 95% (`IC 95% Inf`, `IC 95% Sup`), N e R² Within (pronto para Forest Plot e download CSV).
    2. `wide_df`: Tabela comparativa lado a lado em formato acadêmico (coeficientes com estrelas
       e erros-padrão entre parênteses + estatísticas de ajuste do modelo).
    3. `raw_results`: Lista de dicionários detalhados por especificação.
    """
    work_df = df.copy()
    raw_results: List[Dict[str, object]] = []
    long_frames: List[pd.DataFrame] = []

    for spec in specs:
        exog_list: List[str] = []
        exog_list.extend(spec.x1x2_vars)
        exog_list.extend(spec.x3_vars)

        for x1x2_c, x3_c in spec.triple_interactions:
            if x1x2_c in work_df.columns and x3_c in work_df.columns:
                s_tri, tri_name = build_triple_interaction_column(
                    work_df,
                    x1x2_c,
                    x3_c,
                    standardize_x3=spec.standardize_x3_in_triple,
                )
                work_df[tri_name] = s_tri
                exog_list.append(tri_name)

        exog_list.extend(spec.control_vars)

        res_dict = estimate_twoway_fe(
            df=work_df,
            dep_var=spec.dep_var,
            exog_vars=exog_list,
            entity_col=entity_col,
            time_col=time_col,
            entity_effects=spec.entity_effects,
            time_effects=spec.time_effects,
            spec_name=spec.name,
        )
        raw_results.append(res_dict)
        long_frames.append(res_dict["coef_df"])

    long_df = pd.concat(long_frames, ignore_index=True) if long_frames else pd.DataFrame()

    # Construir tabela lado a lado (Wide Academic Format)
    all_vars: List[str] = []
    for r in raw_results:
        for v in r["coef_df"]["Variável"].tolist():
            if v not in all_vars:
                all_vars.append(v)

    wide_rows = []
    for var in all_vars:
        row_b = {"Variável / Estatística": var, "Tipo": "Coeficiente"}
        row_se = {"Variável / Estatística": f"   ({var} — EP Cluster)", "Tipo": "Erro-Padrão"}
        for r in raw_results:
            sname = r["spec_name"]
            cdf = r["coef_df"]
            match = cdf.loc[cdf["Variável"] == var]
            if not match.empty:
                b = float(match["Coeficiente"].iloc[0])
                se = float(match["Erro-Padrão (Cluster)"].iloc[0])
                pv = float(match["p-valor"].iloc[0])
                t_st = float(match["Estatística t"].iloc[0])
                row_b[sname] = f"{_fmt_num(b)}{_stars(pv)}"
                row_se[sname] = f"({_fmt_num(se)}) [t={t_st:.2f}, p={pv:.3f}]"
            else:
                row_b[sname] = "--"
                row_se[sname] = ""
        wide_rows.append(row_b)
        wide_rows.append(row_se)

    # Linhas de rodapé do painel
    footer_defs = [
        ("Variável Dependente", lambda r: str(r["dep_var"])),
        ("Observações (N)", lambda r: f"{r['nobs']:,}"),
        ("Municípios (Clusters)", lambda r: f"{r['n_entities']}"),
        ("Anos", lambda r: f"{r['n_times']}"),
        ("R² Within", lambda r: f"{r['r2_within']:.4f}" if pd.notna(r["r2_within"]) else "--"),
        ("R² Overall", lambda r: f"{r['r2_overall']:.4f}" if pd.notna(r["r2_overall"]) else "--"),
        ("Estatística F (Within)", lambda r: f"{r['f_stat']:.2f} (p={r['f_pval']:.3f})" if pd.notna(r["f_stat"]) else "--"),
        ("EF Município (codigo_ibge)", lambda r: "Sim" if r["entity_effects"] else "Não"),
        ("EF Ano (ano)", lambda r: "Sim" if r["time_effects"] else "Não"),
    ]
    for label, fn in footer_defs:
        frow = {"Variável / Estatística": label, "Tipo": "Diagnóstico"}
        for r in raw_results:
            frow[r["spec_name"]] = fn(r)
        wide_rows.append(frow)

    wide_df = pd.DataFrame(wide_rows)
    return long_df, wide_df, raw_results


def export_horse_race_to_latex(
    raw_results: Sequence[Dict[str, object]],
    caption: str = "Modelos de Efeitos Fixos Two-Way: Retornos Esperados, Capacidade Produtiva e Condicionamento Institucional (H1, H1-a e H1-b)",
    label: str = "tab:reg_h1_chap1",
) -> str:
    """Exporta os resultados do Horse Race Econométrico para uma tabela LaTeX `booktabs` pronta para a tese."""
    if not raw_results:
        return "% Nenhum modelo estimado."

    def _esc(text: str) -> str:
        return (
            str(text)
            .replace("\\", "\\textbackslash{}")
            .replace("_", "\\_")
            .replace("%", "\\%")
            .replace("&", "\\&")
            .replace("#", "\\#")
        )

    all_vars: List[str] = []
    for r in raw_results:
        for v in r["coef_df"]["Variável"].tolist():
            if v not in all_vars:
                all_vars.append(v)

    n_models = len(raw_results)
    col_spec = "l" + "c" * n_models
    headers = " & ".join([f"({i+1}) {_esc(r['spec_name'])}" for i, r in enumerate(raw_results)])
    dep_headers = " & ".join([f"\\texttt{{{_esc(r['dep_var'])}}}" for r in raw_results])

    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        "\\footnotesize",
        f"\\begin{{tabular}}{{{col_spec}}}",
        "\\toprule",
        f"Variável Explicativa & {headers} \\\\",
        f"Var. Dependente ($Y_{{it}}$) & {dep_headers} \\\\",
        "\\midrule",
    ]

    for var in all_vars:
        b_cells = []
        se_cells = []
        for r in raw_results:
            cdf = r["coef_df"]
            match = cdf.loc[cdf["Variável"] == var]
            if not match.empty:
                b = float(match["Coeficiente"].iloc[0])
                se = float(match["Erro-Padrão (Cluster)"].iloc[0])
                pv = float(match["p-valor"].iloc[0])
                b_cells.append(f"{_fmt_num(b)}$^{{{_stars(pv)}}}$")
                se_cells.append(f"({_fmt_num(se)})")
            else:
                b_cells.append("--")
                se_cells.append("")
        lines.append(f"{_esc(var)} & " + " & ".join(b_cells) + " \\\\")
        lines.append(" & " + " & ".join(se_cells) + " \\\\[2pt]")

    lines.append("\\midrule")
    obs_cells = " & ".join([f"{r['nobs']:,}" for r in raw_results])
    muni_cells = " & ".join([f"{r['n_entities']}" for r in raw_results])
    r2w_cells = " & ".join([f"{r['r2_within']:.4f}" if pd.notna(r["r2_within"]) else "--" for r in raw_results])
    fe_i_cells = " & ".join(["Sim" if r["entity_effects"] else "Não" for r in raw_results])
    fe_t_cells = " & ".join(["Sim" if r["time_effects"] else "Não" for r in raw_results])

    lines.extend([
        f"Observações ($N$) & {obs_cells} \\\\",
        f"Municípios (Clusters) & {muni_cells} \\\\",
        f"$R^2$ Within & {r2w_cells} \\\\",
        f"Efeitos Fixos de Município & {fe_i_cells} \\\\",
        f"Efeitos Fixos de Ano & {fe_t_cells} \\\\",
        "\\bottomrule",
        "\\end{tabular}",
        "\\begin{tablenotes}[flushleft]",
        "\\footnotesize",
        "\\item \\textit{Nota:} Erros-padrão robustos e clusterizados ao nível de município (\\texttt{codigo\\_ibge}) entre parênteses. "
        "Significância estatística: $^{*}p<0,10$; $^{**}p<0,05$; $^{***}p<0,01$. Estimativas mostram associações condicionais intra-município.",
        "\\end{tablenotes}",
        "\\end{table}",
    ])
    return "\n".join(lines)

