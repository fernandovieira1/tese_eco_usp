"""Auditar primeiro; depois juntar por ano. Sem rede na reprodução."""
import argparse
import csv
import hashlib
import json
import math
import statistics as st
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

P=Path(__file__).resolve().parent
F=P/'fontes_v2'
V1=P/'painel_h1_base3_v1.csv'
HASH_V1='3192b5ff1f8c8040eea1b2e47c4410d62dd62928a4932aa1823324da7d2abc79'
NOVAS=['preco_real_usd2024_media_anual_lag1__dap','razao_medias_reais_lag1__soja_dap','razao_medias_reais_lag1__milho_dap','selic_efetiva_anualizada_media_anual_lag1_pct_aa']
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ler(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def csvout(name,rows):
    with (P/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def js(name,data):(P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def planilha_xml(path):
    # Leitor independente de openpyxl: resolve aba, strings e coordenadas OOXML.
    with zipfile.ZipFile(path) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
        wb=ET.fromstring(z.read('xl/workbook.xml'))
        sheet=next(x for x in wb.find('s:sheets',NS) if x.attrib['name']=='Monthly Prices')
        rid=sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
        rel=next(x for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels')) if x.attrib['Id']==rid)
        target=rel.attrib['Target']; target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
        rows=[]
        for row in ET.fromstring(z.read(target)).findall('s:sheetData/s:row',NS):
            d={}
            for c in row:
                col=''.join(x for x in c.attrib['r'] if x.isalpha());v=c.find('s:v',NS)
                if c.attrib.get('t')=='inlineStr':value=''.join(c.find('s:is',NS).itertext())
                elif v is None:value=None
                elif c.attrib.get('t')=='s':value=strings[int(v.text)]
                else:
                    try:value=float(v.text)
                    except ValueError:value=v.text
                d[col]=value
            rows.append(d)
        return rows

def auditar():
    assert hashfile(V1)==HASH_V1,'V1 alterada'
    provenance=json.loads((F/'proveniencia_v2.json').read_text())
    for name,expected in provenance['hashes'].items():assert hashfile(F/name)==expected,name
    meta=json.loads((F/'manifesto_deflatores.json').read_text())
    assert hashfile(F/'bls_fred_CPIAUCNS_1960_2024.csv')==meta['fontes']['cpi']['sha256']
    rows=planilha_xml(F/'pink_sheet_monthly_20260930.xlsx')
    header=next(r for r in rows if r.get('BG')=='DAP')
    cols={k:next(c for c,v in header.items() if v==n) for k,n in [('soja','Soybeans'),('milho','Maize'),('dap','DAP')]}
    units=rows[rows.index(header)+1]
    assert all(units[c]=='($/mt)' for c in cols.values())
    raw=[r for r in rows if isinstance(r.get('A'),str) and len(r['A'])==7 and r['A'][4]=='M']
    assert len({r['A'] for r in raw})==len(raw),'Datas WB duplicadas'
    wb={r['A']:r for r in raw}
    cp=ler(F/'bls_fred_CPIAUCNS_1960_2024.csv')
    assert len({r['observation_date'] for r in cp})==len(cp)
    cpi={r['observation_date'][:7]:float(r['CPIAUCNS']) for r in cp}
    base=st.mean(cpi[f'2024-{m:02d}'] for m in range(1,13))
    # CSV transmitido do HTML SGS oficial; hashes exatos recebidos do coletor.
    sp=json.loads((F/'sgs4189_provenance.json').read_text())
    for name in ['sgs4189_2000_2024.csv','sgs4189_annual_lag_panel2001_2024.csv']:
        assert hashfile(F/name)==sp['sha256'][name]
    sr=ler(F/'sgs4189_2000_2024.csv')
    assert [r['date'] for r in sr]==[f'{y}-{m:02d}-01' for y in range(2000,2025) for m in range(1,13)]
    selic={r['date'][:7]:float(r['selic_4189_percent_pa']) for r in sr}
    assert len(selic)==300 and all(math.isfinite(v) and v>0 for v in selic.values())
    official=ler(F/'dap_official_2000_2023.csv')
    assert len(official)==288 and len({r['date'] for r in official})==288
    for r in official:
        key=r['date'][:7].replace('-','M')
        assert r['unit']=='USD/metric tonne' and float(r['value'])==float(wb[key][cols['dap']])
    comparison=json.loads((F/'wb_confronto_summary.json').read_text())
    assert comparison['hashes']['drive_pink_sheet_monthly_20260930.xlsx']==hashfile(F/'pink_sheet_monthly_20260930.xlsx')
    assert all(x['n']==288 and x['mismatches']==0 for x in comparison['comparison'].values())
    monthly=[];annual=[];diff=[];v1=ler(V1)
    for year in range(2000,2024):
        subset=[]
        for month in range(1,13):
            key=f'{year}-{month:02d}';r=wb[f'{year}M{month:02d}']
            values={k:float(r[c]) for k,c in cols.items()}
            assert all(math.isfinite(v) and v>0 for v in [*values.values(),cpi[key]])
            row={'mes':key,'cpi_u':cpi[key],**{k+'_usd_t':v for k,v in values.items()},**{k+'_usd2024_t':v*base/cpi[key] for k,v in values.items()},'selic_4189_pct_aa':selic.get(key,'')}
            subset.append(row);monthly.append(row)
        av={k:st.mean(r[k+'_usd2024_t'] for r in subset) for k in cols}
        original=next(r for r in v1 if int(r['ano'])==year+1)
        for crop in ['soja','milho']:
            delta=av[crop]-float(original[f'preco_real_usd2024_media_anual_lag1__{crop}'])
            diff.append({'ano_referencia':year,'produto':crop,'diferenca':delta})
            assert abs(delta)<1e-9,'Divergência de vintage/deflação: interromper join'
        rates=[r['selic_4189_pct_aa'] for r in subset if r['selic_4189_pct_aa']!='']
        annual.append({'ano':year+1,'ano_referencia':year,NOVAS[0]:av['dap'],NOVAS[1]:av['soja']/av['dap'],NOVAS[2]:av['milho']/av['dap'],NOVAS[3]:st.mean(rates) if len(rates)==12 else '', 'meses_wb_cpi':12,'meses_selic':len(rates),'flag_selic_incompleta':len(rates)!=12})
    csvout('auditoria_mensal_v2.csv',monthly);csvout('economia_anual_v2.csv',annual);csvout('coerencia_precos_v1_v2.csv',diff)
    audit={'status':'PARCIAL_SELIC_PENDENTE' if not selic else 'SERIES_DISPONIVEIS','meses_wb_cpi':288,'janela':'2000-01 a 2023-12','cpi_base_media_2024':base,'max_diferenca_precos_v1':max(abs(r['diferenca']) for r in diff),'meses_selic_no_recorte':sum(r['selic_4189_pct_aa']!='' for r in monthly),'fonte_oficial_wb_confrontada':True,'limitacao_wb':'Confronto oficial 864 células realizado no ambiente pai; 288 DAP reconferidos localmente. XLSX oficial/HTML SGS preservados no ambiente pai; hashes e extratos locais. Validação restrita ao recorte.', 'regra':'Média de 12 preços mensais deflacionados CPI-U; razões das médias anuais; Selic média temporal do nível anualizado (não acumulada).','hash_v1':HASH_V1,'hashes_fontes':provenance['hashes']}
    js('auditoria_pre_join_v2.json',audit)
    # Conferência independente das médias anuais recebidas, antes de apensar.
    received=ler(F/'sgs4189_annual_lag_panel2001_2024.csv')
    assert len(received)==24
    for a,r in zip(annual,received):
        assert a['ano']==int(r['ano']) and a['ano_referencia']==int(r['ano_origem'])
        assert int(r['n_meses'])==12 and abs(a[NOVAS[3]]-float(r['selic_media_ano_anterior_pct_aa']))<1e-12
    (P/'AUDITORIA_PRE_JOIN_V2.md').write_text(f"""# Auditoria anterior ao apensamento — base3 v2 completa

PASS: 288 meses completos janeiro2000–dezembro2023 para DAP/soja/milho/CPI/Selic, sem duplicatas, finitos e positivos. SGS bruto extraído contém300meses2000–24; os12meses2024 não entram nos outcomes. Hashes dos CSVs SGS mensal/anual coincidem exatamente com os transmitidos pelo coletor oficial. Recalculadas24médias anuais de12meses, diferença inferior a1e-12 frente ao extrato anual independente.

DAP oficial:288valores recebidos coincidem exatamente com o XLSX Drive local. Relatório de confronto externo documenta864células iguais (DAP/soja/milho) e zero divergências. Dois leitores locais também concordam nessas864células. Arquivos XLSX têm hashes/vintages diferentes, não bytes iguais. Ambos contêm Mismatch Details; isso não prova adulteração. Fontes, hashes e limites em fontes_v2/CONFRONTO_OFICIAL.md. XLSX oficial e HTML bruto SGS permanecem no ambiente pai; não afirmar que estão locais.

CPI-U confere com manifesto; base média2024={base}. Média dos12preços mensais deflacionados no ano anterior. Preços soja/milho preservados da v1 reconciliados com diferença máxima {audit['max_diferenca_precos_v1']:.3g}. Razões das médias anuais reais, não médias das razões; deflator comum cancela mensalmente, mas a ponderação anual importa. Selic4189 é média temporal do nível anualizado %a.a., não acumulada ou meta. Nenhuma imputação ou modelo.

Decisão: PASS para apensar quatro campos por ano (many-to-one), preservando42colunas e3384chaves. São24valores anuais repetidos, não3384choques. DAP é proxy parcial de insumos, não custo/ha. Preços e Selic comuns são absorvidos por FEano. Vintage retrospectivo não equivale à informação disponível em tempo real; CPI2024 fixa apenas a unidade monetária.
""",encoding='utf-8')
    return annual,audit

def juntar():
    # Executar auditoria e gravar parecer antes de qualquer escrita do painel.
    annual,audit=auditar(); lookup={r['ano']:r for r in annual};assert len(lookup)==24
    original=ler(V1);result=[]
    for r in original:
        a=lookup[int(r['ano'])];result.append({**r,**{c:a[c] for c in NOVAS}})
    assert len(result)==3384 and len({(r['codigo_ibge'],r['ano']) for r in result})==3384
    csvout('painel_h1_base3_v2.csv',result)
    js('manifesto_v2.json',{'versao':'base3_v2_parcial' if audit['meses_selic_no_recorte']<288 else 'base3_v2','linhas':3384,'colunas':46,'municipios':141,'fonte_v1_sha256':HASH_V1,'auditoria_previa_sha256':hashfile(P/'auditoria_pre_join_v2.json'),'sha256_painel':hashfile(P/'painel_h1_base3_v2.csv'),'fontes':audit['hashes_fontes'],'sem_modelos':True})
    print(json.dumps({'status':audit['status'],'linhas':3384,'colunas':46,'sha256':hashfile(P/'painel_h1_base3_v2.csv')}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apensar',action='store_true');args=parser.parse_args()
    juntar() if args.apensar else auditar()
