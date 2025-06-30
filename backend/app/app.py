from fastapi import FastAPI, File, Form, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
import hashlib
from pathlib import Path
import os
import shutil
from compile import compile
from convert import convert
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware


ROOT = Path(__file__).resolve().parent.parent

APP_DIR = ROOT / 'app'
OUTPUT_DIR = ROOT / 'compiled_output'
CONVERTED_OUTPUT_DIR = ROOT / 'converted_output'
ZIP_OUTPUT_DIR = ROOT / 'zip_output'
PROJECTS_DIR = ROOT / 'project_folders'


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def cleanup(hash):
    shutil.rmtree(OUTPUT_DIR / hash, ignore_errors=True)
    shutil.rmtree(PROJECTS_DIR / hash, ignore_errors=True)


@app.post('/api')
async def api(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(),
    engine: str = Form('pdflatex'),
    macro: str = Form('latex'),
    format: str = Form('pdf'),
    format_image: str = Form('png'),
    dpi: int = Form(200),
    tools: List[str] = Form([]),
    compiles: int = Form(3),
    compile_tool: str = Form('manual')
):

    hash = str(hashlib.sha256(
        datetime.utcnow().isoformat().encode()).hexdigest())
    os.makedirs(PROJECTS_DIR / hash, exist_ok=True)
    os.makedirs(OUTPUT_DIR / hash, exist_ok=True)

    for file in files:
        file_path = PROJECTS_DIR / hash / file.filename
        with file_path.open('wb') as f:
            shutil.copyfileobj(file.file, f)

    if len(files) == 1 and Path(files[0].filename).suffix == '.zip':
        shutil.unpack_archive(PROJECTS_DIR / hash /
                              files[0].filename, PROJECTS_DIR / hash)

    pdf_path = compile(
        file_folder=PROJECTS_DIR / hash,
        output_folder=OUTPUT_DIR / hash,
        engine=engine,
        macro=macro,
        compile_tool=compile_tool,
        tools=tools,
        compiles=int(compiles)
    )
    final_path = convert(
        file_path=pdf_path,
        output_folder=CONVERTED_OUTPUT_DIR / hash,
        zip_folder=ZIP_OUTPUT_DIR,
        format=format,
        image_format=format_image,
        dpi=dpi
    )

    background_tasks.add_task(cleanup, hash)
    return FileResponse(
        final_path,
        media_type='application/zip' if final_path.suffix == '.zip' else f'application/{format}',
        filename=final_path.name
    )
