import sys
sys.path.insert(0, '/home/petteri/blender_py/numpy314')
import bpy, math, os
from mathutils import Vector

OUT = '/home/petteri/godot_humanoid_prototype'
MODEL_NAME = os.environ.get('MODEL_NAME', 'featureless_dummy')
MODEL_COLOR = tuple(float(v) for v in os.environ.get('MODEL_COLOR', '0.46,0.49,0.53').split(','))
GLB = os.path.join(OUT, MODEL_NAME + '.glb')
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

# Materials
def mat(name, color, metallic=0.0, rough=0.7):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Metallic'].default_value=metallic; bs.inputs['Roughness'].default_value=rough
    return m
# Featureless mannequin: one neutral material, with no face, hair, clothing, or details.
dummy=mat('DummyBody',MODEL_COLOR, metallic=0.0, rough=0.82)
skin=shirt=pants=shoes=hair=white=dummy

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
cyl('Neck',(0,0,1.62),0.105,0.18,skin)
torso=cube('Torso',(0,0,1.30),(0.27,0.16,0.34),shirt,0.10)
# pelvis and limbs
pelvis=cube('Pelvis',(0,0,0.92),(0.25,0.15,0.16),pants,0.07)
for side,x in [('L',-0.14),('R',0.14)]:
    thigh=cyl('Thigh_'+side,(x,0,0.60),0.115,0.48,pants)
    shin=cyl('Shin_'+side,(x,0,0.20),0.095,0.38,pants)
    foot=cube('Foot_'+side,(x,-0.075,0.0),(0.12,0.22,0.10),shoes,0.04)
    sign=-1 if side=='L' else 1
    # Arms hang down in a slight A-pose (15 deg from vertical) — T-pose rest made
    # the X-swing keys spin the arms in place instead of swinging them front-back.
    a=math.radians(15)
    dx, dz = sign*math.sin(a), -math.cos(a)
    sh=(0.31*sign,0,1.43)
    elbow=(sh[0]+dx*0.43, 0, sh[2]+dz*0.43)
    wrist=(elbow[0]+dx*0.52, 0, elbow[2]+dz*0.52)
    rot_y=math.radians(195 if side=='L' else 165)
    # Spherical shoulder joint bridges the torso and upper arm.
    uv('ShoulderJoint_'+side,sh,(0.125,0.145,0.145),shirt)
    upper=cyl('UpperArm_'+side,(sh[0]+dx*0.215,0,sh[2]+dz*0.215),0.095,0.43,shirt); upper.rotation_euler[1]=rot_y
    uv('ElbowJoint_'+side,elbow,(0.095,0.10,0.10),skin)
    fore=cyl('Forearm_'+side,(elbow[0]+dx*0.26,0,elbow[2]+dz*0.26),0.082,0.52,skin); fore.rotation_euler[1]=rot_y
    uv('Wrist_'+side,(wrist[0]+dx*0.02,0,wrist[2]+dz*0.02),(0.085,0.08,0.08),skin)
    palm=uv('Palm_'+side,(wrist[0]+dx*0.10,0,wrist[2]+dz*0.10),(0.14,0.105,0.14),skin)
# Armature
bpy.ops.object.armature_add( location=(0,0,0)); arm=bpy.context.object; arm.name='HumanoidSkeleton'; arm.data.name='HumanoidSkeleton'
bpy.ops.object.mode_set(mode='EDIT'); eb=arm.data.edit_bones; root=eb[0]; root.name='root'; root.head=(0,0,0); root.tail=(0,0,0.25)
def bone(name, parent, head, tail):
    b=eb.new(name); b.head=head; b.tail=tail; b.parent=eb.get(parent); return b
bone('spine','root',(0,0,0.25),(0,0,1.35)); bone('chest','spine',(0,0,1.15),(0,0,1.55)); bone('neck','chest',(0,0,1.55),(0,0,1.68)); bone('head','neck',(0,0,1.68),(0,0,1.95))
for s,x in [('L',-1),('R',1)]:
    # Hanging arms (15 deg A-pose): bone local Y points DOWN, so X-rotation =
    # front-back swing, same convention as the thigh bones.
    bone('upper_arm.'+s,'chest',(0.31*x,0,1.43),(0.31*x+0.1113*x,0,1.0147)); bone('forearm.'+s,'upper_arm.'+s,(0.31*x+0.1113*x,0,1.0147),(0.31*x+0.2459*x,0,0.5124)); bone('hand.'+s,'forearm.'+s,(0.31*x+0.2459*x,0,0.5124),(0.31*x+0.2718*x,0,0.4158))
    bone('thigh.'+s,'root',(0.14*x,0,0.92),(0.14*x,0,0.55)); bone('shin.'+s,'thigh.'+s,(0.14*x,0,0.55),(0.14*x,0,0.15)); bone('foot.'+s,'shin.'+s,(0.14*x,0,0.15),(0.14*x,-0.18,0.02))
# Auto-roll gives L and R arm bones DIFFERENT local-X directions, so identical
# swing keys move each arm differently. Force local X = world X (lateral) on all
# arm bones: then +X = arm swings backward, -X = forward, on BOTH sides.
for _nm in ('upper_arm.L','forearm.L','hand.L','upper_arm.R','forearm.R','hand.R'):
    _b = eb[_nm]
    _Y = (_b.tail - _b.head).normalized()
    def _proj(_v): return _v - _Y * _v.dot(_Y)
    _M = _b.matrix.to_3x3()
    _xa = _proj(Vector((_M[0][0], _M[1][0], _M[2][0]))).normalized()  # current local X in bone space
    _xt = _proj(Vector((1,0,0))).normalized()
    _b.roll += math.atan2((_xa.cross(_xt)).dot(_Y), _xa.dot(_xt))
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

# ---- Animations: procedurally keyed full gait cycle (30 fps, seamless loops) ----
bpy.context.scene.render.fps = 30
TWO_PI = 2*math.pi

def _gauss(x, c, w):
    d = (x - c + math.pi) % TWO_PI - math.pi  # cyclic angular distance
    return math.exp(-(d*d)/(2*w*w))

def _zero_pose():
    bones = [b.name for b in arm.pose.bones]
    return ({b: (0,0,0) for b in bones}, {b: (0,0,0) for b in bones})

def walk_pose(f):
    n = 60  # 2 s per stride cycle at 30 fps
    p = ((f - 1) % n) / n * TWO_PI
    rots, locs = _zero_pose()
    # Phase convention (LEFT leg): heel strike at p=pi/2 (forward extreme),
    # mid-stance at p=pi (under body), toe-off at p=3pi/2 (back extreme),
    # mid-swing at p=0 (under body). Right leg = everything +pi.
    # Verified bone signs (headless probe): shin +X = knee flexion,
    # foot +X = plantarflexion, thigh +X = leg forward, upper_arm +X = hand back.
    thigh_L = math.radians(22) * math.sin(p)
    # Knee: main flexion at mid-swing (L p=0, R p=pi); heel-strike absorption
    # bump (L pi/2, R 3pi/2); small flexion at push-off (L 3pi/2, R pi/2).
    knee_L = (math.radians(58) * _gauss(p, 0.0, 0.50)
              + math.radians(15) * _gauss(p, math.pi/2, 0.35)
              + math.radians(8)  * _gauss(p, 3*math.pi/2, 0.30))
    knee_R = (math.radians(58) * _gauss(p, math.pi, 0.50)
              + math.radians(15) * _gauss(p, 3*math.pi/2, 0.35)
              + math.radians(8)  * _gauss(p, math.pi/2, 0.30))
    # Foot: plantarflexion burst just before toe-off, dorsiflexion during swing
    # for ground clearance, slight dorsiflexion at heel strike.
    foot_L = (math.radians(28) * _gauss(p, 3*math.pi/2 - 0.30, 0.28)
              - math.radians(10) * _gauss(p, 0.0, 0.55)
              - math.radians(6)  * _gauss(p, math.pi/2, 0.30))
    foot_R = (math.radians(28) * _gauss(p, math.pi/2 - 0.30, 0.28)
              - math.radians(10) * _gauss(p, math.pi, 0.55)
              - math.radians(6)  * _gauss(p, 3*math.pi/2, 0.30))
    # Arms swing contralaterally in the sagittal plane: L arm forward
    # (negative X) when L leg is back, i.e. in phase with the R leg.
    ua_L = math.radians(26) * math.sin(p)
    ua_R = -math.radians(26) * math.sin(p)
    elb_L = math.radians(35) - math.radians(8) * math.cos(2*p)
    elb_R = math.radians(35) + math.radians(8) * math.cos(2*p)
    rots['thigh.L'] = (thigh_L, 0, 0); rots['thigh.R'] = (-thigh_L, 0, 0)
    rots['shin.L'] = (knee_L, 0, 0); rots['shin.R'] = (knee_R, 0, 0)
    rots['foot.L'] = (foot_L, 0, 0); rots['foot.R'] = (foot_R, 0, 0)
    rots['upper_arm.L'] = (ua_L, 0, 0); rots['upper_arm.R'] = (ua_R, 0, 0)
    rots['forearm.L'] = (elb_L, 0, 0); rots['forearm.R'] = (elb_R, 0, 0)
    # Trunk: constant forward lean, yaw sway toward the stance leg
    # (L mid-stance p=pi, R mid-stance p=0), head counter-rotation.
    rots['chest'] = (math.radians(4) + math.radians(1.0)*math.cos(2*p), math.radians(2)*math.cos(p), 0)
    rots['head'] = (-math.radians(1)*math.cos(2*p), -math.radians(2)*math.cos(p), 0)
    # Vertical bob: highest at mid-stance (p=0, pi), lowest at double support.
    locs['root'] = (0.005*math.sin(2*p), 0, 0.016*math.cos(2*p))
    return rots, locs

def idle_pose(f):
    n = 120  # 4 s breathing loop
    p = ((f - 1) % n) / n * TWO_PI
    rots, locs = _zero_pose()
    b = math.sin(p)
    rots['chest'] = (math.radians(1.8)*b, 0, 0)
    rots['head'] = (-math.radians(1.0)*b, 0, 0)
    rots['upper_arm.L'] = (math.radians(2)*math.sin(p + 0.7), 0, 0)
    rots['upper_arm.R'] = (math.radians(2)*math.sin(p + 0.7 + math.pi), 0, 0)
    rots['forearm.L'] = (math.radians(4)*b + math.radians(2), 0, 0)
    rots['forearm.R'] = (math.radians(4)*b + math.radians(2), 0, 0)
    locs['root'] = (0, 0, 0.006*b)
    return rots, locs

def set_dense(action_name, n_frames, eval_fn):
    """Key every pose bone on every frame; frame n+1 repeats frame 1 for a seamless loop."""
    arm.animation_data_clear()
    arm.animation_data_create()
    act = bpy.data.actions.new(action_name)
    arm.animation_data.action = act
    for f in range(1, n_frames + 2):
        rots, locs = eval_fn(f)
        for bn, rot in rots.items():
            pb = arm.pose.bones[bn]
            pb.rotation_mode = 'XYZ'
            pb.rotation_euler = rot
            pb.keyframe_insert('rotation_euler', frame=f)
        for bn, loc in locs.items():
            pb = arm.pose.bones[bn]
            pb.location = loc
            pb.keyframe_insert('location', frame=f)
    act.frame_start = 1
    act.frame_end = n_frames
    act.use_frame_range = True
    return act

set_dense('idle', 120, idle_pose)
set_dense('walk', 60, walk_pose)
arm.animation_data.action = bpy.data.actions['idle']
# Keep both actions as fake users so they survive saving/export workflows.
for _act in bpy.data.actions:
    _act.use_fake_user = True

# save editable source and export
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, MODEL_NAME + '.blend'))
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active=arm
for o in parts: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=GLB, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS', export_skins=True, export_apply=False)
print('SAVED',GLB)
print('SAVED',os.path.join(OUT, MODEL_NAME + '.blend'))
# validation info
print('ACTIONS', [a.name for a in bpy.data.actions])
print('PARTS',len(parts),'BONES',len(arm.data.bones))
