extends Node3D

@onready var player: CharacterBody3D = $CharacterBody3D
@onready var model: Node3D = $CharacterBody3D/Model
@onready var anim: AnimationPlayer = $CharacterBody3D/AnimationPlayer

const SPEED := 2.5
var model_scene: Node3D

func _ready() -> void:
    var capsule := CapsuleShape3D.new()
    capsule.radius = 0.28
    capsule.height = 1.8
    $CharacterBody3D/CollisionShape3D.shape = capsule
    $CharacterBody3D/CollisionShape3D.position.y = 0.9
    model_scene = load("res://featureless_dummy.glb").instantiate()
    model.add_child(model_scene)
    var lib: AnimationPlayer = model_scene.get_node_or_null("AnimationPlayer")
    if lib != null:
        anim = lib
    if anim.has_animation("idle"):
        anim.play("idle")

func _physics_process(_delta: float) -> void:
    var input_vec := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
    var direction := Vector3(input_vec.x, 0.0, input_vec.y)
    player.velocity.x = direction.x * SPEED
    player.velocity.z = direction.z * SPEED
    player.move_and_slide()
    if direction.length_squared() > 0.01:
        player.look_at(player.global_position + direction, Vector3.UP)
        if anim.has_animation("walk") and anim.current_animation != "walk":
            anim.play("walk")
    elif anim.has_animation("idle") and anim.current_animation != "idle":
        anim.play("idle")

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
