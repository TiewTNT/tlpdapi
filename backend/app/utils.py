from pathlib import Path
import moderngl
import numpy as np
from PIL import Image

def generate_frag(frag_path, out_path, width, height):
    ctx = moderngl.create_standalone_context()
    prog = ctx.program(
        vertex_shader='''
            #version 330
            in vec2 in_vert;
            out vec2 uv;
            void main() {
                uv = in_vert * 0.5 + 0.5;
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
        ''',
        fragment_shader=open(frag_path).read()
    )

    prog['iResolution'].value = (width, height)

    quad = np.array([
        -1.0, -1.0,
         1.0, -1.0,
        -1.0,  1.0,
        -1.0,  1.0,
         1.0, -1.0,
         1.0,  1.0,
    ], dtype='f4')

    vbo = ctx.buffer(quad.tobytes())
    vao = ctx.simple_vertex_array(prog, vbo, 'in_vert')

    fbo = ctx.simple_framebuffer((width, height))
    fbo.use()
    fbo.clear(0.0, 0.0, 0.0, 1.0)
    vao.render()

    img = Image.frombytes('RGBA', fbo.size, fbo.read(components=3))
    img.save(out_path)


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
    elif number > max_val:
        clamped = max_val
    else:
        clamped = number
    if int(clamped) == clamped:
        return int(clamped)
    else:
        return clamped
    
if __name__ == "__main__":
    print(clamp(120, 0, 360))