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


def compile(file_folder: Path,
            output_folder: Path,
            engine: str = 'pdflatex',
            macro: str = 'latex',
            tools: list = (),
            compile_tool: str = 'manual',
            compiles: int = 2) -> Path:
    
    if len(list(file_folder.rglob("*"))) == 1 and Path(list(file_folder.rglob("*"))[0]).suffix == '.zip':
        print('UNPACKING ZIP')
        shutil.unpack_archive(str(file_folder / Path(list(file_folder.rglob("*"))[0]).stem) + '.zip', str(output_folder))
        if os.name == "nt":
            output_folder = output_folder / Path(list(file_folder.rglob("*"))[0]).stem

    else:
        print('FILE FOLDER RGLOB *:', file_folder.rglob("*"))
        shutil.copytree(file_folder, output_folder, dirs_exist_ok=True)
    # find the .tex
    file_path = output_folder / 'main.tex'
    if not file_path.exists():
        candidates = list(output_folder.rglob('*.tex'))
        print(candidates, 'CANDIDATES')
        if not candidates:
            raise FileNotFoundError("No .tex file in the provided folder.")
        file_path = candidates[0]

    output_folder.mkdir(parents=True, exist_ok=True)

    stem = file_path.stem

    if macro == 'context':
        # Context writes *all* outputs into cwd; include file_folder on TEXINPUTS if needed
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
                f'-pdflatex="{engine} -interaction=nonstopmode"',
                '-pdf',
                '-outdir=' + str(output_folder),
                file_path
            ], cwd=output_folder, check=True)
        # elif compile_tool == 'tectonic': # tectonic is not included in texlive-full
        #     # Use tectonic for compilation
        #     subprocess.run([
        #         'tectonic',
        #         str(file_path),
        #         '--outdir', str(output_folder)
        #     ], cwd=file_folder, check=True)

    # finally, point at your new PDF
    return output_folder / f"{stem}.pdf", stem
