import subprocess
import shutil
from pathlib import Path
import os
import tempfile
from PIL import Image
import io


# def remove_patterns_from_file(file_path: Path, patterns: regex.Pattern):
#     """Remove lines matching the given regex patterns from a file."""
#     with file_path.open('r', encoding='utf-8') as file:
#         html = file.read()

#     with file_path.open('w', encoding='utf-8') as file:
#         file.write(
#             regex.sub(patterns, '', html)
#         )


def convert(file_paths, output_folder, zip_folder, format='pdf', image_format='png', dpi=200, bg_color={"r": 255, "g": 255, "b": 255, "a": 1}):
    os.makedirs(output_folder, exist_ok=True)
    for file_path in file_paths:
        if format == 'pdf':
            shutil.copy(file_path, output_folder / file_path.name)
        elif format in ['md', 'txt', 'html']:
            subprocess.run(['pdftohtml', '-c', '-s', '-noframes', str(file_path),
                            Path(str(output_folder / file_path.stem) + '.html')], check=True)
            if format in ['md', 'txt']:
                subprocess.run(['pdftohtml', '-c', '-s', '-noframes', str(file_path),
                                Path(str(output_folder / file_path.stem) + '.html')], check=True)
                # remove_patterns_from_file(Path(str(output_folder / file_path.stem) + '.html'),
                #                         regex.compile(rf'<img\s+width="\d+"\s+height="\d+"\s+src="{regex.escape(file_path.stem)}\d+\.png"\s+alt="background image"\s*/?>', regex.DOTALL))

                # subprocess.run(['pandoc', Path(str(output_folder / file_path.stem) + '.html'), '-t', 'markdown_strict',
                #             '-o', Path(str(output_folder / file_path.stem) + '.md')], check=True)

                # os.remove(Path(str(output_folder / file_path.stem) + '001.png'))
                os.remove(Path(str(output_folder / file_path.stem) + '.html'))
                if format == 'txt':
                    subprocess.run(['pandoc', Path(str(output_folder / file_path.stem) + '.md'), '-t', 'plain',
                                    '-o', Path(str(output_folder / file_path.stem) + '.txt')], check=True)
                    os.remove(Path(str(output_folder / file_path.stem) + '.md'))
        elif format == 'raster':
            # Step 1: Create output pattern
            raster_dir = output_folder / f"{file_path.stem}_raster"
            os.makedirs(raster_dir, exist_ok=True)

            # Step 2: Convert each PDF page to PNG
            subprocess.run([
                "magick",
                "-density", str(dpi),
                str(file_path),
                str(raster_dir / f"{file_path.stem}_%03d.png")
            ], check=True)

            # Step 3: Composite each over background
            for page_path in sorted(Path(raster_dir).glob("*.png")):
                with Image.open(page_path) as img:
                    w, h = img.width, img.height

                rgba = f"rgba({bg_color['r']},{bg_color['g']},{bg_color['b']},{bg_color['a']})"

                # Create background
                bg_image = subprocess.run([
                    "magick", "-size", f"{w}x{h}", f"canvas:{rgba}", "PNG32:-"
                ], stdout=subprocess.PIPE, check=True).stdout

                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as bg_tmp, \
                    tempfile.NamedTemporaryFile(suffix=".png", delete=False) as fg_tmp:

                    bg_tmp.write(bg_image)
                    fg_tmp.write(page_path.read_bytes())
                    bg_tmp.flush()
                    fg_tmp.flush()

                out_page = output_folder / f"{page_path.stem}.{image_format}"
                subprocess.run([
                    "magick", "composite",
                    fg_tmp.name, bg_tmp.name,
                    str(out_page)
                ], check=True)

                os.unlink(bg_tmp.name)
                os.unlink(fg_tmp.name)

            shutil.rmtree(raster_dir)

                

        else:
            raise ValueError(f"Unsupported format: {format}")

    actual_format = format if format != 'raster' else image_format
    if len(list(output_folder.rglob('*'))) == 1:
        return output_folder / Path(file_path.stem + '.' + actual_format)

    
    shutil.make_archive(base_name=zip_folder / file_path.stem,
                        root_dir=output_folder, format='zip')
    
    
    return Path(str(zip_folder / file_path.stem) + '.zip')
