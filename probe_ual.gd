extends SceneTree

func _init() -> void:
	var p := OS.get_cmdline_user_args()[0]
	var scene: PackedScene = load(p)
	if scene == null:
		print("FAIL load: ", p)
		quit(1)
		return
	var root: Node3D = scene.instantiate()
	var ap := _find_anim_player(root)
	if ap == null:
		print(p, ": no AnimationPlayer")
		quit(1)
		return
	var anims: PackedStringArray = ap.get_animation_list()
	var names: String = ""
	for a in anims:
		names += a + " | "
	print(p, " count=", anims.size())
	print("  ", names)
	var sk := _find_skel(root)
	if sk != null:
		print("  skeleton bones=", sk.get_bone_count())
	quit(0)

func _find_anim_player(n: Node) -> AnimationPlayer:
	if n is AnimationPlayer:
		return n
	for c in n.get_children():
		var r := _find_anim_player(c)
		if r != null:
			return r
	return null

func _find_skel(n: Node) -> Skeleton3D:
	if n is Skeleton3D:
		return n
	for c in n.get_children():
		var r := _find_skel(c)
		if r != null:
			return r
	return null
