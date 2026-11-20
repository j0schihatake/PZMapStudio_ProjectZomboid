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
