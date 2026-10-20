"""Regressão da cópia isolada usada na compilação dos artigos."""
import importlib.util
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('audit_thesis', Path(__file__).resolve().parents[1] / 'audit_thesis.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class CompilationCopyTests(unittest.TestCase):
    def test_compilation_inputs_are_copied_without_data_or_stale_output(self):
        for with_assets in (True, False):
            with self.subTest(with_assets=with_assets), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                chapter = root / 'chapters/chap1'
                relative_workdir = Path('text') if with_assets else Path('.')
                results = Path('stats/descritiva/resultados_h1')
                files = {
                    relative_workdir / 'main.tex': b'compilation input',
                    relative_workdir / 'main.pdf': b'stale compiled PDF',
                    relative_workdir / 'figures/reference.pdf': b'reference figure',
                    Path('stats/descritiva/df_h1'): b'data must not be copied',
                    Path('stats/DASHBOARD/app.py'): b'dashboard must not be copied',
                }
                if with_assets:
                    files.update({results / 'tabelas/numeros.tex': b'latex macros',
                                  results / 'figuras/fig01_conversao.pdf': b'descriptive figure'})
                for relative, content in files.items():
                    path = chapter / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(content)
                report_dir = root / 'audit'
                report_dir.mkdir()

                def compile_copy(command, cwd, **kwargs):
                    copied_chapter = cwd.parent if with_assets else cwd
                    self.assertEqual((cwd / 'main.tex').read_bytes(), files[relative_workdir / 'main.tex'])
                    self.assertFalse((cwd / 'main.pdf').exists())
                    self.assertEqual((cwd / 'figures/reference.pdf').read_bytes(), b'reference figure')
                    self.assertFalse((copied_chapter / 'stats/descritiva/df_h1').exists())
                    self.assertFalse((copied_chapter / 'stats/DASHBOARD').exists())
                    if with_assets:
                        for relative in (results / 'tabelas/numeros.tex', results / 'figuras/fig01_conversao.pdf'):
                            self.assertEqual((copied_chapter / relative).read_bytes(), files[relative])
                    (cwd / 'main.pdf').write_bytes(b'new compiled PDF')
                    return SimpleNamespace(stdout=b'compiled', returncode=0)

                findings = []
                with patch.object(audit, 'ROOT', root), patch.object(audit.subprocess, 'run', side_effect=compile_copy):
                    audit.compile_article('chap1', report_dir, 'latexmk', 30, findings)
                self.assertEqual(findings[-1]['level'], 'INFO')
                self.assertEqual((report_dir / 'chap1_latexmk.txt').read_text(), 'compiled')
                for relative, content in files.items():
                    self.assertEqual((chapter / relative).read_bytes(), content)


if __name__ == '__main__':
    unittest.main()
