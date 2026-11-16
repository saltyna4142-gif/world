# Infinite World — Games

A browser-playable 3D prototype inspired by the floating-island world generator in `Blender/scripts/create_world.py`.

## Run
- **Online build:** Open `index.html` in a modern browser with an internet connection. Three.js is loaded from jsDelivr.
- **Offline build:** Open `infinite-world-offline.html`. It bundles Three.js r160 inline, so the game can run without fetching the library from a CDN.

## Modes included
- **Explorer:** roam the island, collect eight glowing crystals, follow four stacked stone cairns, discover the hidden grotto, collect its turquoise crystal, inspect the ancient tablet, gather four aquamarine ore shards, and examine the seal console and its three rune stones with E or a tap.
- **Survival:** gather wood with E and manage food and health.
- **Action RPG:** fight the island slimes with F or a mouse/touch click.
- **Building:** spend three pieces of wood to place a small cabin.

## World landmarks
The browser scene includes the Day 02 winding creek, waterfall, plunge pool and splash droplets; the Day 03 cedar footbridge; the Day 08 cairn trail; the Day 09 hidden grotto entrance and turquoise crystal; the Day 10 sloped cave passage, ancient rune tablet, glowing aquamarine vein and four collectible shards; the Day 11 stone-and-bronze seal console; and the Day 12 three keyed hexagonal rune stones with forked-path, river and mountain glyphs. The cave is a lightweight Three.js approximation of the Blender design, not a direct mesh export. Terrain and water heights are approximations of the Blender scene.

## Controls
WASD / arrow keys to move, Space to jump. On mobile, use the on-screen directional pad. In Survival, hold E near a tree to gather wood; in Action RPG, press F or click to attack; in Building, click to place a cabin. In Explorer, approach the seal console and press E or tap to inspect the three glyphs.
