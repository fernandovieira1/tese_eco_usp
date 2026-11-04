from pathlib import Path
import subprocess,sys
p=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(p.parent/'testes2/executar.py'),str(p)],check=True)
subprocess.run([sys.executable,str(p/'validar.py')],check=True)
