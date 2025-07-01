import subprocess
from pathlib import Path
import sys

current_file = Path(__file__)
current_dir = current_file.resolve().parent

subprocess.run([Path(sys.executable), '-m', 'uvicorn', 'app:app', "--host", "0.0.0.0", "--port", "8000"], check=True, cwd=current_dir / 'app')