import sys
sys.path.insert(0, '/home/petteri/blender_py/numpy314')
import numpy as np
import bpy
from mathutils import Vector
import os
MODEL_NAME=os.environ.get('MODEL_NAME','featureless_dummy')
BASE='/home/petteri/godot_humanoid_prototype/'+MODEL_NAME
bpy.ops.wm.open_mainfile(filepath=BASE+'.blend')
arm=bpy.data.objects.get('HumanoidSkeleton')
assert arm and arm.type == 'ARMATURE'
assert len(arm.data.bones) == 17, len(arm.data.bones)
assert {'idle','walk'} <= {a.name for a in bpy.data.actions}
for o in bpy.data.objects:
    if o.type == 'MESH':
        assert o.find_armature() == arm, o.name
        assert any(m.type == 'ARMATURE' for m in o.modifiers), o.name
print('BLEND_VERIFY_PASS bones=%d meshes=%d actions=%s' % (len(arm.data.bones), sum(o.type=='MESH' for o in bpy.data.objects), sorted(a.name for a in bpy.data.actions)))
# Verify exported GLB can be imported in a clean file.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=BASE+'.glb')
arm2=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
assert arm2, 'no armature imported'
assert len(arm2[0].data.bones) == 17
names = {a.name for a in bpy.data.actions}
print('GLB_IMPORTED_ACTIONS', sorted(names))
assert any('idle' in n.lower() for n in names)
assert any('walk' in n.lower() for n in names)
print('GLB_IMPORT_PASS bones=%d actions=%s' % (len(arm2[0].data.bones), sorted(names)))
