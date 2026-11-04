from pathlib import Path
import subprocess,sys
p=Path(__file__).resolve().parent
for name in ['construir.py','validar.py']:subprocess.run([sys.executable,str(p/name)],check=True)
