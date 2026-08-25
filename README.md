# Godot Humanoid Dummy Test Gallery

A Godot 4 playtesting project containing four rigged humanoid variants generated from the same deterministic Blender rig. Each model has 17 bones and `idle` / `walk` animations.

## Included models

- `dummy_gray.glb` — neutral gray
- `dummy_blue.glb` — blue test variant
- `dummy_orange.glb` — orange test variant
- `dummy_green.glb` — green test variant

All models use the same featureless mannequin design: no face, hair, clothing blocks, fingers, thumbs, or decorative details. Hands are rounded palms connected to the forearms. Skinning is rigid per-part prototype weighting.

## Godot test project

Open this directory in Godot 4.7.2 and run `main.tscn`. The scene loads all four GLBs into a test gallery, places them side by side, and includes:

- WASD movement
- Idle/walk animation switching for every loaded model
- Capsule collision
- Camera, lighting, ground, and status label

Godot 4.7.2 headless verification completed successfully: all four GLBs imported and the project started without loader, parse, or runtime script errors.

## Regenerate all variants

```bash
for spec in \
  'dummy_gray 0.46,0.49,0.53' \
  'dummy_blue 0.18,0.38,0.72' \
  'dummy_orange 0.78,0.32,0.10' \
  'dummy_green 0.18,0.55,0.30'; do
  set -- $spec
  MODEL_NAME="$1" MODEL_COLOR="$2" blender -b -P build_featureless_dummy.py
  MODEL_NAME="$1" blender -b -P render_featureless_dummy.py
  MODEL_NAME="$1" blender -b -P verify_featureless_dummy.py
  mv "$1.blend" ../godot_humanoid_prototype_source/multi_models/
done
```

The editable `.blend` sources are kept outside the Godot project so Godot does not try to import them automatically. Blender may report a non-fatal Draco library warning; exports complete without Draco compression.
