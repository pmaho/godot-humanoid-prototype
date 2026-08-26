extends SceneTree

func _init() -> void:
	var p := OS.get_cmdline_user_args()[0]
	var scene: PackedScene = load(p)
	if scene == null:
		print("FAIL load: ", p)
		quit(1)
		return
	var root: Node3D = scene.instantiate()
	var sk := _find_skel(root)
	if sk == null:
		print(p, ": no Skeleton3D")
		quit(1)
		return
	var names: String = ""
	for i in sk.get_bone_count():
		names += sk.get_bone_name(i) + " | "
	print(p, " bones=", sk.get_bone_count())
	print("  ", names)
	# also print the skeleton's node path and any anim player track sample
	var ap := _find_anim_player(root)
	if ap != null:
		var anims: PackedStringArray = ap.get_animation_list()
		if anims.size() > 0:
			var a: Animation = ap.get_animation(anims[0])
			for t in a.get_track_count():
				print("  track0: ", a.get_track_path(t))
				break
	quit(0)

func _find_skel(n: Node) -> Skeleton3D:
	if n is Skeleton3D:
		return n
	for c in n.get_children():
		var r := _find_skel(c)
		if r != null:
			return r
	return null

func _find_anim_player(n: Node) -> AnimationPlayer:
	if n is AnimationPlayer:
		return n
	for c in n.get_children():
		var r := _find_anim_player(c)
		if r != null:
			return r
	return null
