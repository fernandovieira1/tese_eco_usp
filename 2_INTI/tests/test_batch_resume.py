"""Retomada OLS/FE exige proveniencia do codigo antes de ler checkpoints."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

APP = Path(__file__).resolve().parents[1] / 'chapters/chap1/stats/DASHBOARD/pt_h1'
BATCHES = {
    'ols': ('execucao_ols_200', 'reproduzir.py', 'plano_pre_estimacao.json', 'M001.json', 'dump'),
    'fe': ('execucao_fe_candidatas', 'estimar_fe.py', 'plano_fe.json', 'M001_fe.json', 'save'),
}


class StopRun(BaseException):
    """Interrompe o teste antes de estimar ou gravar produtos do lote."""


class BatchResumeTests(unittest.TestCase):
    def fixture(self, kind):
        folder, filename, plan_name, record_name, writer = BATCHES[kind]
        spec = importlib.util.spec_from_file_location('batch_' + kind, APP / folder / filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        app = root / 'pt_h1'
        here = app / folder
        here.mkdir(parents=True)
        (app / 'h1lab').mkdir()
        script = here / filename
        script.write_bytes((APP / folder / filename).read_bytes())
        for name in ['app.py', 'h1lab/models.py', 'h1lab/data.py', 'h1lab/panel_metrics.py', 'h1lab/ui.py']:
            (app / name).write_text('# fixture\n', encoding='utf-8')
        for key, value in {'ROOT': root, 'APP': app, 'HERE': here, '__file__': str(script)}.items():
            self.enterContext(patch.object(module, key, value))
        self.enterContext(patch.object(module, 'load_data', return_value=(pd.DataFrame(), None, {'csv_sha256': 'csv'})))
        self.enterContext(patch.object(module.subprocess, 'check_output', return_value='main'))
        model_plan = {'id': 'M001', 'local': 22, 'spec': {'y': 'y', 'xs': ['x']}, 'description': 'x'}
        if kind == 'ols':
            self.enterContext(patch.object(module, 'plan', return_value=[model_plan]))
        else:
            workbook = app / 'RESULTADOS_DASH_H1.xlsx'
            workbook.write_bytes(b'fixture workbook')
            source = {'created': 'fixture', 'sha256': module.sha256(workbook), 'candidates': [{
                'ID do modelo': 'M001', 'Variável dependente': module.pretty('y'),
                'Variáveis Independentes': 'x', 'R2': 0.4, 'ID amostra SHA256': 'sample'}]}
            (here / 'candidatas_origem.json').write_text(json.dumps(source), encoding='utf-8')
            originals = app / 'execucao_ols_200'
            originals.mkdir()
            (originals / 'resultados_completos.json').write_text(json.dumps([
                {'plan': model_plan, 'summary': {'R2': 0.4}}]), encoding='utf-8')
        return module, here / plan_name, here / record_name, writer

    def hashes(self, module):
        paths = [Path(module.__file__), module.APP / 'app.py', *sorted((module.APP / 'h1lab').glob('*.py'))]
        return {str(p.relative_to(module.ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

    def checkpoint(self, kind):
        module, plan_path, record_path, writer = self.fixture(kind)
        with patch.object(module, 'fit_model', side_effect=StopRun):
            with self.assertRaises(StopRun):
                module.run()
        plan = json.loads(plan_path.read_text(encoding='utf-8'))
        plan['code_hashes'] = self.hashes(module)
        plan_path.write_text(json.dumps(plan), encoding='utf-8')
        record = {'plan': plan['models'][0], 'status': 'ok', 'data_sha256': 'csv'}
        record_path.write_text(json.dumps(record), encoding='utf-8')
        return module, plan_path, record_path, writer

    def assert_blocked_without_writes(self, module, writer):
        before = {p.name: p.read_bytes() for p in module.HERE.iterdir() if p.is_file()}
        with patch.object(module, writer, side_effect=StopRun) as write, patch.object(module, 'fit_model', side_effect=StopRun) as fit:
            with self.assertRaisesRegex(RuntimeError, 'diretório de execução novo'):
                module.run()
        write.assert_not_called()
        fit.assert_not_called()
        self.assertEqual(before, {p.name: p.read_bytes() for p in module.HERE.iterdir() if p.is_file()})

    def test_new_plan_records_code_before_first_estimation(self):
        for kind in BATCHES:
            with self.subTest(batch=kind):
                module, plan_path, _, _ = self.fixture(kind)
                with patch.object(module, 'fit_model', side_effect=StopRun):
                    with self.assertRaises(StopRun):
                        module.run()
                self.assertEqual(json.loads(plan_path.read_text(encoding='utf-8'))['code_hashes'], self.hashes(module))

    def test_compatible_resume_reuses_checkpoint(self):
        for kind in BATCHES:
            with self.subTest(batch=kind):
                module, _, _, writer = self.checkpoint(kind)
                with patch.object(module, writer, side_effect=StopRun), patch.object(module, 'fit_model', side_effect=StopRun) as fit:
                    with self.assertRaises(StopRun):
                        module.run()
                fit.assert_not_called()

    def test_changed_code_blocks_resume_without_writing(self):
        for kind in BATCHES:
            module, _, _, writer = self.checkpoint(kind)
            for path in [Path(module.__file__), *(module.APP / 'h1lab').glob('*.py')]:
                with self.subTest(batch=kind, code=path.name):
                    original = path.read_bytes()
                    path.write_bytes(original + b'\n# changed\n')
                    self.assert_blocked_without_writes(module, writer)
                    path.write_bytes(original)

    def test_legacy_plan_without_hashes_is_not_upgraded(self):
        for kind in BATCHES:
            with self.subTest(batch=kind):
                module, plan_path, _, writer = self.checkpoint(kind)
                plan = json.loads(plan_path.read_text(encoding='utf-8'))
                del plan['code_hashes']
                plan_path.write_text(json.dumps(plan), encoding='utf-8')
                self.assert_blocked_without_writes(module, writer)

    def test_orphan_checkpoint_cannot_create_new_plan(self):
        for kind in BATCHES:
            with self.subTest(batch=kind):
                module, plan_path, _, writer = self.checkpoint(kind)
                plan_path.unlink()
                self.assert_blocked_without_writes(module, writer)


if __name__ == '__main__':
    unittest.main()
