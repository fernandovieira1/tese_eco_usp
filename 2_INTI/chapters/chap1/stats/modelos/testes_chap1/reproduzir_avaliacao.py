"""Compatibilidade: use executar_tudo.py para reprodução completa."""
from pathlib import Path
import subprocess,sys
subprocess.run([sys.executable,str(Path(__file__).with_name('executar_tudo.py'))],check=True)
