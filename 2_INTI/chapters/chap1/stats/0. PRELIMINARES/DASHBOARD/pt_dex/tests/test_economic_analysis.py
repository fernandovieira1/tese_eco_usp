"""Economic summaries: independent numerical oracles and real UI paths.

Only synthetic fixtures and read-only access to the supplied panel are used.
Run alongside test_dashboard.py with ``python -m unittest discover -s tests -v``.
"""

from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd
import statsmodels.api as sm

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from src.economic_metrics import (
    economic_portrait, grouped_hypothesis, multivariate_partial, univariate_summary,
)
from src.data_loader import flag_mask, load_panel


def economic_panel():
    """Six municipalities, unequal stocks, a zero conversion and unbalanced support."""
    d = pd.MultiIndex.from_product(
        [range(1, 7), range(2001, 2005)], names=["codigo_ibge", "ano"]
    ).to_frame(index=False)
    d = d.loc[~((d.codigo_ibge == 6) & (d.ano == 2002))].reset_index(drop=True)
    d["bioma_dominante"] = np.where(d.codigo_ibge.le(3), "Amazônia", "Cerrado")
    d["capacidade_z__soja__gaez_sxHr0_soy"] = d.codigo_ibge.map({1: 1, 2: 1, 3: 1, 4: 2, 5: 3, 6: 3})
    d["ln_preco_real_usd2024_media_anual_lag1__soja"] = d.ano.map({2001: 2, 2002: 2, 2003: 4, 2004: 6})
    d["n_autos_flora_lag1__ibama_informada"] = (d.codigo_ibge + d.ano) % 4
    d["y_nativa_inicial_ha"] = 100.0 * d.codigo_ibge
    d["conversao_ha__agricultura"] = ((d.codigo_ibge + d.ano) % 5).astype(float)
    d["conversao_ha__pastagem"] = ((2 * d.codigo_ibge + d.ano) % 7).astype(float)
    for destination in ["agricultura", "pastagem"]:
        d[f"taxa_conversao__{destination}"] = d[f"conversao_ha__{destination}"] / d.y_nativa_inicial_ha
    d["nativa_ha"] = 200.0 * d.codigo_ibge - d.ano + 2000
    d["agricultura_ha"] = 10.0 * d.codigo_ibge + 2 * (d.ano - 2000)
    d["pastagem_ha"] = 25.0 * d.codigo_ibge + d.ano - 2000
    d["y_area_total_ha"] = 300.0 * d.codigo_ibge
    d["area_referencia_ha"] = d.y_area_total_ha
    return d


def regression_panel():
    """Unbalanced and confounded panel with missing controls for a FWL oracle."""
    rng = np.random.default_rng(41065)
    d = pd.MultiIndex.from_product(
        [range(14), range(2001, 2010)], names=["codigo_ibge", "ano"]
    ).to_frame(index=False)
    d = d.loc[(d.codigo_ibge + 2 * d.ano) % 11 != 0].reset_index(drop=True)
    d["bioma_dominante"] = np.where(d.codigo_ibge.le(6), "Amazônia", "Cerrado")
    d["z"] = rng.normal(size=len(d))
    d["w"] = rng.normal(size=len(d))
    d["x"] = .7 * d.z + rng.normal(size=len(d))
    d["y"] = 2.3 * d.x - 1.4 * d.z + .6 * d.w + d.codigo_ibge / 2 + .2 * (d.ano - 2000) + rng.normal(scale=.3, size=len(d))
    d.loc[[1, 7, 14], "z"] = np.nan
    return d


class EconomicPortraitTests(unittest.TestCase):
    def test_paired_exposure_weighting_differs_from_simple_mean(self):
        d = economic_panel()
        original = d.copy(deep=True)
        result = economic_portrait(d)
        rows = result["destinations"].set_index("destination")
        for destination in ["agricultura", "pastagem"]:
            rate, area = f"taxa_conversao__{destination}", f"conversao_ha__{destination}"
            row = rows.loc[destination]
            self.assertAlmostEqual(row.weighted_rate, d[area].sum() / d.y_nativa_inicial_ha.sum())
            self.assertAlmostEqual(row.mean_rate, d[rate].mean())
            self.assertAlmostEqual(row.conversion_ha, d[area].sum())
            self.assertEqual(row.nobs, len(d))
            self.assertAlmostEqual(row.zero_pct, 100 * d[rate].eq(0).mean())
        self.assertNotAlmostEqual(rows.loc["agricultura", "weighted_rate"], rows.loc["agricultura", "mean_rate"])
        self.assertAlmostEqual(rows.share_two_destinations.sum(), 1)
        pd.testing.assert_frame_equal(d, original)

    def test_both_destinations_use_identical_common_support(self):
        d = economic_panel()
        d.loc[0, "conversao_ha__pastagem"] = np.nan
        d.loc[1, "taxa_conversao__agricultura"] = np.nan
        d.loc[2, "y_nativa_inicial_ha"] = 0
        d.loc[3, "conversao_ha__agricultura"] = -1
        result = economic_portrait(d)
        self.assertEqual(len(result["sample"]), len(d) - 4)
        self.assertTrue(result["destinations"].nobs.eq(len(d) - 4).all())
        expected = d.iloc[4:]
        self.assertTrue(result["destinations"].denominator_ha_year.eq(expected.y_nativa_inicial_ha.sum()).all())

    def test_concentration_counts_municipalities_and_uses_cumulative_flows(self):
        d = economic_panel()
        result = economic_portrait(d)
        curve = result["concentration"].query("destination == 'total'")
        expected = d.assign(total=d.conversao_ha__agricultura + d.conversao_ha__pastagem).groupby("codigo_ibge").total.sum().sort_values(ascending=False)
        self.assertEqual(len(curve), d.codigo_ibge.nunique())
        np.testing.assert_allclose(curve.conversion_ha, expected.to_numpy())
        np.testing.assert_allclose(curve.cumulative_share, expected.cumsum().to_numpy() / expected.sum())
        summary = result["concentration_summary"].set_index("destination").loc["total"]
        self.assertEqual(summary.top_n, 1)
        self.assertAlmostEqual(summary.top10_share, expected.iloc[0] / expected.sum())

    def test_balanced_option_holds_municipal_composition_constant(self):
        d = economic_panel()
        result = economic_portrait(d, balanced=True)
        sample = result["sample"]
        self.assertEqual(sample.codigo_ibge.nunique(), 5)
        self.assertEqual(len(sample), 20)
        self.assertEqual(sample.groupby("codigo_ibge").ano.nunique().unique().tolist(), [4])

    def test_stock_snapshot_uses_latest_year_and_same_three_class_coverage(self):
        d = economic_panel()
        d.loc[(d.codigo_ibge == 6) & (d.ano == 2004), "pastagem_ha"] = np.nan
        result = economic_portrait(d)
        stock = result["stocks"].set_index("use")
        expected = d.loc[d.ano.eq(2004) & d.codigo_ibge.ne(6)]
        self.assertTrue(stock.ano.eq(2004).all())
        self.assertTrue(stock.n_entities.eq(5).all())
        for use in ["nativa", "agricultura", "pastagem"]:
            self.assertAlmostEqual(stock.loc[use, "area_ha"], expected[f"{use}_ha"].sum())
            self.assertAlmostEqual(stock.loc[use, "share_reference"], expected[f"{use}_ha"].sum() / expected.area_referencia_ha.sum())

    def test_reference_year_absent_after_quality_filter_cannot_be_ignored_by_balancing(self):
        reference = economic_panel()
        sample = reference.loc[reference.ano.ne(2001)]
        result = economic_portrait(sample, reference=reference, balanced=True)
        self.assertTrue(result["sample"].empty)
        self.assertEqual(result["metadata"]["target_years"], [2001, 2002, 2003, 2004])
        self.assertTrue(result["destinations"].weighted_rate.isna().all())

    def test_stock_trajectory_keeps_a_complete_common_municipal_cohort(self):
        d = economic_panel()
        d.loc[(d.codigo_ibge == 5) & (d.ano == 2003), "nativa_ha"] = np.nan
        d.loc[(d.codigo_ibge == 4) & (d.ano == 2001), "area_referencia_ha"] = 0
        result = economic_portrait(d)
        trajectory = result["stocks_annual"]
        self.assertEqual(len(trajectory), 4 * 3)
        self.assertTrue(trajectory.n_entities.eq(3).all())
        for row in trajectory.itertuples():
            expected = d.loc[d.ano.eq(row.ano) & d.codigo_ibge.le(3)]
            self.assertAlmostEqual(row.area_ha, expected[f"{row.use}_ha"].sum())
            self.assertAlmostEqual(row.reference_ha, expected.area_referencia_ha.sum())


class UnivariateEconomicTests(unittest.TestCase):
    def test_latex_exports_mathematical_group_labels_without_font_gaps(self):
        from src.presentation import booktabs
        table = pd.DataFrame({"Grupo": ["Registro ≤ mediana", "Δln × capacidade"], "R²": [0.2, 0.4]})
        result = booktabs(table, "Contraste P75 − P25", "x_1 & y (%)")
        for command in [r"$\leq$", r"$\Delta$", r"$\times$", r"$^2$", r"$-$", r"x\_1", r"\&", r"\%"]:
            self.assertIn(command, result)
        self.assertNotIn("≤", result)

    def test_domain_units_distinguish_aptitude_yield_and_commodity_quotes(self):
        from src.economic_views import variable_unit
        expected = {
            "capacidade_valor__soja__gaez_sxHr0_soy": "índice de aptidão GAEZ (0–10.000)",
            "capacidade_valor__soja__gaez_yxHr0_soy": "kg de matéria seca/ha",
            "capacidade_valor__soja__pam_1991_2000_min7": "kg/ha",
            "capacidade_z__soja__gaez_sxHr0_soy": "desvios-padrão (z)",
            "preco_real_usd2024_media_anual_lag1__soja": "USD de 2024/t",
            "preco_real_usd2024_media_anual_lag1__carne_bovina": "USD de 2024/kg",
            "dln_preco_real_usd2024_media_anual_lag1__milho": "variação logarítmica (Δln)",
        }
        for variable, unit in expected.items():
            with self.subTest(variable=variable):
                self.assertEqual(variable_unit(variable), unit)

    def test_auto_uses_one_observation_per_municipality_for_fixed_capacity(self):
        d = economic_panel()
        variable = "capacidade_z__soja__gaez_sxHr0_soy"
        result = univariate_summary(d, variable)
        expected = d.groupby("codigo_ibge")[variable].first()
        self.assertEqual(result["stats"]["n_valid"], 6)
        self.assertEqual(len(result["sample"]), 6)
        self.assertAlmostEqual(result["stats"]["mean"], expected.mean())

    def test_auto_common_prices_count_years_not_municipality_repetitions(self):
        d = economic_panel()
        variable = "ln_preco_real_usd2024_media_anual_lag1__soja"
        result = univariate_summary(d, variable)
        self.assertEqual(result["stats"]["n_valid"], 4)
        self.assertAlmostEqual(result["stats"]["mean"], 3.5)
        self.assertEqual(len(result["sample"]), 4)

    def test_missing_zero_and_negative_are_distinct_and_finite(self):
        d = economic_panel().iloc[:8].copy()
        d["signed_variable"] = [-2.0, -1, 0, 0, 1, np.nan, np.inf, -np.inf]
        result = univariate_summary(d, "signed_variable")
        stats = result["stats"]
        self.assertEqual(stats["n_total"], 8)
        self.assertEqual(stats["n_valid"], 5)
        self.assertEqual(stats["n_missing"], 3)
        self.assertEqual(stats["n_zero"], 2)
        self.assertAlmostEqual(stats["zero_pct"], 40)
        self.assertAlmostEqual(stats["missing_pct"], 37.5)
        self.assertAlmostEqual(stats["mean"], -.4)
        self.assertEqual(stats["min"], -2)

    def test_auto_refuses_inconsistent_common_prices_and_preserves_changing_capacity(self):
        d = economic_panel()
        price = "ln_preco_real_usd2024_media_anual_lag1__soja"
        capacity = "capacidade_z__soja__gaez_sxHr0_soy"
        d.loc[0, price] += 1
        with self.assertRaisesRegex(ValueError, "por ano"):
            univariate_summary(d, price)
        d.loc[0, capacity] += 1
        result = univariate_summary(d, capacity)
        self.assertEqual(result["metadata"]["unit"], "municipality_year")
        self.assertEqual(result["stats"]["n_valid"], len(d))


class GroupedHypothesisTests(unittest.TestCase):
    capacity = "capacidade_z__soja__gaez_sxHr0_soy"
    price = "ln_preco_real_usd2024_media_anual_lag1__soja"
    institution = "n_autos_flora_lag1__ibama_informada"

    def test_quantile_ties_and_price_threshold_use_natural_units(self):
        d = economic_panel()
        result = grouped_hypothesis(d, self.capacity, self.price, group_count=3)
        sample = result["sample"]
        self.assertEqual(result["metadata"]["price_threshold"], 3)
        self.assertNotEqual(result["metadata"]["price_threshold"], d[self.price].median())
        self.assertTrue(sample.groupby(self.capacity).capacity_group.nunique().eq(1).all())
        self.assertTrue(sample.groupby("codigo_ibge").capacity_group.nunique().eq(1).all())
        self.assertEqual(result["metadata"]["capacity_entities"], 6)
        self.assertEqual(result["metadata"]["price_years"], 4)
        self.assertEqual(int(result["table"].nobs.sum()), len(d))

    def test_institution_cells_exclude_unknown_and_negative_without_imputing_zero(self):
        d = economic_panel()
        d.loc[0, self.institution] = np.nan
        d.loc[1, self.institution] = -1
        result = grouped_hypothesis(d, self.capacity, self.price, institution=self.institution)
        sample = result["sample"]
        self.assertEqual(len(sample), len(d) - 2)
        self.assertEqual(result["metadata"]["n_missing_inputs"], 1)
        zero_sample = sample.loc[sample.institution_group.eq("Registro igual a zero")]
        self.assertTrue(zero_sample[self.institution].eq(0).all())
        self.assertEqual(len(zero_sample), int(d[self.institution].eq(0).sum()))
        keys = ["capacity_group", "price_group", "institution_group"]
        expected = sample.groupby(keys).taxa_conversao__agricultura.mean()
        actual = result["table"].set_index(keys).mean_y
        self.assertEqual(actual.index.tolist(), expected.index.tolist())
        np.testing.assert_allclose(actual.to_numpy(), expected.to_numpy())
        self.assertEqual(int(result["table"].nobs.sum()), len(sample))

    def test_high_low_gaps_are_descriptive_cell_differences(self):
        result = grouped_hypothesis(economic_panel(), self.capacity, self.price)
        for row in result["gaps"].itertuples():
            sample = result["sample"].query("capacity_group == @row.capacity_group")
            means = sample.groupby("price_group").taxa_conversao__agricultura.mean()
            expected = means[result["metadata"]["price_high_label"]] - means[result["metadata"]["price_low_label"]]
            self.assertAlmostEqual(row.gap_mean_y, expected)
            self.assertEqual(row.n_low + row.n_high, len(sample))

    def test_constant_capacity_and_single_price_regime_do_not_create_fake_groups(self):
        d = economic_panel()
        d[self.capacity] = 1
        d[self.price] = 2
        result = grouped_hypothesis(d, self.capacity, self.price)
        self.assertEqual(result["metadata"]["actual_groups"], 1)
        self.assertEqual(result["sample"].capacity_group.nunique(), 1)
        self.assertTrue(result["gaps"].gap_mean_y.isna().all())
        self.assertTrue(result["gaps"].n_high.eq(0).all())

    def test_all_missing_capacities_and_duplicate_panel_keys_are_handled_explicitly(self):
        d = economic_panel()
        empty = grouped_hypothesis(d.assign(**{self.capacity: np.nan}), self.capacity, self.price)
        self.assertTrue(empty["sample"].empty)
        self.assertTrue(empty["table"].empty)
        with self.assertRaisesRegex(ValueError, "duplicados"):
            grouped_hypothesis(pd.concat([d, d.iloc[[0]]]), self.capacity, self.price)


class MultivariateEconomicTests(unittest.TestCase):
    def test_fwl_twfe_residuals_and_slope_match_joint_lsdv_on_common_sample(self):
        d = regression_panel()
        original = d.copy(deep=True)
        result = multivariate_partial(d, "y", "x", controls=["z", "w"], mode="twoway")
        sample = d.dropna(subset=["y", "x", "z", "w"])
        nuisance = sm.add_constant(pd.concat([
            pd.get_dummies(sample.codigo_ibge, prefix="i", drop_first=True, dtype=float),
            pd.get_dummies(sample.ano, prefix="t", drop_first=True, dtype=float),
            sample[["z", "w"]]],
            axis=1), has_constant="add")
        values = sample[["x", "y"]].to_numpy()
        expected = values - nuisance.to_numpy() @ np.linalg.lstsq(nuisance, values, rcond=None)[0]
        np.testing.assert_allclose(result["sample"][["x_partial", "y_partial"]], expected, atol=2e-8, rtol=2e-8)
        oracle = sm.OLS(sample.y, pd.concat([nuisance, sample[["x"]]], axis=1)).fit()
        self.assertAlmostEqual(result["slope"], oracle.params["x"], places=9)
        self.assertEqual(result["nobs"], len(sample))
        pd.testing.assert_frame_equal(d, original)

    def test_fwl_pooled_and_entity_match_independent_projection(self):
        d = regression_panel()
        sample = d.dropna(subset=["y", "x", "z"])
        for mode in ["pooled", "entity"]:
            nuisance = sample[["z"]].copy()
            if mode == "entity":
                nuisance = pd.concat([nuisance, pd.get_dummies(sample.codigo_ibge, drop_first=True, dtype=float)], axis=1)
            nuisance = sm.add_constant(nuisance, has_constant="add")
            values = sample[["x", "y"]].to_numpy()
            expected = values - nuisance.to_numpy() @ np.linalg.lstsq(nuisance, values, rcond=None)[0]
            result = multivariate_partial(d, "y", "x", controls=["z"], mode=mode)
            np.testing.assert_allclose(result["sample"][["x_partial", "y_partial"]], expected, atol=2e-9, rtol=2e-9)

    def test_absorbed_prices_and_control_identical_to_x_are_rejected(self):
        d = regression_panel()
        d["year_price"] = d.ano.astype(float)
        with self.assertRaises(ValueError):
            multivariate_partial(d, "y", "year_price", mode="twoway")
        d["copy_x"] = 2 * d.x
        with self.assertRaises(ValueError):
            multivariate_partial(d, "y", "x", controls=["copy_x"])

    def test_empty_and_single_year_twfe_cannot_fake_partial_relationship(self):
        d = regression_panel()
        with self.assertRaises(ValueError):
            multivariate_partial(d.iloc[:2], "y", "x")
        with self.assertRaises(ValueError):
            multivariate_partial(d.loc[d.ano.eq(2001)], "y", "x")


class EconomicStreamlitTests(unittest.TestCase):
    def app(self):
        from streamlit.testing.v1 import AppTest
        return AppTest.from_file(str(APP_DIR / "app.py"), default_timeout=90).run()

    def assert_app_ok(self, app):
        self.assertFalse(app.exception, [exception.message for exception in app.exception])

    def test_economic_tabs_open_and_distribution_switches_units(self):
        app = self.app()
        self.assert_app_ok(app)
        self.assertEqual(len(app.tabs), 8)
        self.assertTrue(any("econômico" in tab.label.lower() for tab in app.tabs))
        self.assertTrue(any("distribuiç" in tab.label.lower() for tab in app.tabs))
        app.selectbox(key="uni_unit").set_value("Média por município").run()
        self.assert_app_ok(app)
        app.selectbox(key="uni_unit").set_value("Média por ano")
        app.checkbox(key="uni_by_biome").set_value(False)
        app.checkbox(key="econ_balanced").set_value(False)
        app.run()
        self.assert_app_ok(app)

    def test_multivariate_modes_and_institutional_stratification(self):
        app = self.app()
        app.toggle(key="impute").set_value(True)
        app.toggle(key="log_ibama").set_value(True)
        app.run()
        self.assert_app_ok(app)
        app.selectbox(key="rel_institution").set_value("n_autos_flora_lag1__ibama_informada")
        app.slider(key="rel_group_count").set_value(4)
        app.checkbox(key="rel_balanced").set_value(False)
        app.multiselect(key="partial_controls").set_value([])
        app.run()
        self.assert_app_ok(app)
        app.selectbox(key="partial_x").set_value("ln_preco_real_usd2024_media_anual_lag1__soja").run()
        self.assert_app_ok(app)

    def test_pantanal_and_single_year_filters_are_safe_for_new_tabs(self):
        app = self.app()
        app.multiselect(key="biomes").set_value(["Pantanal"])
        app.slider(key="years").set_value((2020, 2020))
        app.run()
        self.assert_app_ok(app)
        self.assertEqual(len(app.tabs), 8)
        app.toggle(key="quality").set_value(False)
        app.slider(key="years").set_value((2001, 2001)).run()
        self.assert_app_ok(app)

    def test_filtered_partial_comparison_uses_panel_keys_after_noncontiguous_filters(self):
        app = self.app()
        app.multiselect(key="biomes").set_value(["Cerrado"])
        app.slider(key="years").set_value((2005, 2020)).run()
        self.assert_app_ok(app)
        raw = load_panel(APP_DIR / "painel_tese_chap1_pt.csv")
        variables = [app.selectbox(key="partial_y").value, app.selectbox(key="partial_x").value,
                     *app.multiselect(key="partial_controls").value]
        keep = (raw.bioma_dominante.eq("Cerrado") & raw.ano.between(2005, 2020)
                & flag_mask(raw.y_cobertura_completa) & flag_mask(raw.y_flag_denominador_zero, False))
        expected = raw.loc[keep].copy()
        expected = expected.dropna(subset=variables)
        self.assertFalse(expected.index.equals(pd.RangeIndex(len(expected))))
        comparison = next(item.value for item in app.dataframe if "Comparação" in item.value.columns)
        self.assertTrue(comparison["N"].eq(len(expected)).all())
        partial_metric = next(metric for metric in app.metric if metric.label == "Pares na mesma amostra")
        self.assertEqual(int(partial_metric.value), len(expected))


if __name__ == "__main__":
    unittest.main(verbosity=2)
