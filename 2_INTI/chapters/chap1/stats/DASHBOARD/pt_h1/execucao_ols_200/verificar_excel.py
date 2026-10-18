"""Somente leitura: reabre Excel final e compara cada célula com registros locais."""
from pathlib import Path
import json, collections, math, hashlib, zipfile, datetime
import openpyxl
HERE=Path(__file__).resolve().parent
APP=HERE.parent
ROOT=next(p for p in APP.parents if (p/'2_INTI/RESEARCH_PROTOCOL.md').exists())
path=APP/'RESULTADOS_DASH_H1.xlsx'
expected=json.loads((HERE/'excel_payload.json').read_text(encoding='utf-8'))
records=json.loads((HERE/'resultados_completos.json').read_text(encoding='utf-8'))
metadata=json.loads((HERE/'metadata.json').read_text(encoding='utf-8'))
wb=openpyxl.load_workbook(path,data_only=False)
assert wb.sheetnames==['Resultados','Detalhes','Coeficientes','Metodologia']
cells=0
for name,rows in expected.items():
    sh=wb[name]
    assert sh.max_row==len(rows),(name,sh.max_row,len(rows))
    assert sh.max_column==len(rows[0])
    assert sh.freeze_panes=='A2',(name,sh.freeze_panes)
    assert len(sh.tables)==1
    assert next(iter(sh.tables.values())).autoFilter is not None
    for i,row in enumerate(rows,1):
        for j,value in enumerate(row,1):
            actual=sh.cell(i,j).value
            if value=='': value=None
            if isinstance(value,(int,float)) and not isinstance(value,bool):
                assert isinstance(actual,(int,float)) and math.isfinite(actual),(name,i,j,actual)
                assert math.isclose(actual,value,rel_tol=1e-13,abs_tol=1e-15),(name,i,j,actual,value)
            else: assert actual==value,(name,i,j,str(actual)[:100],str(value)[:100])
            assert sh.cell(i,j).data_type!='e',(name,i,j,actual)
            cells+=1
results=list(wb['Resultados'].values)
assert results[0]==('Variável dependente','Variáveis Independentes','R2')
counts=collections.Counter(v[0] for v in results[1:])
assert len(counts)==4 and set(counts.values())=={50}
assert len(set((v[0],v[1]) for v in results[1:]))==200
details=list(wb['Detalhes'].values)
originals=[row for row in details[1:] if row[3]=='Original — conta na meta']
assert len(originals)==200
assert {row[2] for row in originals}=={f'M{i:03}' for i in range(1,201)}
for result,detail,record in zip(results[1:],originals,records):
    assert result[:2]==detail[:2]
    assert result[2]==detail[8]
    assert detail[10]==record['summary']['N']
    assert detail[11]==len(record['coef']) and detail[12]==detail[10]-detail[11]
    assert record['plan']['spec']['fe']=='none'
    assert record['plan']['spec']['cov']=='cluster_entity'
    assert record['coef'][0]['term']=='const'
ids={row[2] for row in details[1:]}
coef=list(wb['Coeficientes'].values)
assert {row[0] for row in coef[1:]}==ids
for row in details[1:]:
    assert sum(v[0]==row[2] for v in coef[1:])==row[11]
assert sum(row[3].startswith('Conferência') for row in details[1:])==12
assert len(json.loads((HERE/'conferencia_dashboard.json').read_text(encoding='utf-8')))==4
hashpath=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert hashpath(ROOT/metadata['meta']['csv'])==metadata['meta']['csv_sha256']
for source,digest in metadata['code_hashes'].items(): assert hashpath(ROOT/source)==digest
with zipfile.ZipFile(path) as z:
    assert z.testzip() is None
out={'arquivo':str(path),'sha256':hashpath(path),'abas':wb.sheetnames,'contagens':dict(counts),'originais_validos':200,
     'conferencias_amostra_comum':12,'conferencias_dashboard':4,'termos':len(coef)-1,'celulas_comparadas':cells,
     'duplicatas':0,'erros_excel':0,'codigo_e_csv_preservados':True,'status':'VERIFICADO',
     'checked':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat()}
(HERE/'verificacao.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False))
