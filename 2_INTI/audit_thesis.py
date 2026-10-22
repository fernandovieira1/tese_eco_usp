"""Auditoria técnica offline dos artigos ativos; fontes nunca são escritas.

Parser estático: segue input/include e bibliografias literais; não expande macros
TeX. BibTeX aceita valores delimitados, concatenação e @string. A compilação
complementa a análise estática. Relatórios e logs ficam em 2_INTI/audit/.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unicodedata

ROOT = Path(__file__).resolve().parent
EXPECTED = ('main.tex', '_abstract.tex', '0_introduction.tex',
            '1_literature_review.tex', '2_mt_descriptive.tex',
            '3_econometrics_strategy.tex', '4_discussion.tex',
            '5_Final_Remarks.tex', 'library.bib', 'citation-options.bib')


def uncomment(text):
    return re.sub(r'(?<!\\)(?:\\\\)*%[^\n]*', '', text)


def group(text, pos, opening='{', closing='}'):
    """Return balanced content and first position after delimiter."""
    depth, start = 1, pos + 1
    pos += 1
    while pos < len(text):
        if text[pos] == '\\':
            pos += 2
            continue
        if text[pos] == opening:
            depth += 1
        elif text[pos] == closing:
            depth -= 1
            if not depth:
                return text[start:pos], pos + 1
        pos += 1
    raise ValueError('Delimitador não fechado')


def parse_bib(text):
    """Return entries (including duplicate keys), preserving source offsets."""
    text = uncomment(text)
    entries, strings = [], {}
    pos = 0
    while match := re.search(r'@([\w-]+)\s*([{(])', text[pos:]):
        start = pos + match.start()
        delimiter = pos + match.end() - 1
        kind = match[1].lower()
        body, pos = group(text, delimiter, match[2], '}' if match[2] == '{' else ')')
        if kind in ('comment', 'preamble'):
            continue
        if kind == 'string':
            key, body = '', body
        else:
            key, sep, body = body.partition(',')
            if not sep or not key.strip():
                raise ValueError(f'Entrada inválida na linha {text.count(chr(10), 0, start) + 1}')
        fields, cursor = {}, 0
        while cursor < len(body):
            field = re.match(r'\s*,?\s*([\w-]+)\s*=\s*', body[cursor:])
            if not field:
                if body[cursor:].strip(' ,\r\n\t'):
                    raise ValueError(f'Campo inválido em {key.strip() or "@string"}')
                break
            name = field[1].lower()
            cursor += field.end()
            values = []
            while True:
                if cursor >= len(body):
                    raise ValueError(f'Valor ausente em {key}: {name}')
                if body[cursor] == '{':
                    value, cursor = group(body, cursor)
                elif body[cursor] == '"':
                    # Quotes inside brace-protected text do not close the value.
                    begin = cursor = cursor + 1
                    depth = 0
                    while cursor < len(body):
                        char = body[cursor]
                        if char == '\\':
                            cursor += 2
                            continue
                        if char == '"' and depth == 0:
                            break
                        depth += (char == '{') - (char == '}')
                        cursor += 1
                    if cursor == len(body):
                        raise ValueError(f'Aspas não fechadas em {key}')
                    value, cursor = body[begin:cursor], cursor + 1
                else:
                    token = re.match(r'[^\s,#]+', body[cursor:])
                    if not token:
                        raise ValueError(f'Valor inválido em {key}: {name}')
                    value = strings.get(token[0].lower(), token[0])
                    cursor += token.end()
                values.append(value)
                while cursor < len(body) and body[cursor].isspace():
                    cursor += 1
                if cursor < len(body) and body[cursor] == '#':
                    cursor += 1
                    while cursor < len(body) and body[cursor].isspace():
                        cursor += 1
                    continue
                break
            fields[name] = ''.join(values)
        if kind == 'string':
            strings.update(fields)
        else:
            entries.append(dict(key=key.strip(), kind=kind, fields=fields,
                                line=text.count('\n', 0, start) + 1))
    return entries


def commands(text):
    """Yield literal citation/file commands, skipping comments and verbatim."""
    text = uncomment(text)
    text = re.sub(r'\\begin\{(verbatim\*?|lstlisting|minted)\}.*?\\end\{\1\}', '', text, flags=re.S)
    text = re.sub(r'\\verb\*?([^\w\s])(.*?)\1', '', text)
    for match in re.finditer(r'\\([A-Za-z]+)\*?', text):
        name = match[1]
        if not ('cite' in name.lower() or name in ('input', 'include', 'bibliography', 'addbibresource')):
            continue
        pos = match.end()
        while pos < len(text):
            if text[pos].isspace():
                pos += 1
            elif text[pos] == '[':
                _, pos = group(text, pos, '[', ']')
            else:
                break
        if pos < len(text) and text[pos] == '{':
            value, _ = group(text, pos)
            yield name, value, text.count('\n', 0, match.start()) + 1


def normalize_doi(value):
    value = value.strip().replace('\\_', '_')
    return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value, flags=re.I).lower()


def metadata(value):
    value = unicodedata.normalize('NFKD', value.lower())
    return ''.join(c for c in value if c.isalnum())


def missing_doi_level(entry):
    """Heurística offline por tipo; não presume DOI a partir da citekey."""
    kind, fields = entry['kind'], entry['fields']
    if kind in ('dataset', 'data', 'software'):
        return 'INFO'
    if kind in ('article', 'inproceedings', 'conference', 'proceedings', 'incollection') or fields.get('journal') or fields.get('booktitle'):
        return 'WARNING'
    # Livros, legislação, páginas institucionais, relatórios e teses podem
    # legitimamente não ter DOI. Tipos desconhecidos mantêm revisão conservadora.
    optional = ('misc', 'online', 'electronic', 'www', 'book', 'booklet', 'inbook',
                'manual', 'techreport', 'report', 'mastersthesis', 'phdthesis',
                'thesis', 'unpublished', 'patent', 'standard', 'legislation')
    return 'INFO' if kind in optional else 'WARNING'


def article_dir(chapter):
    directory = ROOT / 'chapters' / chapter
    if not (directory / 'main.tex').is_file() and (directory / 'text').is_dir():
        return directory / 'text'
    return directory


def audit_article(chapter, findings):
    chapter_root = (ROOT / 'chapters' / chapter).resolve()
    directory = article_dir(chapter)
    def add(level, code, message, file='', line=None):
        findings.append(dict(article=chapter, level=level, code=code,
                             message=message, file=str(file), line=line))
    for name in EXPECTED:
        if not (directory / name).is_file():
            add('ERROR', 'missing_file', f'Arquivo esperado ausente: {name}')
    used, bibliographies, visited = set(), set(), set()
    locations = defaultdict(list)
    def visit(path):
        path = path.resolve()
        if path in visited:
            return
        visited.add(path)
        if not path.is_relative_to(chapter_root):
            add('ERROR', 'outside_scope', 'Dependência fora do artigo ativo', path)
            return
        if not path.is_file():
            add('ERROR', 'missing_dependency', 'Dependência TeX ausente', path)
            return
        try:
            for name, value, line in commands(path.read_text(encoding='utf-8-sig')):
                if name in ('input', 'include'):
                    target = directory / value
                    visit(target if target.suffix else target.with_suffix('.tex'))
                elif name in ('bibliography', 'addbibresource'):
                    for filename in value.split(','):
                        target = directory / filename.strip()
                        bibliographies.add(target if target.suffix else target.with_suffix('.bib'))
                else:
                    for key in value.split(','):
                        used.add(key.strip())
                        locations[key.strip()].append(f'{path.name}:{line}')
        except (OSError, UnicodeError, ValueError) as exc:
            add('ERROR', 'tex_parse', str(exc), path)
    visit(directory / 'main.tex')
    entries = []
    if not bibliographies:
        add('ERROR', 'no_bibliography', 'Nenhuma bibliografia literal encontrada')
    for path in sorted(bibliographies):
        if not path.resolve().is_relative_to(chapter_root):
            add('ERROR', 'outside_scope', 'Bibliografia fora do artigo', path)
            continue
        try:
            parsed = parse_bib(path.read_text(encoding='utf-8-sig'))
        except (OSError, UnicodeError, ValueError) as exc:
            add('ERROR', 'bib_parse', str(exc), path)
            continue
        for key, count in Counter(e['key'] for e in parsed).items():
            if count > 1:
                add('ERROR', 'duplicate_key', f'{key}: {count} entradas na bibliografia', path)
        for entry in parsed:
            entry.update(article=chapter, file=str(path))
        entries.extend(parsed)
    for key, count in Counter(e['key'] for e in entries).items():
        if count > 1 and len({e['file'] for e in entries if e['key'] == key}) > 1:
            add('ERROR', 'duplicate_key_across_bibs', f'{key}: presente em várias bibliografias')
    for key in sorted(used - {e['key'] for e in entries} - {'*'}):
        add('ERROR', 'undefined_citekey', f'{key}: {", ".join(locations[key])}')
    for entry in entries:
        key, fields = entry['key'], entry['fields']
        if entry['kind'] == 'abnt-options':
            continue
        if key not in used and '*' not in used:
            add('INFO', 'unused_reference', f'Referência não utilizada: {key}', entry['file'], entry['line'])
        doi = normalize_doi(fields.get('doi', ''))
        entry['doi'] = doi
        if not doi:
            add(missing_doi_level(entry), 'missing_doi', f'{key}: DOI ausente (pode ser legítimo)', entry['file'], entry['line'])
        elif not re.fullmatch(r'10\.\d{4,9}/[^\s{}]+', doi):
            add('WARNING', 'malformed_doi', f'{key}: DOI malformado: {doi}', entry['file'], entry['line'])
    add('INFO', 'inventory', f'{len(visited)} fontes TeX; {len(entries)} entradas; {len(used - {"*"})} chaves usadas')
    return entries


def audit_dois(entries, findings):
    by_doi = defaultdict(list)
    for entry in entries:
        if entry.get('doi'):
            by_doi[entry['doi']].append(entry)
    for doi, matches in sorted(by_doi.items()):
        if len(matches) < 2:
            continue
        labels = ', '.join(f'{e["article"]}/{e["key"]}' for e in matches)
        conflicts = []
        for field in ('title', 'author', 'year', 'journal', 'booktitle', 'volume', 'number', 'pages'):
            values = {metadata(e['fields'][field]) for e in matches if e['fields'].get(field)}
            if len(values) > 1:
                conflicts.append(field)
        shared = (not conflicts and len(matches) == 2
                  and {e['article'] for e in matches} == {'chap1', 'chap2'}
                  and len({e['key'] for e in matches}) == 1)
        findings.append(dict(article='global', level='ERROR' if conflicts else 'INFO' if shared else 'WARNING',
                             code='doi_conflict' if conflicts else 'shared_doi' if shared else 'duplicate_doi',
                             message=f'{doi}: {labels}' + (f'; metadados conflitantes: {", ".join(conflicts)}' if conflicts else ''),
                             file='', line=None))


def scan_log(text, article, filename):
    findings = []
    # Final log only: intermediate passes naturally contain undefined references.
    patterns = [
        ('ERROR', r'^!|^.*(?:LaTeX|Package .*?) Error:|^.*(?:Repeated entry|I couldn.t open|I found no|Illegal,|[1-9]\d* error messages?)'),
        ('ERROR', r'.*(?:Citation|Reference).*undefined|.*(?:undefined references|undefined citations|didn.t find a database entry|multiply defined)'),
        ('INFO', r'Underfull\s+\\vbox\b'),
        ('WARNING', r'.*(?:Warning(?::|--|\s)|Overfull|Underfull|Rerun to get|Label\(s\) may have changed)'),
    ]
    for number, line in enumerate(text.splitlines(), 1):
        for level, pattern in patterns:
            if re.search(pattern, line, re.I):
                findings.append(dict(article=article, level=level, code='compilation_log',
                                     message=line.strip(), file=filename, line=number))
                break
    return findings


def compile_article(chapter, report_dir, executable, timeout, findings):
    chapter_root = ROOT / 'chapters' / chapter
    directory = article_dir(chapter)
    with tempfile.TemporaryDirectory(prefix='audit_thesis_') as temporary:
        target = Path(temporary) / chapter
        shutil.copytree(chapter_root, target,
                        ignore=shutil.ignore_patterns('stats', 'code', '.venv', 'venv', '__pycache__',
                                                      '.pytest_cache', '.ipynb_checkpoints',
                                                      '*.aux', '*.bbl', '*.blg', '*.log', 'main.pdf',
                                                      '*.fls', '*.fdb_latexmk', '*.synctex.gz', '*.out', '*.toc'))
        # A seção descritiva inclui estes produtos; dados e dashboards ficam fora.
        for relative in ('stats/descritiva/resultados_h1/tabelas',
                         'stats/descritiva/resultados_h1/figuras',
                         'stats/tabelas', 'stats/figuras'):
            if (chapter_root / relative).is_dir():
                shutil.copytree(chapter_root / relative, target / relative)
        workdir = target / directory.relative_to(chapter_root)
        command = [executable, '-norc', '-pdf', '-g', '-interaction=nonstopmode',
                   '-halt-on-error', '-file-line-error', '-no-shell-escape', 'main.tex']
        try:
            result = subprocess.run(command, cwd=workdir, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, timeout=timeout)
            output = result.stdout.decode('utf-8', errors='replace')
            code = result.returncode
        except (OSError, subprocess.TimeoutExpired) as exc:
            output, code = str(exc), -1
        (report_dir / f'{chapter}_latexmk.txt').write_text(output, encoding='utf-8')
        for extension in ('log', 'blg'):
            source = workdir / f'main.{extension}'
            if source.exists():
                text = source.read_text(encoding='utf-8', errors='replace')
                destination = report_dir / f'{chapter}.{extension}'
                destination.write_text(text, encoding='utf-8')
                findings.extend(scan_log(text, chapter, str(destination)))
        pdf = workdir / 'main.pdf'
        findings.append(dict(article=chapter, level='ERROR' if code or not pdf.is_file() else 'INFO',
                             code='compilation', message=f'latexmk exit={code}; PDF={pdf.is_file()}',
                             file=str(report_dir / f'{chapter}_latexmk.txt'), line=None))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chapters', nargs='+', choices=('chap1', 'chap2'), default=['chap1', 'chap2'])
    parser.add_argument('--skip-compile', action='store_true', help='Auditoria estática; registra compilação não verificada')
    parser.add_argument('--latexmk', help='Executável latexmk; padrão: PATH ou TeX Live 2025 documentado')
    parser.add_argument('--timeout', type=int, default=180, help='Timeout de compilação por artigo em segundos')
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error('--timeout deve ser positivo')
    report_dir = ROOT / 'audit' / ('audit_thesis_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ'))
    report_dir.mkdir(parents=True)
    findings, entries = [], []
    for chapter in dict.fromkeys(args.chapters):
        entries.extend(audit_article(chapter, findings))
    audit_dois(entries, findings)
    executable = args.latexmk or os.environ.get('LATEXMK_PATH') or shutil.which('latexmk')
    for chapter in dict.fromkeys(args.chapters):
        if args.skip_compile:
            findings.append(dict(article=chapter, level='INFO', code='compile_skipped',
                                 message='Compilação não verificada (--skip-compile)', file='', line=None))
        elif not executable:
            findings.append(dict(article=chapter, level='ERROR', code='missing_latexmk',
                                 message='latexmk indisponível; compilação não verificada', file='', line=None))
        else:
            compile_article(chapter, report_dir, executable, args.timeout, findings)
    counts = {level: sum(f['level'] == level for f in findings) for level in ('ERROR', 'WARNING', 'INFO')}
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(), chapters=args.chapters,
                  offline=True, compilation=not args.skip_compile, counts=counts, findings=findings,
                  limitations=['Análise estática não expande macros TeX, condicionais ou nomes dinâmicos.',
                               'DOI validado por sintaxe, sem resolução online; diferenças de metadados requerem revisão.',
                               'Ausência de DOI não implica erro científico.'])
    (report_dir / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# Auditoria técnica da tese', '', f'UTC: {report["created_utc"]}', '',
             ' | '.join(f'{level}: {count}' for level, count in counts.items()), '',
             *report['limitations'], '', '## Achados', '']
    for f in findings:
        lines.append(f'- **{f["level"]}** [{f["article"]}/{f["code"]}] {f["message"]}'
                     + (f' — {f["file"]}:{f["line"] or ""}' if f['file'] else ''))
    (report_dir / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(' | '.join(f'{level}: {count}' for level, count in counts.items()))
    for chapter in dict.fromkeys(args.chapters):
        subset = [f for f in findings if f['article'] == chapter]
        print(f'{chapter}: ' + ', '.join(f'{level}={sum(f["level"] == level for f in subset)}' for level in counts))
    for f in [f for f in findings if f['level'] == 'ERROR'][:5]:
        print(f'ERROR [{f["article"]}]: {f["message"]}')
    print(f'Relatório: {report_dir / "report.md"}')
    return int(counts['ERROR'] > 0)


if __name__ == '__main__':
    raise SystemExit(main())
