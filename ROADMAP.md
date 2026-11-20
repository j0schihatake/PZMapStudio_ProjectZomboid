# Roadmap

## Done

- command-driven sparse scene;
- multi-storey houses, rooms, furniture;
- paint/erase terrain, roads, water, walls, floors;
- spawn markers;
- undo/redo;
- JSON save/load;
- PNG preview;
- HTTP command API;
- overlay import from a compiled PZ map folder (cell bounds + spawns);
- PZ-oriented bundle export;
- terrain-only `.lotheader`/`.lotpack` writer and round-trip test.

## Next

1. Decode and re-encode `.lotheader`/`.lotpack` so a scene can round-trip
   compiled terrain and buildings.
2. Attach the existing KnoxMap/WorldEd compiler as the backend for real cell
   output.
3. Read terrain and buildings from a generated Isilkul/Omsk map, not just its
   spawn points.
4. Browser UI with the same command API: paint, house tool, floor selector,
   furniture palette, spawn markers.
5. Procedural art pass: roadside cleaning, tree lines, yards, benches, lamps,
   fences, parking.
6. Batch agent plans: a JSON list of commands applied in one transaction.

## Long-term: live in-game agent editing

Add a bridge that lets an agent modify a running/loaded map instead of only
editing files offline:

- live scene API backed by the currently loaded cells;
- agent commands for placing/removing props, fences, roads and base modules;
- regenerate or improve AI-controlled survivor/NPC bases in place;
- safe hot-reload or next-cell reload of edited regions;
- undo, permission boundaries and a dry-run preview before touching a save;
- multiplayer/server authority and conflict handling;
- fallback to offline PZMapStudio export when the game cannot hot-reload a cell.

This is the final stage, after the offline editor, WorldEd bridge and art rules
are stable. It must never silently rewrite an active save.
