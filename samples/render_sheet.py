# Renders every weapon and VFX FBX into one contact sheet for checking shapes:
#   blender -b -P tools/blender/render_sheet.py -- <output.png>
import math
import os
import sys

import bpy
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
out = sys.argv[sys.argv.index("--") + 1]

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

files = []
for category in ("weapons", "vfx"):
    folder = os.path.join(ROOT, "assets", "models", category)
    files += [os.path.join(folder, f) for f in sorted(os.listdir(folder)) if f.endswith(".fbx")]

COLUMNS = 7
SPACING = 8
for i, path in enumerate(files):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    corners = [o.matrix_world @ Vector(c) for o in new for c in o.bound_box]
    centre = sum(corners, Vector()) / len(corners)
    radius = max((c - centre).length for c in corners) or 1
    place = Vector(((i % COLUMNS) * SPACING, -(i // COLUMNS) * SPACING, 0))
    for o in new:
        o.matrix_world.translation += place - centre
        o.scale = o.scale * min(1, 3.2 / radius)

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_cavity = True
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.filepath = out
scene.world = bpy.data.worlds.new("w")
scene.world.color = (0.5, 0.5, 0.55)

rows = math.ceil(len(files) / COLUMNS)
cam = bpy.data.cameras.new("cam")
cam.type = "ORTHO"
cam.ortho_scale = max(COLUMNS, rows * 1.6) * SPACING
obj = bpy.data.objects.new("cam", cam)
bpy.context.collection.objects.link(obj)
middle = Vector(((COLUMNS - 1) * SPACING / 2, -(rows - 1) * SPACING / 2, 0))
obj.location = middle + Vector((30, -30, 30))
obj.rotation_euler = (middle - obj.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = obj
bpy.ops.render.render(write_still=True)
print("[sheet] " + str(len(files)) + " models -> " + out)
