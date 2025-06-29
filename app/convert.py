import subprocess
import shutil
from pathlib import Path
import os
import regex


def remove_patterns_from_file(file_path: Path, patterns: regex.Pattern):
    """Remove lines matching the given regex patterns from a file."""
    with file_path.open('r', encoding='utf-8') as file:
        html = file.read()

    with file_path.open('w', encoding='utf-8') as file:
        file.write(
            regex.sub(patterns, '', html)
        )


def convert(file_path, output_folder, format='pdf', image_format='png', dpi=200):
    os.makedirs(output_folder, exist_ok=True)
    if format == 'pdf':
        shutil.copy(file_path, output_folder / file_path.name)
    elif format in ['md', 'txt', 'html']:
        subprocess.run(['pdftohtml', '-c', '-s', '-noframes', str(file_path),
                       Path(str(output_folder / file_path.stem) + '.html')], check=True)
        if format in ['md', 'txt']:
            subprocess.run(['pdftohtml', '-c', '-s', '-noframes', str(file_path),
                        Path(str(output_folder / file_path.stem) + '.html')], check=True)
            remove_patterns_from_file(Path(str(output_folder / file_path.stem) + '.html'),
                                    regex.compile(rf'<img\s+width="\d+"\s+height="\d+"\s+src="{regex.escape(file_path.stem)}001\.png"\s+alt="background image"\s*/?>', regex.DOTALL))
            
            subprocess.run(['pandoc', Path(str(output_folder / file_path.stem) + '.html'), '-t', 'markdown_strict',
                        '-o', Path(str(output_folder / file_path.stem) + '.md')], check=True)
            
            os.remove(Path(str(output_folder / file_path.stem) + '001.png'))
            os.remove(Path(str(output_folder / file_path.stem) + '.html'))
            if format == 'txt':
                subprocess.run(['pandoc', Path(str(output_folder / file_path.stem) + '.md'), '-t', 'plain',
                            '-o', Path(str(output_folder / file_path.stem) + '.txt')], check=True)
                os.remove(Path(str(output_folder / file_path.stem) + '.md'))
    elif format == 'raster':
        subprocess.run(['magick', '-density', str(dpi), file_path,
                       Path(str(output_folder / file_path.stem) + '.'+image_format)], check=True)
    else:
        raise ValueError(f"Unsupported format: {format}")

    if len(list(output_folder.iterdir())) == 1:
        return Path(str(output_folder / file_path.stem) + '.' + format)

    shutil.make_archive(str(output_folder / file_path.stem), 'zip', root_dir=output_folder)
    return output_folder / (file_path.stem + '.zip')
