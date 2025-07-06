import subprocess
import shutil
from pathlib import Path
import os
import tempfile
from PIL import Image
import io
from utils import clamp, generate_frag


# def remove_patterns_from_file(file_path: Path, patterns: regex.Pattern):
#     """Remove lines matching the given regex patterns from a file."""
#     with file_path.open('r', encoding='utf-8') as file:
#         html = file.read()

#     with file_path.open('w', encoding='utf-8') as file:
#         file.write(
#             regex.sub(patterns, '', html)
#         )


def convert(file_paths, output_folder, zip_folder, format='pdf', image_format='png', dpi=200, bg_color={"r": 255, "g": 255, "b": 255, "a": 1}, raster_plasma=False, invert=False, frag_path: str | Path | None=None, use_frag: bool = False, cwd: str | Path | None=None):
    if not cwd:
        cwd = Path(file_paths[0]) if Path(file_paths[0]).isdir() else Path(file_paths[0]).parent
    else:
        cwd = Path(cwd)

    if use_frag:
        if frag_path:
            if Path(frag_path).exists():
                ...
            else:
                frag_files = []
                for frag in list(cwd.rglob("*.frag")):
                    frag_files.append(frag)
                if frag_files:
                    frag_path = frag_files[0]
                else:
                    frag_path = None
        else:
            frag_files = []
            for frag in list(cwd.rglob("*.frag")):
                frag_files.append(frag)
            if frag_files:
                frag_path = frag_files[0]
    else:
        frag_path = None

    os.makedirs(output_folder, exist_ok=True)
    for file_path in file_paths:
        if format == 'pdf':
            shutil.copy(file_path, output_folder / file_path.name)
        elif format in ['md', 'txt', 'html']:
            subprocess.run(['pdftohtml', '-c', '-s', '-noframes', str(file_path),
                            Path(str(output_folder / file_path.stem) + '.html')], check=True, cwd=cwd)
            if format in ['md', 'txt']:
                # remove_patterns_from_file(Path(str(output_folder / file_path.stem) + '.html'),
                #                         regex.compile(rf'<img\s+width="\d+"\s+height="\d+"\s+src="{regex.escape(file_path.stem)}\d+\.png"\s+alt="background image"\s*/?>', regex.DOTALL))

                # subprocess.run(['pandoc', Path(str(output_folder / file_path.stem) + '.html'), '-t', 'markdown_strict',
                #             '-o', Path(str(output_folder / file_path.stem) + '.md')], check=True)

                # os.remove(Path(str(output_folder / file_path.stem) + '001.png'))
                os.remove(Path(str(output_folder / file_path.stem) + '.html'))
                if format == 'txt':
                    subprocess.run(['pandoc', Path(str(output_folder / file_path.stem) + '.md'), '-t', 'plain',
                                    '-o', Path(str(output_folder / file_path.stem) + '.txt')], check=True, cwd=cwd)
                    os.remove(Path(str(output_folder / file_path.stem) + '.md'))
        elif format == 'raster':
            # Step 1: Create output pattern
            raster_dir = output_folder / f"{file_path.stem}_raster"
            os.makedirs(raster_dir, exist_ok=True)

            # Step 2: Convert each PDF page to PNG
            fg_cmd = [
                "magick",
                "-density", str(dpi),
                str(file_path),
                
            ]
            if invert:
                fg_cmd.extend(["-channel", "RGB", "-negate", "+channel"])
            fg_cmd.append(str(raster_dir / f"{file_path.stem}_%03d.png"))
            subprocess.run(fg_cmd, check=True, cwd=cwd)

            # Step 3: Composite each over background
            for page_path in sorted(Path(raster_dir).glob("*.png")):
                with Image.open(page_path) as img:
                    w, h = img.width, img.height
                rgba = f"rgba({bg_color['r']},{bg_color['g']},{bg_color['b']},{bg_color['a']})"
                # Create background
                if raster_plasma:
                    bg_image = subprocess.run([
                        "magick", "-size", f"{w}x{h}", f"plasma:{rgba}-{rgba}", "-modulate", "100,15,100", "PNG32:-"
                    ], stdout=subprocess.PIPE, check=True, cwd=cwd).stdout
                    bg_image_overlay = subprocess.run([
                        "magick", "-size", f"{w}x{h}", f"canvas:{rgba}", "PNG32:-"
                    ], stdout=subprocess.PIPE, check=True, cwd=cwd).stdout

                else:
                    bg_image = subprocess.run([
                        "magick", "-size", f"{w}x{h}", f"canvas:{rgba}", "PNG32:-"
                    ], stdout=subprocess.PIPE, check=True, cwd=cwd).stdout

                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as bg_tmp_file, \
                        tempfile.NamedTemporaryFile(suffix=".png", delete=False) as fg_tmp_file, \
                        tempfile.NamedTemporaryFile(suffix=".png", delete=False) as over_tmp_file:

                    bg_path = Path(bg_tmp_file.name)
                    fg_path = Path(fg_tmp_file.name)
                    overlay_path = Path(over_tmp_file.name)

                    if not frag_path:
                        bg_path.write_bytes(bg_image)
                        if raster_plasma:
                            overlay_path.write_bytes(bg_image_overlay)
                        fg_path.write_bytes(page_path.read_bytes())
                    else:
                        fg_path.write_bytes(page_path.read_bytes())
                        generate_frag(frag_path, bg_path, w, h)
                        if raster_plasma:
                            overlay_path.write_bytes(bg_image)

                if raster_plasma:
                    composite_output = bg_path.parent / "overlayed_bg.png"
                    composite_cmd = [
                        "magick",
                        str(bg_path),
                        "(",
                        str(overlay_path),
                        "-alpha", "Set",
                        "-channel", "A",
                        "-evaluate", "Multiply", "0.75",
                        "+channel",
                        ")",
                        "-compose", "Screen",
                        "-composite",
                        str(composite_output)
                    ]
                    proc = subprocess.run(composite_cmd, check=True, cwd=cwd,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if not composite_output.exists():
                        raise FileNotFoundError(f"Magick composite failed: {proc.stderr.decode()}")
                    bg_path = composite_output

                out_page = output_folder / f"{page_path.stem}.{image_format}"
                final_composite = [
                    "magick", "composite",
                    str(fg_path),
                    str(bg_path),
                    str(out_page)
                ]
                subprocess.run(final_composite, check=True, cwd=cwd)

                # Clean up
                if bg_path.exists() and "overlayed_bg" not in bg_path.name:
                    os.unlink(bg_path)
                os.unlink(fg_path)
                os.unlink(overlay_path)


            shutil.rmtree(raster_dir)

        else:
            raise ValueError(f"Unsupported format: {format}")

    # If exactly one output file is produced, return it
    output_files = list(output_folder.rglob(f'*'))
    if len(output_files) == 1:
        return output_files[0]

    # Otherwise, ZIP the whole folder
    archive_path = shutil.make_archive(
        base_name=zip_folder / file_path.stem,
        root_dir=output_folder,
        format='zip'
    )
    return Path(archive_path)
