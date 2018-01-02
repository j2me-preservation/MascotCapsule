# helper for offline rendering using blender

import bpy
import sys
 
argv = sys.argv
argv = argv[argv.index("--") + 1:] # get all args after "--"

OBJFILE = argv[0]
SCALE = float(argv[1])

bpy.ops.object.delete()
bpy.ops.import_scene.obj(filepath=OBJFILE)
#bpy.ops.transform.resize(value=(SCALE, SCALE, SCALE))
bpy.ops.transform.resize(value=(0.01, 0.01, 0.01))
bpy.ops.view3d.camera_to_view_selected()
