# Infinite World — Games

A browser-playable 3D prototype inspired by the floating-island world generator in `Blender/scripts/create_world.py`.

## Run

Open `index.html` in a modern browser with an internet connection. Three.js is loaded from jsDelivr.

## Modes included

- **Explorer:** roam the island and collect eight glowing crystals.
- **Survival:** gather wood with E and manage food and health.
- **Action RPG:** fight the island slimes with F or a mouse/touch click.
- **Building:** spend three pieces of wood to place a small cabin.

The browser scene now also includes the Day 03 cedar footbridge at the creek bend, with stringers, plank deck, bank supports, and handrails. The bridge deck uses a simple jump-to-board landing check so the player can jump onto it and cross the stream. The bridge is a Three.js approximation of the Blender generator; terrain height remains an approximation rather than a direct `.glb` export.

Controls: WASD / arrow keys to move, Space to jump. On mobile, use the on-screen directional pad.

The browser scene follows the latest Day 03 world design: the Day 02 winding turquoise creek, waterfall, plunge pool and splash droplets are retained, and the cedar footbridge is added at the creek bend. The island uses a procedural 65×65 terrain approximation; Blender's noise functions are not exported directly, so the browser terrain and water heights are approximate rather than a direct `.glb` import. All four gameplay modes remain available.
