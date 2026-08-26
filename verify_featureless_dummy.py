import sys, math
sys.path.insert(0, '/home/petteri/blender_py/numpy314')
import bpy
from mathutils import Vector
import os

MODEL_NAME=os.environ.get('MODEL_NAME','featureless_dummy')
BASE='/home/petteri/godot_humanoid_prototype/'+MODEL_NAME
bpy.ops.wm.open_mainfile(filepath=BASE+'.blend')
arm=bpy.data.objects.get('HumanoidSkeleton')
assert arm and arm.type == 'ARMATURE'
assert len(arm.data.bones) == 17, len(arm.data.bones)
actions={a.name: a for a in bpy.data.actions}
assert {'idle','walk'} <= set(actions), actions.keys()
walk=actions['walk']
assert walk.frame_start==1 and walk.frame_end==60, (walk.frame_start, walk.frame_end)
idle=actions['idle']
assert idle.frame_end==120
# every frame keyed on thigh.L rotation
# Blender 4.4+/5.x slotted action API
def action_fcurves(act):
    fcs=[]
    for layer in act.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                fcs.extend(bag.fcurves)
    return fcs
thc=[fc for fc in action_fcurves(walk) if 'thigh.L' in fc.data_path and 'rotation_euler' in fc.data_path]
assert thc, 'no thigh.L fcurves in walk'
keys=thc[0].keyframe_points
assert len(keys)>=60, len(keys)
# seamless loop: frame 61 value == frame 1 value
v1=keys[0].co[1]; v61=keys[-1].co[1]
assert abs(v1-v61)<1e-4, (v1, v61)
print('BLEND_VERIFY_PASS bones=%d actions=%s walk_keys=%d' % (len(arm.data.bones), sorted(actions), len(keys)))
# Verify exported GLB can be imported in a clean file.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=BASE+'.glb')
arm2=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
assert arm2, 'no armature imported'
assert len(arm2[0].data.bones) == 17
anims=[]
def _walk(node):
    if isinstance(node, bpy.types.Action):
        anims.append(node.name)
    for child in node.children:
        _walk(child)
# glTF imports animations as actions in bpy.data
names=[a.name for a in bpy.data.actions]
print('GLB_ACTIONS', sorted(names))
assert any('idle' in n.lower() for n in names)
assert any('walk' in n.lower() for n in names)
print('GLB_IMPORT_PASS bones=%d actions=%s' % (len(arm2[0].data.bones), sorted(names)))
