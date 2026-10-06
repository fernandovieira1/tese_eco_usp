"""Testes isolados do auditor; sem dependências ou fontes científicas reais."""
import tempfile
import unittest
import contextlib
import io
from pathlib import Path
from unittest.mock import patch

import audit_thesis as audit


class AuditTests(unittest.TestCase):
    def test_bib_nested_quotes_strings_duplicates(self):
        entries = audit.parse_bib('''% @article{ignored, title={No}}
@string{prefix = "10.1234/"}
@article{key, title={A {nested} title}, doi=prefix # "abc"}
@article(key, title="A {\"protected\"} title", year=2020)
@comment{ignored @article{fake}}
''')
        self.assertEqual([e['key'] for e in entries], ['key', 'key'])
        self.assertEqual(entries[0]['fields']['doi'], '10.1234/abc')
        self.assertEqual(entries[1]['fields']['year'], '2020')

    def test_commands_comments_options_verbatim(self):
        text = r'''% \cite{fake}
\citeonline*[p. 1]{a,b} \textcite[see][2]{c} \nocite{*}
\begin{verbatim}\cite{fake}\end{verbatim}
\verb|\cite{fake}| \input{section}
'''
        self.assertEqual([v for _, v, _ in audit.commands(text)], ['a,b', 'c', '*', 'section'])

    def test_static_missing_duplicate_unused_doi(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            chapter = root / 'chapters' / 'chap1'
            chapter.mkdir(parents=True)
            for filename in audit.EXPECTED:
                (chapter / filename).write_text('', encoding='utf-8')
            (chapter / 'main.tex').write_text(r'\input{section}\bibliography{library}', encoding='utf-8')
            (chapter / 'section.tex').write_text(r'\cite{missing,a}', encoding='utf-8')
            (chapter / 'library.bib').write_text('''@article{a,title={A},doi={10.1234/a}}
@article{a,title={B},doi={10.1234/a}}
@book{unused,title={Unused}}
@article{bad,title={Bad},doi={not-a-doi}}''', encoding='utf-8')
            findings = []
            with patch.object(audit, 'ROOT', root):
                entries = audit.audit_article('chap1', findings)
            audit.audit_dois(entries, findings)
            codes = {f['code'] for f in findings}
            self.assertTrue({'undefined_citekey', 'duplicate_key', 'unused_reference',
                             'missing_doi', 'malformed_doi', 'doi_conflict'} <= codes)
            self.assertEqual(next(f['level'] for f in findings if f['code'] == 'doi_conflict'), 'ERROR')
            self.assertEqual(next(f['level'] for f in findings if f['code'] == 'malformed_doi'), 'WARNING')
            self.assertEqual(next(f['level'] for f in findings if f['code'] == 'missing_doi'), 'INFO')

    def test_shared_doi_and_log_severity(self):
        entries = [dict(article=c, key='a', doi='10.1234/a', fields={'title': '{Same} title'})
                   for c in ('chap1', 'chap2')]
        findings = []
        audit.audit_dois(entries, findings)
        self.assertEqual((findings[0]['level'], findings[0]['code']), ('INFO', 'shared_doi'))
        entries[1]['article'] = 'chap1'
        findings = []
        audit.audit_dois(entries, findings)
        self.assertEqual((findings[0]['level'], findings[0]['code']), ('WARNING', 'duplicate_doi'))
        entries[1]['article'] = 'chap2'
        entries[1]['key'] = 'other'
        findings = []
        audit.audit_dois(entries, findings)
        self.assertEqual((findings[0]['level'], findings[0]['code']), ('WARNING', 'duplicate_doi'))
        entries[1]['key'] = 'a'
        entries[1]['fields']['title'] = 'Different title'
        findings = []
        audit.audit_dois(entries, findings)
        self.assertEqual((findings[0]['level'], findings[0]['code']), ('ERROR', 'doi_conflict'))
        findings = audit.scan_log("LaTeX Warning: Citation `x' undefined.\nOverfull \\hbox\n"
                                  "Warning--empty year in key\n! Fatal error", 'chap1', 'log')
        self.assertEqual([f['level'] for f in findings], ['ERROR', 'WARNING', 'WARNING', 'ERROR'])
        findings = audit.scan_log('Underfull \\vbox (badness 10000)\nUnderfull \\hbox\n'
                                  'Package babel Warning: deprecated', 'chap1', 'log')
        self.assertEqual([f['level'] for f in findings], ['INFO', 'WARNING', 'WARNING'])
        self.assertEqual(audit.normalize_doi('https://doi.org/10.1234/ABC'), '10.1234/abc')
        self.assertEqual(audit.scan_log('Package: infwarerr Providing info/warning/error messages\n'
                                       'warning$ -- 0\n(There were 0 error messages)', 'chap1', 'log'), [])

    def test_missing_doi_levels(self):
        for kind in ('misc', 'online', 'techreport', 'book', 'phdthesis', 'dataset', 'software'):
            with self.subTest(kind=kind):
                self.assertEqual(audit.missing_doi_level(dict(kind=kind, fields={})), 'INFO')
        for kind in ('article', 'inproceedings', 'conference', 'incollection', 'unknown'):
            with self.subTest(kind=kind):
                self.assertEqual(audit.missing_doi_level(dict(kind=kind, fields={})), 'WARNING')
        self.assertEqual(audit.missing_doi_level(dict(kind='misc', fields={'journal': 'Journal'})), 'WARNING')

    def test_unclosed_bib_rejected(self):
        with self.assertRaises(ValueError):
            audit.parse_bib('@article{a,title={unclosed}')

    def test_exit_status_and_reports(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            chapter = root / 'chapters' / 'chap1'
            chapter.mkdir(parents=True)
            for filename in audit.EXPECTED:
                (chapter / filename).write_text('', encoding='utf-8')
            (chapter / 'main.tex').write_text(r'\bibliography{library}\cite{a}', encoding='utf-8')
            (chapter / 'library.bib').write_text('@book{a,title={Title}}', encoding='utf-8')
            with patch.object(audit, 'ROOT', root), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(audit.main(['--chapters', 'chap1', '--skip-compile']), 0)
                (chapter / '_abstract.tex').unlink()
                self.assertEqual(audit.main(['--chapters', 'chap1', '--skip-compile']), 1)
            self.assertEqual(len(list((root / 'xreports').glob('*/report.json'))), 2)
            self.assertFalse((root / 'reports').exists())


if __name__ == '__main__':
    unittest.main()
