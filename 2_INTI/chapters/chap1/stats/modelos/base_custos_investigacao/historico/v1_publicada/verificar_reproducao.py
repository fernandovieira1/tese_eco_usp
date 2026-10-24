"""Duas construções isoladas; compara bytes das saídas determinísticas."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
hashes=lambda p:{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.glob('*.csv'))}
def verificar():
 esperado=hashes(P);execucoes=[]
 for _ in range(2):
  with tempfile.TemporaryDirectory(prefix='custos_repro_') as temp:
   destino=Path(temp)
   shutil.copytree(P/'fontes',destino/'fontes')
   shutil.copy2(P/'construir.py',destino/'construir.py')
   shutil.copy2(P/'construir_imea.py',destino/'construir_imea.py')
   # Dicionário e decisões são entradas documentais, não dados calculados.
   for nome in ['dicionario_variaveis.csv','candidatos_incorporacao.csv']:
    shutil.copy2(P/nome,destino/nome)
   proc=subprocess.run([sys.executable,str(destino/'construir.py')],capture_output=True,text=True,check=True)
   atual=hashes(destino);assert atual==esperado
   execucoes.append({'hashes_iguais':True,'numero_csv':len(atual),'resumo':json.loads(proc.stdout)})
 resultado={'execucoes_isoladas':execucoes,'hashes_csv':esperado,'python':sys.version,'sem_coleta_rede':True}
 (P/'validacao_reproducao.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n')
 return resultado
if __name__=='__main__':print(json.dumps(verificar(),ensure_ascii=False))
