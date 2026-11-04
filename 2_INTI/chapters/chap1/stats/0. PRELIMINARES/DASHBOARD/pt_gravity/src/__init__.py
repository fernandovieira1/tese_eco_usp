"""Pacote modular do Dashboard Econométrico e EDA em Painel — Capítulo 1 (Tese USP)."""

from .data_loader import (
    DEFAULT_CSV_PATH,
    THEORETICAL_BLOCKS,
    categorize_columns,
    get_column_block,
    load_raw_panel,
    apply_ibama_imputation,
    get_ibama_imputation_audit,
    filter_panel_data,
    get_friendly_label,
)
from .panel_metrics import (
    compute_panel_descriptive_table,
    export_descriptive_to_latex,
    compute_vif_table,
    compute_correlation_matrix,
    transform_within,
    compute_missing_summary_by_year,
    compute_sample_loss_comparison,
    compute_univariate_deep_profile,
    compute_lorenz_curves,
    compute_municipal_ranking,
    compute_structural_land_transition,
    compute_multivariate_regimes_h1,
    compute_municipal_pca_typology,
)
from .econometric_lab import (
    estimate_twoway_fe,
    run_horse_race,
    export_horse_race_to_latex,
)

__all__ = [
    "DEFAULT_CSV_PATH",
    "THEORETICAL_BLOCKS",
    "categorize_columns",
    "get_column_block",
    "load_raw_panel",
    "apply_ibama_imputation",
    "get_ibama_imputation_audit",
    "filter_panel_data",
    "get_friendly_label",
    "compute_panel_descriptive_table",
    "export_descriptive_to_latex",
    "compute_vif_table",
    "compute_correlation_matrix",
    "transform_within",
    "compute_missing_summary_by_year",
    "compute_sample_loss_comparison",
    "compute_univariate_deep_profile",
    "compute_lorenz_curves",
    "compute_municipal_ranking",
    "compute_structural_land_transition",
    "compute_multivariate_regimes_h1",
    "compute_municipal_pca_typology",
    "estimate_twoway_fe",
    "run_horse_race",
    "export_horse_race_to_latex",
]

