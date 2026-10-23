"""Executa notebooks em kernels novos e valida resultados, sem operações Git de escrita."""
from pathlib import Path
import os,json,sys,subprocess,time
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('IPYTHONDIR','/tmp/chap1-ipython')
os.environ.setdefault('JUPYTER_RUNTIME_DIR','/tmp/chap1-jupyter')
import nbformat
from nbclient import NotebookClient
p=Path(__file__).resolve().parent
r=next(x for x in p.parents if (x/'AGENTS.md').exists())
a=r/'2_INTI/audit/testes_chap1_20261023'
ordem=['auditoria','ols_simples','ols_multiplo','painel','alternativas','quebras_temporais','avaliacao_desenho']
logs=[]
for nome in ordem:
 t=time.time();arquivo=p/(nome+'.ipynb');nb=nbformat.read(arquivo,as_version=4)
 NotebookClient(nb,timeout=600,kernel_name='python3',resources={'metadata':{'path':str(p)}}).execute()
 nbformat.validate(nb)
 cells=[c for c in nb.cells if c.cell_type=='code']
 assert all(c.execution_count is not None for c in cells)
 assert not any(o.output_type=='error' for c in cells for o in c.outputs)
 nbformat.write(nb,arquivo)
 logs.append({'notebook':nome,'celulas':len(cells),'erros':0,'segundos':round(time.time()-t,2)})
 (a/'execucao_completa.json').write_text(json.dumps(logs,indent=2))
 print('CONCLUÍDO',nome,flush=True)
subprocess.run([sys.executable,str(p/'consolidar.py')],check=True)
subprocess.run([sys.executable,str(p/'sintetizar.py')],check=True)
(a/'dependencias_estimacao.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True))
print('VALIDAÇÃO END-TO-END CONCLUÍDA',flush=True)
