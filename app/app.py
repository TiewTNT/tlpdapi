from fastapi import FastAPI, File, Form, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
import hashlib
from pathlib import Path
import os
import shutil
from compile import compile
ROOT = Path(__file__).resolve().parent.parent

APP_DIR = ROOT / 'app'
OUTPUT_DIR = ROOT / 'output'
PROJECTS_DIR = ROOT / 'project_folders'


app = FastAPI()

def cleanup(hash):
    shutil.rmtree(OUTPUT_DIR / hash, ignore_errors=True)
    shutil.rmtree(PROJECTS_DIR / hash, ignore_errors=True)


@app.post('/api')
async def api(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(),
    engine: str = Form('engine'),
    format: str = Form('format'),
    tools: List[str] = Form('tools'),
    compiles: int = Form('compiles'),
    time: str = Form('time'),
):
    
    hash = str(hashlib.sha256(time.encode()).hexdigest())
    os.makedirs(PROJECTS_DIR / hash, exist_ok=True)
    os.makedirs(OUTPUT_DIR / hash, exist_ok=True)

    for file in files:
        file_path = PROJECTS_DIR / hash / file.filename
        with file_path.open('wb') as f:
            shutil.copyfileobj(file.file, f)

    if len(files) == 1 and Path(files[0].filename).suffix == '.zip':
        shutil.unpack_archive(PROJECTS_DIR / hash / files[0].filename, PROJECTS_DIR / hash)

    compile(
        file_folder=PROJECTS_DIR / hash,
        output_folder=OUTPUT_DIR / hash,
        engine=engine,
        tools=tools,
        compiles=int(compiles)
    )

    # background_tasks.add_task(cleanup, hash)
    return # FileResponse() (not now)