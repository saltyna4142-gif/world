# Infinite World — Games

A browser-playable 3D prototype inspired by the floating-island world generator in `Blender/scripts/create_world.py`.

## Run

Open `index.html` in a modern browser with an internet connection. Three.js is loaded from jsDelivr.

## Modes included

- **Explorer:** roam the island and collect eight glowing crystals.
- **Survival:** gather wood with E and manage food and health.
- **Action RPG:** fight the island slimes with F or a mouse/touch click.
- **Building:** spend three pieces of wood to place a small cabin.

Controls: WASD / arrow keys to move, Space to jump. On mobile, use the on-screen directional pad.

The current game scene recreates the Day 01 island procedurally in Three.js, including a 65×65 softened height-field meadow and a rocky floating underside. The source repository currently contains the Blender generator script rather than an exported `.glb` asset. The browser terrain is an approximation of the Blender noise field, not a direct render/export.
