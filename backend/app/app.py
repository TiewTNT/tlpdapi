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
import asyncio
from time import sleep

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


async def cleanup(hash):
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


def compile_convert(file_folder, output_folder, converted_output_folder, zip_dir, engine, macro, compile_tool, compile_folder, tex_paths, tools, compiles, format, format_image, dpi):
    pdf_paths, stem = compile(
        file_folder=file_folder,
        output_folder=output_folder,
        engine=engine,
        macro=macro,
        compile_tool=compile_tool,
        tools=tools,
        compiles=int(compiles),
        compile_folder=Path(compile_folder),
        tex_paths=[Path(tex_path) for tex_path in tex_paths]
    )
    final_path = convert(
        file_paths=pdf_paths,
        output_folder=converted_output_folder,
        zip_folder=zip_dir,
        format=format,
        image_format=format_image,
        dpi=dpi
    )
    return final_path, stem


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
    compile_tool: str = Form('latexmk'),
    compile_folder: str = Form('/'),
    tex_paths: List[str] = Form(['/main.tex']),
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

    # background_tasks.add_task(cleanup, hash)
    try:
        final_path, stem = await asyncio.wait_for(
            asyncio.to_thread(compile_convert, PROJECTS_DIR / hash, OUTPUT_DIR / hash, CONVERTED_OUTPUT_DIR /
                              hash, ZIP_OUTPUT_DIR, engine, macro, compile_tool, Path(compile_folder), tex_paths, tools, compiles, format, format_image, dpi),
            timeout=120
        )
    except asyncio.TimeoutError as e:
        print(e)
        if webhook_url:
            background_tasks.add_task(send_webhook, webhook_url, {
                                      "status": "timeout", "code": 1})
        return JSONResponse(content={
            "error": str(e),
            "message": "Subprocesses timed out"
        }, status_code=500)
    except Exception as e:
        print(e)
        if webhook_url:
            background_tasks.add_task(send_webhook, webhook_url, {
                                      "status": "error during compile / convert", "code": 1})
        return JSONResponse(content={
            "error": str(e),
            "message": "Error during compile or conversion process."
        }, status_code=500)

    else:
        if not final_path.exists():
            print("Final path doesn't exist.")
            if webhook_url:
                background_tasks.add_task(send_webhook, webhook_url, {
                                          "status": "error: final path does not exist", "code": 1})
            return JSONResponse(content={
                "error": "",
                "message": "Error during compile or conversion process."
            }, status_code=500)
        if webhook_url:
            background_tasks.add_task(send_webhook, webhook_url, {
                                      "status": "success", "code": 0})
        return FileResponse(
            final_path,
            media_type=mime_types.get(
                final_path.suffix[1:], 'application/octet-stream'),
            filename=stem + (final_path.suffix)
        )

app.mount("/", StaticFiles(directory=FRONTEND /
          'build', html=True), name="static")
