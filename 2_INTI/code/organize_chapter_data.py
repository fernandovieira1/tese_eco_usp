"""Move the existing snapshot into chapter directories without losing evidence.

Dry run by default; --apply performs verified moves/copies. --verify checks the
saved relocation manifest and requires no source downloads or recalculation.
"""
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
import shutil
from data_paths import DATA, ROOT, chapters_for, data_paths, file_sha256

CATALOG = DATA / 'catalog'
MANIFEST = CATALOG / 'relocacao_chap1_chap2_20261002.csv'
SUMMARY = CATALOG / 'validacao_organizacao_chap1_chap2_20261002.json'
COLUMNS = ['arquivo_anterior', 'arquivo_atual', 'capitulo', 'operacao', 'bytes', 'sha256', 'verificado_utc']


def safe_path(path):
    target = Path(path).resolve()
    if target == DATA.resolve() or not target.is_relative_to(DATA.resolve()):
        raise ValueError(f'Unsafe target: {target}')
    return target


def plan():
    files = sorted(p for folder in ('raw', 'interim', 'processed')
                   for p in (DATA / folder).rglob('*') if p.is_file())
    totals = {'source_files': len(files), 'source_bytes': sum(p.stat().st_size for p in files),
              'additional_bytes': 0, 'chap1': {'files': 0, 'bytes': 0},
              'chap2': {'files': 0, 'bytes': 0}}
    for source in files:
        relative = source.relative_to(DATA)
        for i, chapter in enumerate(chapters_for(relative)):
            totals[chapter]['files'] += 1
            totals[chapter]['bytes'] += source.stat().st_size
            if i:
                totals['additional_bytes'] += source.stat().st_size
    return files, totals


def export_chapter_catalogs(rows):
    old_inventory = {}
    with (CATALOG / 'inventario_arquivos_dados_h1_h2.csv').open(encoding='utf-8-sig', newline='') as stream:
        old_inventory = {r['arquivo']: r for r in csv.DictReader(stream)}
    with (CATALOG / 'data_catalogo_variaveis_h1_h2.csv').open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames + ['arquivo_anterior', 'nota_organizacao']
        variables = list(reader)
    for chapter in ('chap1', 'chap2'):
        target = DATA / chapter / 'catalog'
        target.mkdir(parents=True, exist_ok=True)
        selected = [r for r in rows if r['capitulo'] == chapter]
        index = {r['arquivo_anterior']: r for r in selected}
        with (target / 'inventario_arquivos.csv').open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=COLUMNS + ['fonte', 'url', 'status_anterior'])
            writer.writeheader()
            for row in selected:
                old = old_inventory.get(row['arquivo_anterior'], {})
                writer.writerow(dict(row, fonte=old.get('fonte', ''), url=old.get('url', ''), status_anterior=old.get('status', '')))
        with (target / 'catalogo_variaveis.csv').open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for variable in variables:
                old = variable['arquivo_local']
                if old in index:
                    record = dict(variable, arquivo_local=index[old]['arquivo_atual'], arquivo_anterior=old,
                                  nota_organizacao='Copia ou relocacao verificada; disponibilidade e status cientifico preservados.')
                    writer.writerow(record)
                elif not old and ('H1' if chapter == 'chap1' else 'H2') in variable['hipotese']:
                    writer.writerow(dict(variable, arquivo_anterior='', nota_organizacao='Lacuna preservada; sem arquivo adquirido.'))
        for manifest in sorted(CATALOG.glob('acquisition*.jsonl')):
            records = []
            for line in manifest.read_text(encoding='utf-8').splitlines():
                record = json.loads(line)
                old = record.get('arquivo_local', '')
                relative = old.removeprefix('2_INTI/data/')
                if chapter in chapters_for(relative):
                    record['arquivo_anterior'] = old
                    record['arquivo_local'] = f'2_INTI/data/{chapter}/{relative}'
                    record['nota_organizacao'] = 'Visao derivada; manifesto original imutavel em data/catalog.'
                    records.append(record)
            if records:
                (target / manifest.name).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records), encoding='utf-8')


def verify():
    with MANIFEST.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    errors = []
    for row in rows:
        target = safe_path(ROOT / row['arquivo_atual'])
        if not target.is_file() or target.stat().st_size != int(row['bytes']) or file_sha256(target) != row['sha256']:
            errors.append(row['arquivo_atual'])
    result = {'verified_utc': datetime.now(timezone.utc).isoformat(), 'checked_files': len(rows),
              'original_files': len({r['arquivo_anterior'] for r in rows}),
              'shared_copies': sum(r['operacao'] == 'COPIA_COMPARTILHADA' for r in rows),
              'bytes_after': sum(int(r['bytes']) for r in rows), 'errors': errors}
    SUMMARY.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    if errors:
        raise SystemExit(1)
    return rows


def complete_shared():
    """Append newly assigned chapter copies without repeating any move."""
    with MANIFEST.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    index = {}
    for row in rows:
        index.setdefault(row['arquivo_anterior'], []).append(row)
    pending = []
    for old, records in index.items():
        source_record = next(r for r in records if r['operacao'] == 'RELOCACAO')
        source = safe_path(ROOT / source_record['arquivo_atual'])
        assigned = {r['capitulo'] for r in records}
        for chapter in chapters_for(old):
            if chapter in assigned:
                continue
            relative = old.removeprefix('2_INTI/data/')
            target = safe_path(DATA / chapter / relative)
            if target.exists():
                raise FileExistsError(target)
            pending.append((source, target, chapter, source_record))
    extra = sum(int(r['bytes']) for _, _, _, r in pending)
    free = shutil.disk_usage(DATA).free
    print(json.dumps({'additional_copies': len(pending), 'additional_bytes': extra,
                      'free_bytes_before': free}, indent=2), flush=True)
    if free < extra + 128 * 1024**2:
        raise ValueError('Insufficient space for supplementary shared copies')
    with MANIFEST.open('a', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        for i, (source, target, chapter, record) in enumerate(pending, 1):
            digest = file_sha256(source)
            if digest != record['sha256']:
                raise ValueError(f'Source changed since relocation: {source}')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            if target.stat().st_size != int(record['bytes']) or file_sha256(target) != digest:
                raise ValueError(f'Copy verification failed: {target}')
            row = dict(record, arquivo_atual=target.relative_to(ROOT).as_posix(), capitulo=chapter,
                       operacao='COPIA_COMPARTILHADA', verificado_utc=datetime.now(timezone.utc).isoformat())
            writer.writerow(row)
            stream.flush()
            rows.append(row)
            if i % 100 == 0:
                print(f'Verified supplementary copies {i}/{len(pending)}', flush=True)
    export_chapter_catalogs(rows)
    verify()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--complete-shared', action='store_true')
    args = parser.parse_args()
    if args.verify:
        verify()
        return
    if args.complete_shared:
        complete_shared()
        return
    files, totals = plan()
    print(json.dumps(totals, indent=2), flush=True)
    if not args.apply:
        return
    if MANIFEST.exists():
        raise ValueError('Relocation already recorded; use --verify, do not repeat moves.')
    if not files:
        raise ValueError('No source snapshot found')
    if shutil.disk_usage(DATA).free < totals['additional_bytes'] + 128 * 1024**2:
        raise ValueError('Insufficient space for verified shared copies')
    # Validate every source and destination before the first move.
    for source in files:
        safe_path(source)
        for target in data_paths(source.relative_to(DATA)):
            safe_path(target)
            if target.exists():
                raise FileExistsError(target)
    rows = []
    with MANIFEST.open('x', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        for i, source in enumerate(files, 1):
            relative = source.relative_to(DATA)
            destinations = data_paths(relative)
            digest = file_sha256(source)
            size = source.stat().st_size
            for j, target in enumerate(destinations):
                safe_path(target).parent.mkdir(parents=True, exist_ok=True)
                if j == 0:
                    safe_path(source).rename(safe_path(target))
                else:
                    shutil.copy2(destinations[0], target)
                if target.stat().st_size != size or file_sha256(target) != digest:
                    raise ValueError(f'Hash differs after move/copy: {target}')
                row = dict(arquivo_anterior='2_INTI/data/' + relative.as_posix(),
                           arquivo_atual=target.relative_to(ROOT).as_posix(),
                           capitulo=chapters_for(relative)[j],
                           operacao='RELOCACAO' if j == 0 else 'COPIA_COMPARTILHADA',
                           bytes=size, sha256=digest, verificado_utc=datetime.now(timezone.utc).isoformat())
                writer.writerow(row)
                stream.flush()
                rows.append(row)
            if i % 100 == 0:
                print(f'Verified {i}/{len(files)} original files', flush=True)
    export_chapter_catalogs(rows)
    verify()


if __name__ == '__main__':
    main()
