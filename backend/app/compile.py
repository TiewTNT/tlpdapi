import subprocess
from pathlib import Path
import os
import shutil

DANGEROUS_COMMANDS = {
    "rm", "rmdir", "mv", "cp", "dd", "mkfs", "fsck", "shutdown", "reboot",
    "init", "telinit", "kill", "killall", "halt", "poweroff", "systemctl",
    "chmod", "chown", "chgrp", "usermod", "userdel", "groupdel",
    "passwd", "su", "sudo", "bash", "sh", "zsh", "ksh", "dash",
    "python", "python3", "perl", "ruby", "node", "php",
    "wget", "curl", "ftp", "scp", "sftp", "nc", "ncat", "netcat", "telnet",
    "echo", "cat", "tee", "lsblk", "mount", "umount", "losetup", "parted",
    "mktemp", "mkfifo", "xargs", "env", "set", "export", "sl"
}

def safe(path: Path, base: Path):
    try:
        path.resolve().relative_to(base.resolve())
    except ValueError:
        print('PATH', path, 'IS NOT SAFE RELATIVE TO', base)
        return False
    return True

def compile(file_folder: Path,
            output_folder: Path,
            engine: str = 'pdflatex',
            macro: str = 'latex',
            tools: list = (),
            compile_tool: str = 'manual',
            compiles: int = 2,
            compile_folder: Path = Path('/'),
            tex_paths: list = [Path('/main.tex')]) -> Path:
    
    output_root = output_folder
    output_root.mkdir(parents=True, exist_ok=True)
    if len(list(file_folder.rglob("*"))) == 1 and Path(list(file_folder.rglob("*"))[0]).suffix == '.zip':
        print('UNPACKING ZIP')
        shutil.unpack_archive(str(file_folder / Path(list(file_folder.rglob("*"))[0]).stem) + '.zip', str(output_folder))
        print('OUTPUT DIRECTORY FOR COMPILE FUNCTION BEFORE CHANGE:', output_folder)
    else:
        print('FILE FOLDER RGLOB *:', file_folder.rglob("*"))
        shutil.copytree(file_folder, output_root, dirs_exist_ok=True)

    if safe(output_root / compile_folder.relative_to(compile_folder.anchor), output_root):        
        output_folder = output_root / compile_folder.relative_to(compile_folder.anchor)
        print('COMPILE CWD', output_folder, 'SAFE')

    tex_exists = False
    for tex_path in tex_paths:
        if (output_root / tex_path.relative_to(compile_folder.anchor)).exists():
            tex_exists = True
        else:
            tex_paths.remove(tex_path)

    pdf_paths = []

    if not tex_paths:
        candidates = list(output_root.rglob('*.tex'))
        print(candidates, 'CANDIDATES')
        if not candidates:
            raise FileNotFoundError("No .tex file in the provided folder.")
        tex_paths.append(candidates[0])

    for tex_path in tex_paths:
        
        file_path = output_root/tex_path.relative_to(compile_folder.anchor)
        print('ATTEMPTING TO COMPILE', file_path)
        stem = file_path.stem

        if macro == 'context':
            subprocess.run(
                ['context', str(file_path)],
                cwd=output_folder,
                check=True,
            )
        else:
            if compile_tool == 'manual':
                # 1) First pdflatex pass → writes .aux, .pdf, etc into output_folder
                subprocess.run([
                    engine,
                    "-interaction=nonstopmode",
                    "-output-directory", str(output_folder),
                    str(file_path)
                ], cwd=output_folder, check=True)

                # 2) Run your post-processors (bibtex, makeindex, …) *inside* output_folder
                for tool in tools:
                    cmd = tool.strip().split()[0].lower()
                    if cmd in DANGEROUS_COMMANDS:
                        if cmd == 'sl':
                            print("Choo choo trains are not allowed!")
                        else:
                            print(f"Skipping potentially harmful command: {tool}")
                    else:
                        # most tools want just the basename, no extension
                        subprocess.run(
                            [*tool.split(), stem],
                            cwd=output_folder,
                            check=True
                        )

                # 3) Remaining pdflatex passes to resolve references
                for _ in range(compiles - 1):
                    subprocess.run([
                        engine,
                        "-interaction=nonstopmode",
                        "-output-directory", str(output_folder),
                        str(file_path)
                    ], cwd=output_folder, check=True)
            elif compile_tool == 'latexmk':
                # Use latexmk to handle the compilation process
                subprocess.run([
                    'latexmk',
                    '-f',
                    f'-pdflatex={engine} -interaction=nonstopmode %O %S',
                    '-pdf',
                    '-outdir=' + str(output_folder),
                    file_path
                ], cwd=output_folder, check=True)
        pdf_paths.append(output_folder / f"{stem}.pdf")
    # finally, point at your new PDF
    return pdf_paths, stem
