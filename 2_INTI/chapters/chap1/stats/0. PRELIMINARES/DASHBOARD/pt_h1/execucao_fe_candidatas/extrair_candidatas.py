from pathlib import Path
import openpyxl,json,hashlib,datetime
HERE=Path(__file__).resolve().parent
source=HERE.parent/'RESULTADOS_DASH_H1.xlsx'
wb=openpyxl.load_workbook(source,read_only=True,data_only=True)
rows=list(wb['Detalhes'].values); header=rows[0]
candidates=[dict(zip(header,r)) for r in rows[1:] if str(r[33]).startswith('Candidata')]
assert len(candidates)==12
assert {r['ID do modelo'] for r in candidates}=={'M022','M042','M046','M072','M092','M096','M122','M142','M146','M172','M192','M196'}
payload={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'created':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat(),
 'candidates':sorted(candidates,key=lambda r:r['ID do modelo'])}
(HERE/'candidatas_origem.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
print('12 candidatas extraídas da planilha atual; SHA256='+payload['sha256'])
