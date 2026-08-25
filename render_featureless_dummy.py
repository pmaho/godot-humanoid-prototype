import sys, math
sys.path.insert(0, '/home/petteri/blender_py/numpy314')
import bpy
from mathutils import Vector

BLEND='/home/petteri/godot_humanoid_prototype/featureless_dummy.blend'
OUT='/home/petteri/godot_humanoid_prototype/featureless_dummy_preview.png'
bpy.ops.wm.open_mainfile(filepath=BLEND)
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=700
scene.render.resolution_y=700
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=OUT
scene.display.shading.light='STUDIO'
scene.display.shading.studio_light='paint.sl'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='WORLD'
scene.display.shading.curvature_ridge_factor=1.5
scene.display.shading.curvature_valley_factor=1.2
scene.display.shading.background_type='WORLD'
scene.display.shading.background_color=(0.035,0.045,0.07)
# camera
cam_data=bpy.data.cameras.new('PreviewCamera')
cam=bpy.data.objects.new('PreviewCamera',cam_data)
bpy.context.collection.objects.link(cam)
scene.camera=cam
cam.location=(3.1,-5.2,2.5)
target=Vector((0,0,0.95))
cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
cam.data.lens=58
cam.data.clip_end=100
# use neutral idle pose
arm=bpy.data.objects.get('HumanoidSkeleton')
if arm and arm.animation_data:
    arm.animation_data.action=bpy.data.actions.get('idle')
scene.frame_set(1)
bpy.ops.render.render(write_still=True)
print('RENDERED',OUT)
