"""Cache do CSV deve acompanhar a versao do arquivo no disco."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd
import streamlit as st

spec = importlib.util.spec_from_file_location('gravity_data_loader', Path(__file__).resolve().parents[1] / 'src/data_loader.py')
data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data)


class DataLoaderCacheTests(unittest.TestCase):
    def setUp(self):
        st.cache_data.clear()
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.addCleanup(st.cache_data.clear)
        self.path = Path(temporary.name) / 'painel.csv'
        names = patch.object(data, '_load_municipality_names', return_value={})
        names.start()
        self.addCleanup(names.stop)
        self.write_panel(1.0)

    def write_panel(self, value):
        pd.DataFrame({'codigo_ibge': [5100001], 'ano': [2001],
            'biome_amazonia_share_i': [1.0], 'biome_cerrado_share_i': [0.0],
            'biome_pantanal_share_i': [0.0], 'x': [value]}).to_csv(self.path, index=False)

    def test_unchanged_csv_is_read_only_once(self):
        with patch.object(data.pd, 'read_csv', wraps=pd.read_csv) as read:
            first = data.load_raw_panel(self.path)
            second = data.load_raw_panel(str(self.path))
        self.assertEqual(read.call_count, 1)
        pd.testing.assert_frame_equal(first, second)

    def test_mtime_change_reloads_csv_even_with_same_size(self):
        self.assertEqual(data.load_raw_panel(self.path).x.iloc[0], 1.0)
        before = self.path.stat()
        self.write_panel(9.0)
        os.utime(self.path, ns=(before.st_atime_ns, before.st_mtime_ns + 1_000_000_000))
        self.assertEqual(self.path.stat().st_size, before.st_size)
        self.assertEqual(data.load_raw_panel(self.path).x.iloc[0], 9.0)

    def test_size_change_reloads_csv_even_with_same_mtime(self):
        self.assertEqual(data.load_raw_panel(self.path).x.iloc[0], 1.0)
        before = self.path.stat()
        self.write_panel(99.0)
        os.utime(self.path, ns=(before.st_atime_ns, before.st_mtime_ns))
        self.assertEqual(self.path.stat().st_mtime_ns, before.st_mtime_ns)
        self.assertNotEqual(self.path.stat().st_size, before.st_size)
        self.assertEqual(data.load_raw_panel(self.path).x.iloc[0], 99.0)


if __name__ == '__main__':
    unittest.main()
