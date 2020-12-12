# helper to render OBJ files (together with blender_importscript.py)

from pathlib import Path
import os
import subprocess
import time

def render_obj(objfile, pngfile, texture="", resolution=(1290, 1080), format="PNG", axis_forward='-Z', axis_up='Y',
                texture_interpolation="Linear"):
    script_path = str(os.path.join(Path(__file__).resolve().parent, "blender_importscript.py"))
    subprocess.check_call([
            "blender",
            '--background',
            "--engine", "CYCLES",       # only Cycles rendering works without OpenGL
            "-noaudio",                 # reduce stderr clutter (we don't need no sound)
            '--python', script_path,
            '--render-output', '//' + pngfile,
            '--render-format', format,
            '--use-extension', '1',
            '-f', '0',
            '--', objfile, texture if texture else "", str(resolution[0]), str(resolution[1]),
            axis_forward,
            axis_up,
            texture_interpolation,      # https://docs.blender.org/api/current/bpy.types.ShaderNodeTexImage.html#bpy.types.ShaderNodeTexImage.interpolation
            ], stdout=subprocess.DEVNULL)

    # TODO: is this really needed, and why?
    time.sleep(1)
