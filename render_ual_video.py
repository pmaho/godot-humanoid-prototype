import sys, os
sys.path.insert(0, '/home/petteri/blender_py/numpy314')
import bpy
from mathutils import Vector

GLB = '/home/petteri/godot_humanoid_prototype/assets/ual/' + os.environ.get('UAL_MODEL', 'UAL1_Standard') + '.glb'
ACTION = os.environ.get('UAL_ACTION', 'Walk_Loop')
FRAME_DIR = '/tmp/ual_frames_' + os.environ.get('UAL_MODEL', 'UAL1_Standard')
OUT = '/home/petteri/godot_humanoid_prototype/ual_' + os.environ.get('UAL_MODEL', 'UAL1_Standard') + '_' + os.environ.get('UAL_ACTION', 'walk') + '.mp4'
os.makedirs(FRAME_DIR, exist_ok=True)

# clean scene
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)

# find the armature + pick action
arm = None
for ob in bpy.data.objects:
    if ob.type == 'ARMATURE':
        arm = ob
        break
print('ARMATURE', arm.name if arm else None)
act = bpy.data.actions.get(ACTION)
print('ACTION', act.name if act else None, 'available:', [a.name for a in bpy.data.actions])
if arm is not None and act is not None:
    arm.animation_data_create()
    arm.animation_data.action = act

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 720
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.fps = 30
scene.render.filepath = FRAME_DIR + '/f_'

scene.display.shading.light = 'STUDIO'
scene.display.shading.studio_light = 'paint.sl'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = 'WORLD'
scene.display.shading.curvature_ridge_factor = 1.5
scene.display.shading.curvature_valley_factor = 1.2
scene.display.shading.background_type = 'WORLD'
scene.display.shading.background_color = (0.035, 0.045, 0.07)

# camera
cam_data = bpy.data.cameras.new('WalkCam')
cam = bpy.data.objects.new('WalkCam', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = (2.4, -4.6, 1.4)
target = Vector((0, 0, 0.85))
cam.rotation_euler = (target - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 55
cam.data.clip_end = 100

scene.frame_start = 1
scene.frame_end = 60
scene.frame_set(1)
bpy.ops.render.render(animation=True)
print('RENDERED', OUT)
