from pathlib import Path

def safe(path: Path, base: Path):
    try:
        path.resolve().relative_to(base.resolve())
    except ValueError:
        print('PATH', path, 'IS NOT SAFE RELATIVE TO', base)
        return False
    return True

def clamp(number: float | int, min_val: float | int, max_val: float | int) -> int | float:
    clamped = 0
    if number < min_val:
        clamped = min_val
    if number > max_val:
        clamped = max_val
    if int(clamped) == clamped:
        return int(clamped)
    else:
        return clamped