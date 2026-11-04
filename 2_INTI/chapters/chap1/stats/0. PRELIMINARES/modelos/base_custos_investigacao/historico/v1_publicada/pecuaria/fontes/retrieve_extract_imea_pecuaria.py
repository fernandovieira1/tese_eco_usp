#!/usr/bin/env python3
"""Read public IMEA livestock XLSX; preserve cached values/units without conversion.
Python standard library only. --fetch creates a fresh live-endpoint snapshot.
Example: python retrieve_extract_imea_pecuaria.py --out /path/to/snapshot [--fetch]
"""
import argparse
from collections import Counter, defaultdict
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

RAW = 'imea_cup_bovinoculturadecorte_1.xlsx'
URLS = {
    'imea_cup_bovinoculturadecorte_1_wrapper.html': 'https://imea.com.br/imea-site/arquivo-externo?categoria=relatorio-de-mercado&arquivo=cup-bovinoculturadecorte&numeropublicacao=1',
    'imea_arquivo_externo.js': 'https://imea.com.br/imea-site/view/js/ArquivoExterno/ArquivoExterno.js?v=4',
    RAW: 'https://publicacoes.imea.com.br/relatorio-de-mercado/cup-bovinoculturadecorte/1',
}
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        csv.writer(f).writerows(rows)


def fetch(out):
    records = []
    for name, url in URLS.items():
        rec = {'file': name, 'source_url': url, 'retrieved_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
        with urllib.request.urlopen(url, timeout=60) as response:
            payload = response.read()
            rec.update(status=response.status, content_type=response.headers.get('Content-Type'), resolved_origin_path=response.url.split('?')[0], bytes=len(payload))
        (out / name).write_bytes(payload)
        rec['sha256'] = sha(out / name)
        records.append(rec)
    (out / 'fetch_manifest.json').write_text(json.dumps(records, indent=2), encoding='utf-8')


def sheets(path):
    with zipfile.ZipFile(path) as z:
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            shared = [''.join(t.text or '' for t in si.findall('.//s:t', NS)) for si in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        rels = {r.attrib['Id']: r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        book = ET.fromstring(z.read('xl/workbook.xml'))
        for sheet in book.find('s:sheets', NS):
            target = rels[sheet.attrib[f'{{{REL}}}id']]
            target = target.lstrip('/') if target.startswith('/') else 'xl/' + target
            doc = ET.fromstring(z.read(target))
            values = {}
            for cell in doc.findall('.//s:sheetData/s:row/s:c', NS):
                typ = cell.attrib.get('t', 'n')
                v = cell.find('s:v', NS)
                formula = cell.find('s:f', NS)
                if typ == 'inlineStr':
                    value = ''.join(t.text or '' for t in cell.findall('.//s:t', NS))
                elif v is None or v.text is None:
                    value = ''
                    typ = 'formula_no_cached_value' if formula is not None else 'stored_blank'
                else:
                    value = v.text
                    if typ == 's':
                        value = shared[int(value)]
                values[cell.attrib['r']] = (value, typ)
            yield sheet.attrib['name'], values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--fetch', action='store_true')
    args = parser.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    if args.fetch:
        fetch(out)
    raw_sha = sha(out / RAW)
    header = ['sheet_id', 'column', 'year_label', 'quarter_label', 'reference_period_from_labels', 'natureza_from_labels', 'coe', 'coe_cell', 'coe_type', 'cot', 'cot_cell', 'cot_type', 'ct', 'ct_cell', 'ct_type', 'modal_productivity', 'modal_productivity_cell', 'modal_productivity_type']
    costs = {k: [header] for k in ('cria', 'recria_engorda', 'ciclo_completo')}
    sheet_rows = [['sheet_id', 'sheet_name_exact', 'system_label_A3', 'geography_label_A4', 'system_key', 'cost_unit_label_A92', 'productivity_label_A91', 'geography_warning', 'rows_exported', 'all_three_costs_numeric_rows', 'source_file']]
    annotations = [['sheet_id', 'cell', 'source_value', 'xlsx_cell_type']]
    audit = []
    for idx, (name, cells) in enumerate(sheets(out / RAW), 1):
        sid = f's{idx:02d}'
        get = lambda addr: cells.get(addr, ('', 'absent_cell'))
        system_label, geography = get('A3')[0], get('A4')[0]
        if 'Ciclo Completo' in system_label:
            system = 'ciclo_completo'
        elif 'Recria e Engorda' in system_label:
            system = 'recria_engorda'
        elif 'Cria' in system_label:
            system = 'cria'
        else:
            raise ValueError((name, system_label))
        assert get('A92')[0] == 'Unidade da tabela: R$/@ vendida.', (name, get('A92'))
        metric_rows = {}
        for addr, (value, typ) in cells.items():
            if not re.fullmatch(r'A\d+', addr):
                continue
            for prefix, key in [('COE (', 'coe'), ('COT (', 'cot'), ('CT (', 'ct'), ('Produtividade Modal', 'modal_productivity')]:
                if value.startswith(prefix):
                    metric_rows[key] = int(addr[1:])
        assert set(metric_rows) == {'coe', 'cot', 'ct', 'modal_productivity'}
        for addr, (value, typ) in cells.items():
            r = int(re.search(r'\d+', addr)[0])
            if value != '' and (r <= 7 or r >= 92 or addr in ('A71', 'A80', 'A89', 'A91')):
                annotations.append([sid, addr, value, typ])
        warning = ''
        if name.strip().startswith('Cria_') and geography in ('MATO GROSSO', 'CUSTO DE PRODUÇÃO'):
            warning = 'sheet_name_and_A4_conflict_unresolved'
        n = numeric_n = 0
        for column in 'BCDEFGHIJKLMNOPQRSTU':
            year, quarter = get(f'{column}6')[0], get(f'{column}7')[0]
            if not re.fullmatch(r'\d{4}', year):
                continue
            m = re.fullmatch(r'([1-4])ºtri\.', quarter)
            if m:
                ref, nature = f'{year}-Q{m[1]}', 'trimestral_sem_classificacao_adicional'
            elif quarter in ('Consolidado', 'Consolidaddo'):
                ref, nature = year, 'consolidado_conforme_rotulo'
            else:
                ref, nature = '', 'periodo_incompleto_na_fonte'
            row = [sid, column, year, quarter, ref, nature]
            is_numeric = True
            for key in ('coe', 'cot', 'ct', 'modal_productivity'):
                addr = f'{column}{metric_rows[key]}'
                value, typ = get(addr)
                row.extend([value, addr, typ])
                if key in ('coe', 'cot', 'ct') and (typ != 'n' or value == ''):
                    is_numeric = False
            costs[system].append(row)
            n += 1
            numeric_n += is_numeric
        sheet_rows.append([sid, name, system_label, geography, system, get('A92')[0], get('A91')[0], warning, n, numeric_n, RAW])
        audit.append({'sheet_id': sid, 'sheet_name': name, 'rows': n, 'all_three_costs_numeric_rows': numeric_n, 'metric_rows': metric_rows, 'geography_warning': warning})
    for system, rows in costs.items():
        write_csv(out / f'imea_pecuaria_costs_{system}.csv', rows)
    write_csv(out / 'imea_pecuaria_sheets.csv', sheet_rows)
    write_csv(out / 'imea_pecuaria_headers_notes.csv', annotations)
    report = {'source_file': RAW, 'source_sha256': raw_sha, 'sheets': audit, 'row_counts': {k: len(v)-1 for k,v in costs.items()}, 'total_records': sum(len(v)-1 for v in costs.values()), 'numeric_cost_records': sum(a['all_three_costs_numeric_rows'] for a in audit), 'headers_notes': len(annotations)-1, 'cost_unit': 'R$/@ vendida', 'productivity_unit': '@vendida/ha', 'transformations': 'No cost conversion, imputation, formula recalculation, geographic resolution, reaggregation or modeling. Exact numeric cached strings retained. Period keys derive solely from explicit source labels; source typos retained.'}
    (out / 'extraction_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k != 'sheets'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
