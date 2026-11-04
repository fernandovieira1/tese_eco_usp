"""Efeitos escolhidos devem chegar ao PanelOLS; sem ele, nao ha estimativa."""
import importlib
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
import statsmodels.api as sm

SRC = Path(__file__).resolve().parents[1] / 'src'
PACKAGE = 'gravity_estimator_test_src'
package = ModuleType(PACKAGE)
package.__path__ = [str(SRC)]
sys.modules[PACKAGE] = package
models = importlib.import_module(PACKAGE + '.econometric_lab')


def panel():
    rng = np.random.default_rng(18)
    df = pd.MultiIndex.from_product([range(8), range(6)], names=['codigo_ibge', 'ano']).to_frame(index=False)
    df['x'] = df.ano + rng.normal(size=len(df))
    df['y'] = 1.7 * df.x + 5 * df.ano + rng.normal(size=len(df))
    return df


class EconometricTests(unittest.TestCase):
    def test_all_effect_combinations_match_explicit_dummy_slopes(self):
        df = panel().drop(index=[2, 11, 25]).reset_index(drop=True)
        for entity, time in [(False, False), (False, True), (True, False), (True, True)]:
            with self.subTest(entity=entity, time=time):
                effects = []
                if entity:
                    effects.append(pd.get_dummies(df.codigo_ibge, prefix='municipio', dtype=float))
                if time:
                    effects.append(pd.get_dummies(df.ano, prefix='ano', drop_first=entity, dtype=float))
                design = pd.concat([*effects, df[['x']]], axis=1)
                expected = sm.OLS(df.y, design).fit().params['x']
                result = models.estimate_twoway_fe(df, 'y', ['x'], entity_effects=entity, time_effects=time)
                self.assertAlmostEqual(result['coef_df']['Coeficiente'].iloc[0], expected, places=10)
                self.assertEqual(result['entity_effects'], entity)
                self.assertEqual(result['time_effects'], time)
                self.assertEqual(result['nobs'], len(df))

    def test_missing_linearmodels_blocks_estimation_with_installation_hint(self):
        name = PACKAGE + '.missing_dependency'
        spec = importlib.util.spec_from_file_location(name, SRC / 'econometric_lab.py')
        missing = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {name: missing, 'linearmodels': None, 'linearmodels.panel': None}):
            spec.loader.exec_module(missing)
            with self.assertRaisesRegex(ImportError, r'linearmodels.*requirements\.txt'):
                missing.estimate_twoway_fe(panel(), 'y', ['x'], entity_effects=False, time_effects=True)

    def test_horse_race_preserves_year_only_specification(self):
        df = panel()
        original = df.copy(deep=True)
        config = models.SpecificationConfig('Ano', 'y', ['x'], [], [], [], entity_effects=False, time_effects=True)
        long, wide, raw = models.run_horse_race(df, [config])
        design = pd.concat([pd.get_dummies(df.ano, dtype=float), df[['x']]], axis=1)
        expected = sm.OLS(df.y, design).fit().params['x']
        self.assertAlmostEqual(long['Coeficiente'].iloc[0], expected, places=10)
        self.assertTrue(raw[0]['time_effects'])
        self.assertFalse(raw[0]['entity_effects'])
        self.assertEqual(wide.loc[wide['Variável / Estatística'].eq('EF Ano (ano)'), 'Ano'].iloc[0], 'Sim')
        pd.testing.assert_frame_equal(df, original)


if __name__ == '__main__':
    unittest.main()
