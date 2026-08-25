import sys
sys.path.insert(0, '/home/petteri/blender_py/numpy314')
import bpy, math, os
from mathutils import Vector

OUT = '/home/petteri/godot_humanoid_prototype'
GLB = os.path.join(OUT, 'humanoid.glb')
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

# Materials
def mat(name, color, metallic=0.0, rough=0.7):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Metallic'].default_value=metallic; bs.inputs['Roughness'].default_value=rough
    return m
skin=mat('Skin',(0.55,0.22,0.12)); shirt=mat('Shirt',(0.08,0.28,0.65)); pants=mat('Pants',(0.06,0.08,0.12)); shoes=mat('Shoes',(0.025,0.025,0.03)); hair=mat('Hair',(0.03,0.012,0.006)); white=mat('Eyes',(0.9,0.9,0.85))

parts=[]
def cube(name, loc, scale, material, bevel=0.08):
    bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod=o.modifiers.new('Soft edges','BEVEL'); mod.width=bevel; mod.segments=2; bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
    o.data.materials.append(material); parts.append(o); return o
def uv(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, location=loc); o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); o.data.materials.append(material); parts.append(o); return o

def cyl(name, loc, radius, depth, material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=depth, location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(material); parts.append(o); return o

# Coordinates: Z up, character about 2m tall, arms in A-ish pose
parts += []
head=uv('Head',(0,0,1.78),(0.22,0.20,0.24),skin)
uv('HairCap',(0,-0.015,1.94),(0.225,0.205,0.12),hair)
cyl('Neck',(0,0,1.62),0.105,0.18,skin)
torso=cube('Torso',(0,0,1.30),(0.27,0.16,0.34),shirt,0.10)
# pelvis and limbs
pelvis=cube('Pelvis',(0,0,0.92),(0.25,0.15,0.16),pants,0.07)
for side,x in [('L',-0.14),('R',0.14)]:
    thigh=cyl('Thigh_'+side,(x,0,0.60),0.115,0.48,pants)
    shin=cyl('Shin_'+side,(x,0,0.20),0.095,0.38,pants)
    foot=cube('Foot_'+side,(x,-0.075,-0.045),(0.12,0.22,0.09),shoes,0.05)
    sign=-1 if side=='L' else 1
    # Longer, readable arms: a spherical shoulder joint bridges the torso and upper arm.
    shoulder_x=0.31*sign
    upper_x=0.52*sign
    elbow_x=0.82*sign
    wrist_x=1.02*sign
    uv('ShoulderJoint_'+side,(shoulder_x,0,1.43),(0.125,0.145,0.145),shirt)
    upper=cyl('UpperArm_'+side,(upper_x,0,1.43),0.095,0.43,shirt); upper.rotation_euler[1]=math.radians(90)
    # Keep the skin-colored forearm level with the blue upper arm.
    arm_z=1.43
    uv('ElbowJoint_'+side,(elbow_x,0,arm_z),(0.095,0.10,0.10),skin)
    # Extend the forearm into the wrist/palm with no gap.
    palm_x=1.10*sign
    fore=cyl('Forearm_'+side,((elbow_x+palm_x)/2,0,arm_z),0.082,0.52,skin); fore.rotation_euler[1]=math.radians(90)
    wrist=uv('Wrist_'+side,(1.05*sign,0,arm_z),(0.085,0.08,0.08),skin)
    palm=uv('Palm_'+side,(palm_x,0,arm_z),(0.14,0.105,0.14),skin)
    # Keep a single simple thumb; no separate fingers.
    uv('Thumb_'+side,(1.10*sign,-0.10,1.47),(0.04,0.075,0.07),skin)
# eyes for readability
uv('Eye_L',(-0.075,-0.185,1.82),(0.035,0.018,0.04),white); uv('Eye_R',(0.075,-0.185,1.82),(0.035,0.018,0.04),white)

# Armature
bpy.ops.object.armature_add( location=(0,0,0)); arm=bpy.context.object; arm.name='HumanoidSkeleton'; arm.data.name='HumanoidSkeleton'
bpy.ops.object.mode_set(mode='EDIT'); eb=arm.data.edit_bones; root=eb[0]; root.name='root'; root.head=(0,0,0); root.tail=(0,0,0.25)
def bone(name, parent, head, tail):
    b=eb.new(name); b.head=head; b.tail=tail; b.parent=eb.get(parent); return b
bone('spine','root',(0,0,0.25),(0,0,1.35)); bone('chest','spine',(0,0,1.15),(0,0,1.55)); bone('neck','chest',(0,0,1.55),(0,0,1.68)); bone('head','neck',(0,0,1.68),(0,0,1.95))
for s,x in [('L',-1),('R',1)]:
    bone('upper_arm.'+s,'chest',(0.28*x,0,1.46),(0.66*x,0,1.40)); bone('forearm.'+s,'upper_arm.'+s,(0.66*x,0,1.40),(1.02*x,0,1.34)); bone('hand.'+s,'forearm.'+s,(1.02*x,0,1.34),(1.18*x,0,1.34))
    bone('thigh.'+s,'root',(0.14*x,0,0.92),(0.14*x,0,0.55)); bone('shin.'+s,'thigh.'+s,(0.14*x,0,0.55),(0.14*x,0,0.15)); bone('foot.'+s,'shin.'+s,(0.14*x,0,0.15),(0.14*x,-0.18,0.02))
bpy.ops.object.mode_set(mode='OBJECT')

# Rigid skin: each part follows nearest semantic bone; this produces a usable prototype rig.
def bone_for(name):
    n=name.lower()
    if 'head' in n or 'hair' in n or 'eye' in n: return 'head'
    if 'neck' in n: return 'neck'
    if 'torso' in n: return 'chest'
    if 'pelvis' in n: return 'root'
    for s in ['L','R']:
        if '_'+s.lower() in n:
            if 'shoulderjoint' in n or 'upperarm' in n: return 'upper_arm.'+s
            if 'elbowjoint' in n or 'forearm' in n: return 'forearm.'+s
            if 'wrist' in n or 'palm' in n or 'finger' in n or 'thumb' in n: return 'hand.'+s
            if 'thigh' in n: return 'thigh.'+s
            if 'shin' in n: return 'shin.'+s
            if 'foot' in n: return 'foot.'+s
    return 'root'
for o in parts:
    vg=o.vertex_groups.new(name=bone_for(o.name)); vg.add(list(range(len(o.data.vertices))),1.0,'REPLACE')
    mod=o.modifiers.new('Armature','ARMATURE'); mod.object=arm

# Animations: keyframe pose bones; rigid parts visibly move with bones.
def clear_action():
    arm.animation_data_clear()
def set_pose(action_name, frames):
    clear_action(); arm.animation_data_create(); act=bpy.data.actions.new(action_name); arm.animation_data.action=act
    for frame, vals in frames.items():
        bpy.context.scene.frame_set(frame)
        for bn, rot in vals.items():
            pb=arm.pose.bones[bn]; pb.rotation_mode='XYZ'; pb.rotation_euler=rot; pb.keyframe_insert('rotation_euler',frame=frame)
    act.use_frame_range=True; act.frame_start=min(frames); act.frame_end=max(frames); return act
zero=(0,0,0); idle={1:{'root':zero},30:{'root':zero},60:{'root':zero}}
set_pose('idle',idle)
walk={1:{'upper_arm.L':(0,0,math.radians(-18)),'upper_arm.R':(0,0,math.radians(18)),'thigh.L':(math.radians(18),0,0),'thigh.R':(math.radians(-18),0,0)},15:{'upper_arm.L':(0,0,math.radians(18)),'upper_arm.R':(0,0,math.radians(-18)),'thigh.L':(math.radians(-18),0,0),'thigh.R':(math.radians(18),0,0)},30:{'upper_arm.L':(0,0,math.radians(-18)),'upper_arm.R':(0,0,math.radians(18)),'thigh.L':(math.radians(18),0,0),'thigh.R':(math.radians(-18),0,0)}}
set_pose('walk',walk)
arm.animation_data.action=bpy.data.actions['idle']
# Keep both actions as fake users so they survive saving/export workflows.
for _act in bpy.data.actions:
    _act.use_fake_user = True

# save editable source and export
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'humanoid.blend'))
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active=arm
for o in parts: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=GLB, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS', export_skins=True, export_apply=False)
print('SAVED',GLB)
print('SAVED',os.path.join(OUT, 'humanoid.blend'))
# validation info
print('ACTIONS', [a.name for a in bpy.data.actions])
print('PARTS',len(parts),'BONES',len(arm.data.bones))
