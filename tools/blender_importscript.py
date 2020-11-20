# helper for offline rendering using blender

import bpy
import bmesh
import sys
 
argv = sys.argv
argv = argv[argv.index("--") + 1:] # get all args after "--"

OBJFILE = argv[0]
TEXTURE = argv[1]
RESOLUTION_X = int(argv[2])
RESOLUTION_Y = int(argv[3])
AXIS_FORWARD, AXIS_UP = argv[4:6]
TEXTURE_INTERPOLATION = argv[6]

bpy.ops.object.delete()
bpy.ops.import_scene.obj(filepath=OBJFILE, axis_forward=AXIS_FORWARD, axis_up=AXIS_UP)

obj, = bpy.context.selected_objects

if TEXTURE:
    mat = bpy.data.materials["Default OBJ"]
    bsdf = mat.node_tree.nodes["Principled BSDF"]

    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = bpy.data.images.load(TEXTURE)
    texImage.interpolation = TEXTURE_INTERPOLATION
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
    bsdf.inputs['Specular'].default_value = 0

    # scale UVs from pixel coordinates to normalized coordinates
    # cheers to https://blender.stackexchange.com/a/111307
    def transform_uv(obj, scale, translate):
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode = 'EDIT')

        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        uv_layer = bm.loops.layers.uv.verify()

        # adjust uv coordinates
        for face in bm.faces:
            for loop in face.loops:
                loop_uv = loop[uv_layer]
                loop_uv.uv = loop_uv.uv[0] * scale[0] + translate[0], loop_uv.uv[1] * scale[1] + translate[1]

        bmesh.update_edit_mesh(me)
        bpy.ops.object.mode_set(mode = 'OBJECT')

    w, h = texImage.image.size

    if w > 0 and h > 0:
        transform_uv(obj, (1 / w, -1 / h), (0, 1))

# scale object down to be lit fully
dim = max(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z)
SCALE = 5 / dim
bpy.ops.transform.resize(value=(SCALE, SCALE, SCALE))
bpy.ops.view3d.camera_to_view_selected()

bpy.context.scene.cycles.samples = 16 # reduce rendering time
bpy.context.scene.render.film_transparent = True
bpy.context.scene.render.resolution_x = RESOLUTION_X
bpy.context.scene.render.resolution_y = RESOLUTION_Y
