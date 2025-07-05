from pathlib import Path
import moderngl
from PIL import Image
import numpy as np

def generate_frag(frag_path: str | Path, output_path: str | Path, width: int, height: int):
    # Create headless context (no display needed)
    ctx = moderngl.create_standalone_context()

    # Vertex shader (passes through positions)
    vertex_shader = '''
    #version 330
    in vec2 in_vert;
    out vec2 uv;
    void main() {
        uv = in_vert * 0.5 + 0.5;
        gl_Position = vec4(in_vert, 0.0, 1.0);
    }
    '''

    # Fragment shader
    with open(frag_path, 'r') as f:
        fragment_shader = f.read()

    # Compile shaders
    prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

    # Create quad
    vertices = np.array([
        -1.0, -1.0,
        1.0, -1.0,
        -1.0,  1.0,
        1.0,  1.0,
    ], dtype='f4')

    vbo = ctx.buffer(vertices)
    vao = ctx.simple_vertex_array(prog, vbo, 'in_vert')

    # Render to framebuffer
    fbo = ctx.simple_framebuffer((width, height))
    fbo.use()
    vao.render(moderngl.TRIANGLE_STRIP)

    # Read pixels
    data = fbo.read(components=3)
    img = Image.frombytes('RGB', (width, height), data)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(str(output_path))
    print("Saved to shader_output.png")


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