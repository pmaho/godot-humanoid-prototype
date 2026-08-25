extends Node3D

@onready var player: CharacterBody3D = $CharacterBody3D
@onready var model: Node3D = $CharacterBody3D/Model
@onready var anim: AnimationPlayer = $CharacterBody3D/AnimationPlayer

const SPEED := 2.5
var model_scene: Node3D
var model_anim_players: Array[AnimationPlayer] = []
var model_instances: Array[Node3D] = []
const MODEL_ASSETS := [
    {"path": "res://dummy_gray.glb", "position": Vector3(-1.8, 0.0, 0.0)},
    {"path": "res://dummy_blue.glb", "position": Vector3(-0.6, 0.0, 0.0)},
    {"path": "res://dummy_orange.glb", "position": Vector3(0.6, 0.0, 0.0)},
    {"path": "res://dummy_green.glb", "position": Vector3(1.8, 0.0, 0.0)},
]

func _ready() -> void:
    var capsule := CapsuleShape3D.new()
    capsule.radius = 0.28
    capsule.height = 1.8
    $CharacterBody3D/CollisionShape3D.shape = capsule
    $CharacterBody3D/CollisionShape3D.position.y = 0.9
    for item in MODEL_ASSETS:
        var scene_asset: PackedScene = load(item.path)
        if scene_asset == null:
            push_error("Could not load %s" % item.path)
            continue
        var instance: Node3D = scene_asset.instantiate()
        instance.position = item.position
        model.add_child(instance)
        model_instances.append(instance)
        var asset_anim := instance.get_node_or_null("AnimationPlayer") as AnimationPlayer
        if asset_anim != null:
            model_anim_players.append(asset_anim)
            if asset_anim.has_animation("idle"):
                asset_anim.play("idle")

func _physics_process(_delta: float) -> void:
    var input_vec := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
    var direction := Vector3(input_vec.x, 0.0, input_vec.y)
    player.velocity.x = direction.x * SPEED
    player.velocity.z = direction.z * SPEED
    player.move_and_slide()
    if direction.length_squared() > 0.01:
        player.look_at(player.global_position + direction, Vector3.UP)
        for asset_anim in model_anim_players:
            if asset_anim.has_animation("walk") and asset_anim.current_animation != "walk":
                asset_anim.play("walk")
        for instance in model_instances:
            instance.rotation.y = lerp_angle(instance.rotation.y, player.rotation.y, 0.15)
    else:
        for asset_anim in model_anim_players:
            if asset_anim.has_animation("idle") and asset_anim.current_animation != "idle":
                asset_anim.play("idle")

func _process(_delta: float) -> void:
    $Camera3D.look_at(player.global_position + Vector3(0, 0.9, 0), Vector3.UP)
    $UI/Label.text = "WASD to move — %s" % ("WALK" if player.velocity.length() > 0.1 else "IDLE")

func _create_world() -> void:
    pass

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
