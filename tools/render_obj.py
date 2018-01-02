# hepler to render OBJ file into PNG

import subprocess
import time

BLENDER_EXE = 'C:/usr/blender-2.79-windows64/blender.exe'

def render_obj(blender, objfile, pngfile, scale):
    subprocess.check_call([
            blender,
            '--background',
            '--python', 'blender_importscript.py',
            '--render-output', '//' + pngfile,
            '--render-format', 'PNG',
            '--use-extension', '1',
            '-f', '0',
            '--', objfile, str(scale)
            ])

    time.sleep(1)

if __name__ == "__main__":
    render_obj(BLENDER_EXE, 'vertexdump.obj', 'vertexdump.png', 0.002)
