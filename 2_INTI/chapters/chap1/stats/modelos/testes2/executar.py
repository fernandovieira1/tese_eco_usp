"""Executor das rodadas locais; kernels novos, estratégia anterior e hashes."""
import os,sys,json,time,hashlib,subprocess
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
os.environ.setdefault('IPYTHONDIR','/tmp/chap1-ipython');os.environ.setdefault('JUPYTER_RUNTIME_DIR','/tmp/chap1-jupyter')
import nbformat
from nbclient import NotebookClient
from metodos import consolidar
p=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
r=next(x for x in p.parents if (x/'AGENTS.md').exists());a=r/'2_INTI/audit'/p.name;a.mkdir(exist_ok=True,parents=True)
ordem=json.loads((p/'ordem.json').read_text())
assert (p/'ESTRATEGIA.md').exists()
protegidos=[p.parent/'painel_municipal_descritiva_h1.csv',*list((r/'2_INTI/chapters/chap1/text').glob('*.tex')),*[f for f in (p.parent/'testes_chap1').iterdir() if f.is_file()]]
hashes={str(f.relative_to(r)):hashlib.sha256(f.read_bytes()).hexdigest() for f in protegidos}
meta={'inicio_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'estrategia_sha256':hashlib.sha256((p/'ESTRATEGIA.md').read_bytes()).hexdigest(),'estrategia_mtime':(p/'ESTRATEGIA.md').stat().st_mtime,'hashes_protegidos':hashes,'semente':20261023,'python':sys.version}
assert meta['estrategia_mtime']<time.time()
(p/'METADADOS.json').write_text(json.dumps(meta,indent=2));(p/'tentativas.jsonl').write_text('')
log=[]
for nome in ordem:
 t=time.time();f=p/(nome+'.ipynb');nb=nbformat.read(f,as_version=4)
 try:NotebookClient(nb,timeout=1200,kernel_name='python3',resources={'metadata':{'path':str(p)}}).execute()
 except Exception as exc:
  (a/'falha.txt').write_text(str(exc));raise
 nbformat.validate(nb);cells=[c for c in nb.cells if c.cell_type=='code'];assert all(c.execution_count for c in cells)
 assert not any(o.output_type=='error' for c in cells for o in c.outputs)
 nbformat.write(nb,f);log.append({'notebook':nome,'celulas':len(cells),'erros':0,'segundos':round(time.time()-t,2)})
 (p/'EXECUCAO.json').write_text(json.dumps(log,indent=2));print('CONCLUÍDO',p.name,nome,flush=True)
c,m,j=consolidar(p)
for f,h in hashes.items():assert hashlib.sha256((r/f).read_bytes()).hexdigest()==h, 'Arquivo protegido alterado: '+f
assert hashlib.sha256((p/'ESTRATEGIA.md').read_bytes()).hexdigest()==meta['estrategia_sha256']
validation={'notebooks':len(log),'modelos':len(m),'coeficientes':len(c),'preservacao':True,'estrategia_inalterada':True,'coeficientes_finitos':True,'publicacao':'proibida nesta rodada'}
(p/'VALIDACAO.json').write_text(json.dumps(validation,indent=2));(a/'validacao.json').write_text(json.dumps(validation,indent=2))
(p/'requirements.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True))
if (p/'sintetizar.py').exists():subprocess.run([sys.executable,str(p/'sintetizar.py')],cwd=p,check=True)
print(validation,flush=True)
