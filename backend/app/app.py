from fastapi import FastAPI, File, Form, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from typing import List
import hashlib
from pathlib import Path
import os
import shutil
from compile import compile
from convert import convert
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import httpx

ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND = ROOT / 'backend'
FRONTEND = ROOT / 'frontend'

APP_DIR = BACKEND / 'app'
OUTPUT_DIR = BACKEND / 'compiled_output'
CONVERTED_OUTPUT_DIR = BACKEND / 'converted_output'
ZIP_OUTPUT_DIR = BACKEND / 'zip_output'
PROJECTS_DIR = BACKEND / 'project_folders'

mime_types = {
    "html": "text/html",
    "md": "text/markdown",
    "txt": "text/plain",
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "zip": "application/zip",
}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def cleanup(hash):
    try:
        shutil.rmtree(PROJECTS_DIR / hash, ignore_errors=True)
        shutil.rmtree(OUTPUT_DIR / hash, ignore_errors=True)
        shutil.rmtree(CONVERTED_OUTPUT_DIR / hash, ignore_errors=True)
        os.remove(ZIP_OUTPUT_DIR / (hash + '.zip'))
    except Exception as e:
        print('Cleanup failed: '+str(e))
    return

async def send_webhook(url: str, payload: dict):
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload)
        except Exception as e:
            print(f"Webhook error: {e}")


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
    compile_tool: str = Form('manual'),
    webhook_url: str | None = None,
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
    background_tasks.add_task(cleanup, hash)
    try:
        pdf_path, stem = compile(
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
    except Exception as e:
        print(e)
        if webhook_url:
            background_tasks.add_task(send_webhook, webhook_url, {"status": "error during compile / convert", "code": 1})
        return JSONResponse(content={
            "error": str(e),
            "message": "Error during compile or conversion process."
        }, status_code=500)

    else:
        if not final_path.exists():
            print("Final path doesn't exist.")
            if webhook_url:
                background_tasks.add_task(send_webhook, webhook_url, {"status": "error: final path does not exist", "code": 1})
            return JSONResponse(content={
                "error": str(e),
                "message": "Error during compile or conversion process."
            }, status_code=500)
        if webhook_url:
            background_tasks.add_task(send_webhook, webhook_url, {"status": "success", "code": 0})
        return FileResponse(
            final_path,
            media_type=mime_types.get(
                final_path.suffix[1:], 'application/octet-stream'),
            filename=stem + (final_path.suffix)
        )

app.mount("/", StaticFiles(directory=FRONTEND /
          'build', html=True), name="static")
