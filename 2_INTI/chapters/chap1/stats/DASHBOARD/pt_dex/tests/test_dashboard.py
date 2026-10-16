"""Substantive regression tests for the H1 exploratory dashboard.

Run with ``python -m unittest discover -s tests -v`` from the app directory.
Only synthetic fixtures and read-only access to the supplied CSV are used.
"""

from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd
import statsmodels.api as sm

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from src.data_loader import (
    BLOCKS, add_dominant_biome, apply_ibama_treatment, categorize_columns,
    filter_panel, flag_mask, load_panel, validate_panel_keys,
)
from src.panel_metrics import (
    calculate_vif, correlation_matrix, panel_descriptive, within_transform,
)
from src.econometric_lab import build_h1b_specification, fit_twfe, horse_race
from src.presentation import binscatter_data


def unbalanced_panel():
    """Connected, genuinely unbalanced panel with two estimable slopes."""
    rng = np.random.default_rng(741)
    df = pd.MultiIndex.from_product(
        [range(12), range(2001, 2009)], names=["codigo_ibge", "ano"]
    ).to_frame(index=False)
    df = df.loc[~((df.codigo_ibge + 2 * df.ano) % 7 == 0)].reset_index(drop=True)
    df["x"] = rng.normal(size=len(df))
    df["z"] = rng.normal(size=len(df))
    df["fixed"] = df.codigo_ibge / 3
    df["common_year"] = df.ano - 2000
    df["y"] = (1.7 * df.x - .8 * df.z + df.fixed + .3 * df.common_year
               + rng.normal(scale=.4, size=len(df)))
    return df


def dummy_matrix(df):
    entity = pd.get_dummies(df.codigo_ibge, prefix="entity", drop_first=True, dtype=float)
    year = pd.get_dummies(df.ano, prefix="year", drop_first=True, dtype=float)
    return sm.add_constant(pd.concat([entity, year], axis=1), has_constant="add")


class DataTreatmentTests(unittest.TestCase):
    def setUp(self):
        self.current = "n_autos_flora__ibama_informada"
        self.lagged = "n_autos_flora_lag1__ibama_informada"
        self.flag = "flag_sem_registro_identificado__ibama_informada"
        self.df = pd.DataFrame({
            "codigo_ibge": [1, 1, 1, 1, 2, 2, 2, 2],
            "ano": [2001, 2002, 2004, 2005, 2001, 2002, 2003, 2004],
            self.flag: ["True", "False", True, False, False, True, None, False],
            self.current: [np.nan, np.nan, np.nan, 7, np.nan, np.nan, np.nan, 0],
            self.lagged: [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 9, np.nan],
        })

    def test_zero_imputation_respects_true_flags_and_calendar_gaps(self):
        original = self.df.copy(deep=True)
        treated, audit = apply_ibama_treatment(self.df, impute_zeros=True)
        np.testing.assert_allclose(treated[self.current], [0, np.nan, 0, 7, np.nan, 0, np.nan, 0], equal_nan=True)
        np.testing.assert_allclose(treated[self.lagged], [np.nan, 0, np.nan, 0, np.nan, np.nan, 9, np.nan], equal_nan=True)
        pd.testing.assert_frame_equal(self.df, original)
        self.assertEqual(audit.set_index("variavel").loc[self.current, "n_imputados_zero"], 3)
        self.assertEqual(audit.set_index("variavel").loc[self.lagged, "n_imputados_zero"], 2)

    def test_flag_parser_never_treats_false_or_missing_as_true(self):
        flags = pd.Series(["False", "True", pd.NA, 0, 1])
        self.assertEqual(flag_mask(flags).tolist(), [False, True, False, False, True])
        self.assertEqual(flag_mask(flags, False).tolist(), [True, False, False, True, False])

    def test_optional_log_and_disabled_imputation_preserve_missing(self):
        treated, audit = apply_ibama_treatment(self.df, impute_zeros=False, log1p=True)
        np.testing.assert_allclose(treated[self.current], self.df[self.current], equal_nan=True)
        self.assertEqual(int(audit.n_imputados_zero.sum()), 0)
        self.assertAlmostEqual(treated.loc[3, "log1p__" + self.current], np.log(8))
        self.assertEqual(treated.loc[7, "log1p__" + self.current], 0)
        self.assertTrue(pd.isna(treated.loc[0, "log1p__" + self.current]))

    def test_filtering_does_not_erase_known_prior_year_flag(self):
        prepared, _ = apply_ibama_treatment(self.df, impute_zeros=False)
        filtered = filter_panel(prepared, year_range=(2002, 2002))
        treated, _ = apply_ibama_treatment(filtered, impute_zeros=True)
        self.assertEqual(treated.loc[treated.codigo_ibge.eq(1), self.lagged].iloc[0], 0)
        self.assertTrue(pd.isna(treated.loc[treated.codigo_ibge.eq(2), self.lagged].iloc[0]))

    def test_duplicate_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicad"):
            validate_panel_keys(pd.concat([self.df, self.df.iloc[[0]]]))

    def test_biome_argmax_and_missing_shares(self):
        df = pd.DataFrame({"biome_amazonia_share_i": [.8, .1, .1, np.nan],
                           "biome_cerrado_share_i": [.1, .8, .1, .5],
                           "biome_pantanal_share_i": [.1, .1, .8, .5]})
        out = add_dominant_biome(df)
        self.assertEqual(out.bioma_dominante.iloc[:3].tolist(), ["Amazônia", "Cerrado", "Pantanal"])
        self.assertTrue(pd.isna(out.bioma_dominante.iloc[3]))
        self.assertTrue(out.flag_bioma_dominante_invalido.iloc[3])


class RealPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel = load_panel(APP_DIR / "painel_tese_chap1_pt.csv")

    def test_schema_coverage_and_complete_theoretical_classification(self):
        d = self.panel
        self.assertEqual(d.attrs["source_shape"], (3384, 296))
        self.assertEqual(d.codigo_ibge.nunique(), 141)
        self.assertEqual((d.ano.min(), d.ano.max()), (2001, 2024))
        self.assertEqual(int(d.taxa_conversao__agricultura.isna().sum()), 612)
        self.assertEqual(int(d.capacidade_z__soja__pam_1991_2000_min7.isna().sum()), 2256)
        self.assertFalse(d.capacidade_z__soja__gaez_sxHr0_soy.isna().any())
        groups = categorize_columns(d)
        assigned = [column for group in groups.values() for column in group]
        self.assertEqual(tuple(groups), BLOCKS)
        self.assertCountEqual(assigned, d.columns)
        self.assertEqual(len(assigned), len(set(assigned)))

    def test_first_year_ibama_lag_absence_is_preserved(self):
        treated, audit = apply_ibama_treatment(self.panel, impute_zeros=True)
        lag = "n_autos_flora_lag1__ibama_informada"
        first = treated.ano.eq(2001)
        original_missing = self.panel.loc[first, lag].isna()
        self.assertTrue(treated.loc[first, lag].loc[original_missing].isna().all())
        self.assertGreater(audit.n_imputados_zero.sum(), 0)


class PanelMetricTests(unittest.TestCase):
    def test_overall_between_within_use_distinct_panel_definitions(self):
        df = pd.DataFrame({"codigo_ibge": [1, 1, 1, 2, 2], "ano": [1, 2, 3, 1, 3],
                           "x": [1., 3., 5., 10., 14.], "fixed": [7., 7., 7., 9., 9.],
                           "absent": [np.nan] * 5})
        table = panel_descriptive(df, ["x", "fixed", "absent"])
        self.assertEqual(table.loc["x", "n_valid"], 5)
        self.assertAlmostEqual(table.loc["x", "mean"], 6.6)
        self.assertAlmostEqual(table.loc["x", "sd_overall"], np.std([1, 3, 5, 10, 14], ddof=1))
        self.assertAlmostEqual(table.loc["x", "sd_between"], np.std([3, 12], ddof=1))
        self.assertAlmostEqual(table.loc["x", "sd_within"], 2)
        self.assertEqual(table.loc["fixed", "sd_within"], 0)
        self.assertTrue(table.loc["fixed", "time_invariant"])
        self.assertEqual(table.loc["absent", "missing_pct"], 100)
        self.assertTrue(pd.isna(table.loc["absent", "sd_within"]))

    def test_two_way_projection_matches_lsdv_on_unbalanced_common_sample(self):
        df = unbalanced_panel()
        df.loc[[2, 5, 9], "z"] = np.nan
        got = within_transform(df, ["y", "x", "z"], mode="twoway")
        sample = df.dropna(subset=["y", "x", "z"])
        dummies = dummy_matrix(sample).to_numpy()
        values = sample[["y", "x", "z"]].to_numpy()
        expected = values - dummies @ np.linalg.lstsq(dummies, values, rcond=None)[0]
        np.testing.assert_allclose(got[["y", "x", "z"]], expected, atol=2e-9, rtol=2e-9)
        np.testing.assert_allclose(got.groupby("codigo_ibge")[["y", "x", "z"]].mean(), 0, atol=2e-9)
        np.testing.assert_allclose(got.groupby("ano")[["y", "x", "z"]].mean(), 0, atol=2e-9)
        self.assertEqual(got.index.tolist(), sample.index.tolist())

    def test_entity_projection_preserves_only_within_variation(self):
        df = unbalanced_panel()
        got = within_transform(df, ["x", "fixed"], mode="entity")
        np.testing.assert_allclose(got.groupby("codigo_ibge").x.mean(), 0, atol=1e-12)
        np.testing.assert_allclose(got.fixed, 0, atol=1e-12)
        self.assertGreater(got.x.std(), 0)

    def test_vif_marks_perfect_collinearity_and_absorbed_terms(self):
        df = unbalanced_panel()
        df["twice_x"] = 2 * df.x
        table = calculate_vif(df, ["x", "twice_x", "fixed"], mode="entity").set_index("variable")
        self.assertTrue(np.isinf(table.loc["x", "vif"]))
        self.assertTrue(np.isinf(table.loc["twice_x", "vif"]))
        self.assertTrue(pd.isna(table.loc["fixed", "vif"]))
        self.assertIn("absorvida", table.loc["fixed", "status"])
        df["empty"] = np.nan
        empty = calculate_vif(df, ["x", "empty"])
        self.assertTrue(empty.vif.isna().all())
        self.assertTrue(empty.nobs.eq(0).all())

    def test_pearson_spearman_and_joint_sample_are_explicit(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "squared": [1, 4, 9, 16, np.nan]})
        pearson = correlation_matrix(df, ["x", "squared"], method="pearson")
        spearman = correlation_matrix(df, ["x", "squared"], method="spearman")
        self.assertLess(pearson.loc["x", "squared"], 1)
        self.assertAlmostEqual(spearman.loc["x", "squared"], 1)
        self.assertEqual(pearson.attrs["nobs"], 4)
        self.assertTrue((pearson.attrs["pairwise_n"] == 4).all().all())

    def test_absorbed_residual_noise_is_not_mistaken_for_identifying_variation(self):
        df = unbalanced_panel()
        df["tiny_x"] = df.x * 1e-14
        transformed = within_transform(df, ["fixed", "common_year", "tiny_x"], mode="twoway")
        correlation = correlation_matrix(transformed, ["fixed", "common_year", "tiny_x"])
        self.assertTrue(correlation.loc["fixed"].isna().all())
        self.assertTrue(correlation.loc["common_year"].isna().all())
        self.assertAlmostEqual(correlation.loc["tiny_x", "tiny_x"], 1)
        vif = calculate_vif(transformed, ["fixed", "common_year", "tiny_x"]).set_index("variable")
        self.assertTrue(pd.isna(vif.loc["fixed", "vif"]))
        self.assertEqual(vif.loc["tiny_x", "vif"], 1)


class EconometricTests(unittest.TestCase):
    def test_twfe_coefficients_clustered_errors_and_df_match_independent_lsdv(self):
        df = unbalanced_panel()
        df.loc[4, "z"] = np.nan
        fitted = fit_twfe(df, "y", ["x", "z"])
        sample = df.dropna(subset=["y", "x", "z"])
        design = pd.concat([dummy_matrix(sample), sample[["x", "z"]]], axis=1)
        oracle = sm.OLS(sample.y, design).fit(
            cov_type="cluster", cov_kwds={"groups": sample.codigo_ibge, "use_correction": True}
        )
        table = fitted["coefficients"].set_index("term")
        np.testing.assert_allclose(table.loc[["x", "z"], "coefficient"], oracle.params[["x", "z"]], rtol=1e-9, atol=1e-9)
        np.testing.assert_allclose(table.loc[["x", "z"], "std_error"], oracle.bse[["x", "z"]], rtol=1e-8, atol=1e-9)
        self.assertEqual(fitted["diagnostics"]["df_resid"], oracle.df_resid)
        self.assertEqual(fitted["diagnostics"]["nobs"], len(sample))
        self.assertTrue(table.ci_lower.lt(table.coefficient).all())
        self.assertTrue(table.ci_upper.gt(table.coefficient).all())

    def test_absorption_and_exact_dependencies_are_reported(self):
        df = unbalanced_panel()
        df["twice_x"] = 2 * df.x
        result = fit_twfe(df, "y", ["x", "twice_x", "fixed", "common_year"])
        statuses = result["coefficients"].set_index("term").status
        self.assertEqual(statuses["x"], "estimated")
        self.assertEqual(statuses["twice_x"], "collinear")
        self.assertEqual(statuses["fixed"], "absorbed")
        self.assertEqual(statuses["common_year"], "absorbed")
        with self.assertRaises(ValueError):
            fit_twfe(df, "y", ["fixed", "common_year"])

    def test_missing_or_nonidentified_outcomes_are_rejected(self):
        df = unbalanced_panel()
        with self.assertRaises(ValueError):
            fit_twfe(df.assign(y=np.nan), "y", ["x"])
        with self.assertRaises(ValueError):
            fit_twfe(df.assign(y=df.fixed + df.common_year), "y", ["x"])
        with self.assertRaises(ValueError):
            fit_twfe(pd.concat([df, df.iloc[[0]]]), "y", ["x"])

    def test_horse_race_distinguishes_common_own_samples_and_failed_models(self):
        df = unbalanced_panel()
        df.loc[:6, "z"] = np.nan
        specs = {"base": ["x"], "augmented": ["x", "z"]}
        _, common = horse_race(df, "y", specs, common_sample=True)
        _, own = horse_race(df, "y", specs, common_sample=False)
        self.assertTrue(common.status.eq("ok").all())
        self.assertEqual(common.nobs.nunique(), 1)
        self.assertGreater(own.set_index("model").loc["base", "nobs"], own.set_index("model").loc["augmented", "nobs"])
        coefficients, diagnostics = horse_race(df, "y", {"valid": ["x"], "absorbed": ["fixed"]})
        self.assertEqual(diagnostics.set_index("model").loc["absorbed", "status"], "error")
        self.assertEqual(coefficients.model.unique().tolist(), ["valid"])

    def test_h1b_triple_keeps_full_lower_order_hierarchy(self):
        df = unbalanced_panel()
        price = "ln_preco_real_usd2024_media_anual_lag1__soja"
        capacity = "capacidade_z__soja__gaez_sxHr0_soy"
        interaction = "interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z__soja__gaez_sxHr0_soy"
        institutional = "n_autos_flora_lag1__ibama_informada"
        df[price], df[capacity], df[institutional] = df.common_year, df.fixed, df.z
        df[interaction] = df[price] * df[capacity]
        original = df.copy(deep=True)
        built, terms, _ = build_h1b_specification(df, interaction, institutional)
        self.assertEqual(len(terms), 7)
        self.assertTrue(set([price, capacity, interaction, institutional]).issubset(terms))
        triple = next(term for term in terms if term.startswith("tripla__"))
        np.testing.assert_allclose(built[triple], df[price] * df[capacity] * df[institutional])
        products = [term for term in terms if term.startswith("produto__")]
        self.assertEqual(len(products), 2)
        pd.testing.assert_frame_equal(df, original)


class PlotPreparationTests(unittest.TestCase):
    def test_binscatter_line_uses_observations_not_bin_means(self):
        df = unbalanced_panel().assign(bioma_dominante="Amazônia")
        bins, line, summary, removed = binscatter_data(df, "y", "x", "pooled", bins=7)
        oracle = sm.OLS(df.y, sm.add_constant(df.x)).fit()
        self.assertAlmostEqual(summary.iloc[0]["Inclinação OLS"], oracle.params["x"])
        self.assertEqual(int(bins["N no bin"].sum()), len(df))
        self.assertEqual(len(bins), 7)
        self.assertEqual(len(line), 80)
        self.assertEqual(removed, 0)

    def test_trimming_keeps_display_sample_auditable(self):
        df = unbalanced_panel().assign(bioma_dominante="Amazônia")
        df.loc[0, "x"] = 1000
        bins, _, summary, removed = binscatter_data(
            df, "y", "x", "twoway", bins=10, trim_pct=1, leverage=True
        )
        self.assertGreater(removed, 0)
        self.assertEqual(int(summary["N"].sum()) + removed, len(df))
        self.assertEqual(int(bins["N no bin"].sum()) + removed, len(df))


class StreamlitIntegrationTests(unittest.TestCase):
    def app(self):
        from streamlit.testing.v1 import AppTest
        return AppTest.from_file(str(APP_DIR / "app.py"), default_timeout=90).run()

    def assert_app_ok(self, app):
        self.assertFalse(app.exception, [exception.message for exception in app.exception])

    def test_five_tabs_and_real_h1a_h1b_comparison(self):
        app = self.app()
        self.assert_app_ok(app)
        self.assertEqual(len(app.tabs), 8)
        self.assertEqual(app.metric[0].value, "2,772")
        app.button(key="lab_run").click().run()
        self.assert_app_ok(app)
        saved = app.session_state["lab_result"]
        self.assertEqual(len(saved["diagnostics"]), 4)
        self.assertTrue(saved["diagnostics"].status.eq("ok").all())
        self.assertTrue(saved["coefficients"].term.str.startswith("tripla__").any())
        self.assertEqual(saved["diagnostics"].nobs.nunique(), 1)

    def test_global_filters_logging_and_reestimated_combined_models(self):
        app = self.app()
        app.toggle(key="impute").set_value(True)
        app.toggle(key="log_ibama").set_value(True)
        app.slider(key="years").set_value((2005, 2020))
        app.multiselect(key="biomes").set_value(["Cerrado"])
        app.run()
        self.assert_app_ok(app)
        app.selectbox(key="lab_y").set_value("taxa_conversao__pastagem")
        app.selectbox(key="lab_strategy").set_value("Combinar proxies selecionadas")
        app.multiselect(key="lab_ibama").set_value(["log1p__n_autos_flora_lag1__ibama_informada"])
        app.checkbox(key="lab_common").set_value(False)
        app.button(key="lab_run").click().run()
        self.assert_app_ok(app)
        saved = app.session_state["lab_result"]
        self.assertEqual(len(saved["diagnostics"]), 2)
        self.assertTrue(saved["diagnostics"].status.eq("ok").all())
        self.assertTrue(saved["diagnostics"].sample_mode.eq("própria").all())
        self.assertTrue(saved["coefficients"].term.str.contains("log1p__").any())
        app.slider(key="years").set_value((2006, 2020)).run()
        self.assert_app_ok(app)
        self.assertTrue(any("Execute novamente" in item.value for item in app.info))

    def test_double_demeaning_bins_extremes_and_empty_selections(self):
        app = self.app()
        app.selectbox(key="corr_method").set_value("Spearman")
        app.selectbox(key="corr_mode").set_value("Double Demeaned (Município + Ano)")
        app.selectbox(key="bins_mode").set_value("Double Demeaned (Município + Ano)")
        app.slider(key="bins_count").set_value(50)
        app.slider(key="bins_trim").set_value(10.0)
        app.checkbox(key="bins_leverage").set_value(True)
        app.run()
        self.assert_app_ok(app)
        # A time-only price is absorbed by two-way effects and must not crash.
        app.selectbox(key="bins_x").set_value("ln_preco_real_usd2024_media_anual_lag1__soja").run()
        self.assert_app_ok(app)
        self.assertTrue(any("formar bins" in item.value for item in app.info))
        app.multiselect(key="diag_blocks").set_value([])
        app.multiselect(key="time_destinations").set_value([])
        app.multiselect(key="proxy_columns").set_value([])
        app.multiselect(key="lab_interactions").set_value([])
        app.button(key="lab_run").click().run()
        self.assert_app_ok(app)
        self.assertTrue(any("pelo menos uma interação" in item.value for item in app.warning))

    def test_single_year_failure_is_reported_and_empty_biome_filter_is_safe(self):
        app = self.app()
        app.toggle(key="quality").set_value(False)
        app.toggle(key="denominator").set_value(False)
        app.slider(key="years").set_value((2024, 2024)).run()
        self.assert_app_ok(app)
        app.button(key="lab_run").click().run()
        self.assert_app_ok(app)
        self.assertTrue(app.session_state["lab_result"]["diagnostics"].status.eq("error").all())
        app.multiselect(key="biomes").set_value([]).run()
        self.assert_app_ok(app)
        self.assertTrue(any("recorte está vazio" in item.value for item in app.warning))


if __name__ == "__main__":
    unittest.main(verbosity=2)
