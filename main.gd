extends Node3D

@onready var player: CharacterBody3D = $CharacterBody3D
@onready var model: Node3D = $CharacterBody3D/Model

const SPEED := 2.5
const UAL1 := "res://assets/ual/UAL1_Standard.glb"
const UAL2 := "res://assets/ual/UAL2_Standard.glb"

var player_anim: AnimationPlayer
var model_instances: Array[Node3D] = []
var player_instance: Node3D
var arp_instance: Node3D
var arp_anim: AnimationPlayer

# 8 Mixamo animations on the ARP dummy, selected with keys 1-8 (0 = idle)
const MIXAMO_ANIMS := [
	"mixamo_Walking",
	"mixamo_Running",
	"mixamo_Idle",
	"mixamo_Jump",
	"mixamo_Punching",
	"mixamo_Hip_Hop_Dancing",
	"mixamo_Start_Walking_Backwards",
	"mixamo_Walking_Left_Turn",
]

const DUMMY_ASSETS := [
	{"path": UAL2, "position": Vector3(-1.8, 0.0, 0.0), "anim": "Zombie_Walk_Fwd"},
	{"path": UAL2, "position": Vector3(-0.6, 0.0, 0.0), "anim": "TreeChopping"},
	{"path": UAL2, "position": Vector3(0.6, 0.0, 0.0), "anim": "Sword_Idle"},
	{"path": "res://featureless_dummy.glb", "position": Vector3(1.8, 0.0, 0.0), "anim": "walk"},
	{"path": "res://assets/arp_mixamo_dummy.glb", "position": Vector3(-3.2, 0.0, 0.0), "anim": "mixamo_Walking"},
]

func _ready() -> void:
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.28
	capsule.height = 1.8
	$CharacterBody3D/CollisionShape3D.shape = capsule
	$CharacterBody3D/CollisionShape3D.position.y = 0.9
	player_instance = _add_model(UAL1, Vector3.ZERO, "Idle")
	for item in DUMMY_ASSETS:
		var inst := _add_model(item.path, item.position, item.anim)
		if item.path == "res://assets/arp_mixamo_dummy.glb":
			arp_instance = inst
			arp_anim = _find_anim_player(inst)

func _add_model(path: String, pos: Vector3, anim_name: String) -> Node3D:
	var scene_asset: PackedScene = load(path)
	if scene_asset == null:
		push_error("Could not load %s" % path)
		return null
	var instance: Node3D = scene_asset.instantiate()
	instance.position = pos
	model.add_child(instance)
	model_instances.append(instance)
	var asset_anim := _find_anim_player(instance)
	if asset_anim != null:
		if asset_anim.has_animation(anim_name):
			asset_anim.play(anim_name)
		elif asset_anim.has_animation("Idle"):
			asset_anim.play("Idle")
	if instance == player_instance:
		player_anim = asset_anim
	return instance

func _find_anim_player(n: Node) -> AnimationPlayer:
	if n is AnimationPlayer:
		return n
	for c in n.get_children():
		var r := _find_anim_player(c)
		if r != null:
			return r
	return null

func _physics_process(_delta: float) -> void:
	var input_vec := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var direction := Vector3(input_vec.x, 0.0, input_vec.y)
	player.velocity.x = direction.x * SPEED
	player.velocity.z = direction.z * SPEED
	player.move_and_slide()
	if direction.length_squared() > 0.01:
		player.look_at(player.global_position + direction, Vector3.UP)
		_play_current("Walk", "walk")
		for instance in model_instances:
			instance.rotation.y = lerp_angle(instance.rotation.y, player.rotation.y, 0.15)
	else:
		_play_current("Idle", "idle")

func _play_current(ual_name: String, dummy_name: String) -> void:
	if player_anim != null and player_anim.current_animation != ual_name:
		if player_anim.has_animation(ual_name):
			player_anim.play(ual_name)
		# dummies keep their loops; the featureless dummy toggles walk/idle
		# (ARP dummy is excluded — its animation is user-selected via 1-8)
		for instance in model_instances:
			if instance == player_instance or instance == arp_instance:
				continue
			var a := _find_anim_player(instance)
			if a != null:
				var target := ual_name if a.has_animation(ual_name) else dummy_name
				if a.has_animation(target) and a.current_animation != target:
					a.play(target)

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_0:
			_play_arp(-1)  # idle
		elif event.keycode >= KEY_1 and event.keycode <= KEY_8:
			_play_arp(event.keycode - KEY_1)

func _play_arp(idx: int) -> void:
	if arp_anim == null:
		return
	var anim_name: String = "idle" if idx < 0 else MIXAMO_ANIMS[idx]
	if arp_anim.has_animation(anim_name):
		arp_anim.play(anim_name)
		print("ARP anim -> ", anim_name)

func _process(_delta: float) -> void:
	$Camera3D.look_at(player.global_position + Vector3(0, 0.9, 0), Vector3.UP)
	var state := "WALK" if player.velocity.length() > 0.1 else "IDLE"
	var arp_now := ""
	if arp_anim != null:
		arp_now = arp_anim.current_animation
	$UI/Label.text = "WASD to move — %s\nARP [1-8]: %s" % [state, arp_now]

func _enter_tree() -> void:
	var env := WorldEnvironment.new()
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color(0.055, 0.07, 0.1)
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.5, 0.55, 0.7)
	environment.ambient_light_energy = 0.8
	env.environment = environment
	add_child(env)
	var ground := MeshInstance3D.new()
	var box := BoxMesh.new(); box.size = Vector3(10, 0.1, 10)
	ground.mesh = box; ground.position.y = -0.1
	var mat := StandardMaterial3D.new(); mat.albedo_color = Color(0.15, 0.18, 0.22); box.material = mat
	add_child(ground)
	var shape := CollisionShape3D.new(); var body := StaticBody3D.new(); var cs := BoxShape3D.new(); cs.size = Vector3(10,0.1,10); shape.shape=cs; shape.position.y=-0.1; body.add_child(shape); add_child(body)
