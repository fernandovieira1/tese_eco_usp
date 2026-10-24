"""Restaura, sem executar regressões, o checkout histórico publicado em destino novo."""
from pathlib import Path
import argparse,subprocess
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--destino',required=True,type=Path);a=ap.parse_args()
 if a.destino.exists():raise SystemExit('Use um destino inexistente; nenhum diretório será sobrescrito.')
 repo=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').exists())
 subprocess.run(['git','clone','--no-hardlinks',str(repo),str(a.destino)],check=True)
 subprocess.run(['git','checkout','--detach','26a17415c3c99df1af8925913c541e40534396c5'],cwd=a.destino,check=True)
 print('Layout histórico restaurado; nenhum modelo executado.')
