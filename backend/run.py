import subprocess
from pathlib import Path
import sys
import os

PORT = os.getenv('PORT', '8000')

current_file = Path(__file__)
current_dir = current_file.resolve().parent

subprocess.run([Path(sys.executable), '-m', 'uvicorn', 'app:app', "--host", "0.0.0.0", "--port", PORT], check=True, cwd=current_dir / 'app')