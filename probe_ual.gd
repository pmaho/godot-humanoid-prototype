extends SceneTree

func _init():
	var scene: PackedScene = load("res://assets/ual_mixamo.glb")
	if scene == null:
		print("FAIL: cannot load glb")
		quit(1); return
	var inst = scene.instantiate()
	root.add_child(inst)
	var anim: AnimationPlayer = null
	var skin: Node3D = null
	for n in inst.find_children("*", "AnimationPlayer"):
		anim = n
	for n in inst.find_children("*", "SkinnedMeshInstance3D"):
		skin = n
	if anim == null:
		print("FAIL: no AnimationPlayer"); quit(1); return
	var anims = anim.get_animation_list()
	print("ANIMS: ", anims.size())
	var origin = skin.global_position if skin else Vector3.ZERO
	for a in anims:
		anim.play(a)
		var len = anim.current_animation_length
		anim.seek(maxf(len - 0.02, 0.0), true)
		var p = skin.global_position if skin else Vector3.ZERO
		var drift = p.distance_to(origin) if skin else 0.0
		print("  %s: len=%.2f end_pos=(%.2f,%.2f,%.2f) drift=%.3f" % [a, len, p.x, p.y, p.z, drift])
	print("PROBE OK")
	quit(0)
