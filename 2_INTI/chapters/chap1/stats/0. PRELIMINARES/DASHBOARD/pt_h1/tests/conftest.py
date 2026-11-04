import os
import sys
from pathlib import Path

os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import pytest

from h1lab.data import load_data


@pytest.fixture(scope='session')
def real_data():
    return load_data()


@pytest.fixture
def synthetic():
    rng = np.random.default_rng(8021)
    grid = pd.MultiIndex.from_product([[str(5100000 + i) for i in range(12)], range(2001, 2009)], names=['codigo_ibge', 'ano']).to_frame(index=False)
    # Unbalanced, still connected panel, with persistent and annual confounders.
    grid = grid.drop(index=[1, 8, 18, 27, 35, 46, 56, 65]).reset_index(drop=True)
    ids = pd.factorize(grid['codigo_ibge'])[0]
    t = grid['ano'] - 2001
    grid['fixed'] = ids.astype(float)
    grid['price'] = 10 + t.astype(float)
    grid['x'] = rng.normal(size=len(grid)) + ids / 4 + t / 5
    grid['z'] = rng.normal(size=len(grid))
    grid['y'] = 2 + 1.7 * grid['x'] - .8 * grid['z'] + ids + .4 * t + rng.normal(scale=.3, size=len(grid))
    grid['municipio'] = 'Município ' + grid['codigo_ibge']
    grid['bioma_dominante'] = np.where(ids < 6, 'Amazônia', 'Cerrado')
    grid['y_cobertura_completa'] = True
    return grid


@pytest.fixture
def filters():
    return {'years': [2001, 2008], 'biomes': ['Amazônia', 'Cerrado'], 'municipalities': []}
