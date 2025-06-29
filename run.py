import subprocess
from pathlib import Path

current_file = Path(__file__)
current_dir = current_file.resolve().parent

subprocess.run(['py', '-m', 'uvicorn', 'app:app', '--reload'], check=True, cwd=current_dir/'app')