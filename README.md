# Godot Humanoid Prototype

A minimal Godot playtesting project containing a neutral, featureless humanoid dummy.

## Current asset

- `featureless_dummy.glb` — rigged GLB with a 17-bone humanoid skeleton and `idle` / `walk` animations.
- `featureless_dummy_preview.png` — preview render.
- `build_featureless_dummy.py` — deterministic Blender generator.
- `render_featureless_dummy.py` — headless preview renderer.
- `verify_featureless_dummy.py` — Blender/GLB validation script.

The dummy has one neutral material, no face, hair, clothing color blocks, decorative details, fingers, or thumbs. Hands are simple rounded palm forms connected to the forearms.

## Godot project

- `main.tscn` / `main.gd` / `project.godot` — Godot prototype scene and WASD controller.
- The scene loads `res://featureless_dummy.glb`, uses capsule collision, and switches between idle and walk based on WASD input.
- Tested with Godot 4.7.2 in headless mode: GLB import and project startup completed without loader or script errors.

Open this directory as a Godot project and run `main.tscn`.

## Regenerate the dummy

```bash
blender -b -P build_featureless_dummy.py
blender -b -P render_featureless_dummy.py
blender -b -P verify_featureless_dummy.py
```

The model uses rigid per-part prototype skin weights rather than production-quality smooth deformation. Blender may report a non-fatal Draco library warning; the GLB is still exported without Draco compression.

The editable `.blend` sources are kept outside this Godot project so Godot does not try to import them automatically.
