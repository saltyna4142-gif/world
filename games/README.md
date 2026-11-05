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

The browser scene follows the latest Day 02 world design: a winding turquoise creek, a narrow surface highlight, a waterfall over the island's front-right rim, a plunge pool, and animated splash droplets. The creek and waterfall are positioned against the game's procedural 65×65 terrain approximation. The original Blender generator uses Blender's noise functions, so the browser terrain and water heights are an approximation rather than a direct `.glb` export. The four gameplay modes remain available.
