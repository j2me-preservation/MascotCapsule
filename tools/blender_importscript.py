# helper for offline rendering using blender

import bpy
import sys
 
argv = sys.argv
argv = argv[argv.index("--") + 1:] # get all args after "--"

OBJFILE = argv[0]
TEXTURE = argv[1]
RESOLUTION_X = int(argv[2])
RESOLUTION_Y = int(argv[3])
AXIS_FORWARD, AXIS_UP = argv[4:6]

bpy.ops.object.delete()
bpy.ops.import_scene.obj(filepath=OBJFILE, axis_forward=AXIS_FORWARD, axis_up=AXIS_UP)

if TEXTURE:
    mat = bpy.data.materials["Default OBJ"]
    bsdf = mat.node_tree.nodes["Principled BSDF"]

    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = bpy.data.images.load(TEXTURE)
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

# scale object down to be lit fully
obj, = bpy.context.selected_objects

dim = max(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z)
SCALE = 5 / dim
bpy.ops.transform.resize(value=(SCALE, SCALE, SCALE))
bpy.ops.view3d.camera_to_view_selected()

bpy.context.scene.cycles.samples = 16 # reduce rendering time
bpy.context.scene.render.film_transparent = True
bpy.context.scene.render.resolution_x = RESOLUTION_X
bpy.context.scene.render.resolution_y = RESOLUTION_Y
