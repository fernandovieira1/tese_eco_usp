"""Extrator do HTML oficial SGS4189; bruto não incluído neste pacote.

Método recebido do ambiente coletor. Use HTML obtido pelo POST documentado
em sgs4189_provenance.json. Saída nova, sem sobrescrever os extratos congelados.
A reprodução do painel usa os CSVs incluídos e não requer executar este script.
"""
import argparse
import csv
import hashlib
import json
import math
import re
from decimal import Decimal
from pathlib import Path


def extrair(html,saida):
    raw=html.read_bytes();s=raw.decode('latin1');rows=[]
    months='jan feb mar apr may jun jul aug sep oct nov dec'.split()
    for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>',s,re.S|re.I):
        cells=[re.sub('<[^>]+>','',c).strip() for c in re.findall(r'<td\b[^>]*>(.*?)</td>',row,re.S|re.I)]
        if len(cells)==2 and re.fullmatch(r'[a-z]{3}/\d{4}',cells[0]):
            mon,year=cells[0].split('/');value=cells[1].replace(',','.')
            assert math.isfinite(float(value))
            rows.append((f'{year}-{months.index(mon)+1:02d}-01',value))
    assert [d for d,v in rows]==[f'{y}-{m:02d}-01' for y in range(2000,2025) for m in range(1,13)]
    saida.mkdir(parents=True,exist_ok=False)
    with (saida/'sgs4189_2000_2024.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['date','selic_4189_percent_pa']);w.writerows(rows)
    with (saida/'sgs4189_annual_lag_panel2001_2024.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['ano','ano_origem','n_meses','selic_media_ano_anterior_pct_aa'])
        for year in range(2000,2024):
            values=[Decimal(v) for d,v in rows if d.startswith(str(year))]
            assert len(values)==12
            w.writerow([year+1,year,12,str(sum(values)/12)])
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in saida.glob('*.csv')}
    hashes['html_fornecido']=hashlib.sha256(raw).hexdigest()
    (saida/'hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('html',type=Path);parser.add_argument('saida',type=Path)
    args=parser.parse_args();extrair(args.html,args.saida)
