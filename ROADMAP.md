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


## Interiors

- never leave grass, road or water tiles inside a building footprint;
- `clean_interiors` removes outdoor ground and lays interior floor;
- audit flags any outdoor tile inside a building;
- imported buildings must receive the same cleanup before an art pass.

## Reference-driven buildings

- attach photos/URLs/coordinates to a building or street;
- import user-supplied screenshots and open sources (OSM, Mapillary, Wikimedia);
- derive footprint, floors, roof, material and entrance side from references;
- side-by-side reference/preview in the browser UI;
- never bulk-scrape or redistribute Google Street View imagery;
- strip non-open references before publishing a Workshop item.

## Trumbull Valley (State of Decay-inspired) — manual map

Add a manual, **State of Decay-inspired** Trumbull Valley map if it fits the
world grid and save limits. This is not an asset import and not a copy of the
game map; it is a hand-built reconstruction of the valley's layout and
landmarks.

- choose a free cell block, e.g. east of Krasnodar (`x≈112, y=0`) or south of
  Moscow (`x=0, y≈130`); verify no overlap with all existing map cells;
- footprint about 8×8 km at 2.0–2.25 m/tile (roughly 12×12 cells), split into
  more than one map if it does not fit the save-state budget;
- hand-trace the valley silhouette, highway, river, Marshall, Spencer's Mill,
  the church, fairground, farms and forest edges;
- add roof access, practical furniture, fences and story sites;
- keep names/art stylised; no ripped State of Decay assets;
- package as an optional map in the same mod, or as a separate Workshop item if
  the combined mod exceeds the Workshop size limit;
- run `map-save-audit` before publishing.

Acceptance: a new save can spawn in or drive to the valley; no duplicate cells;
rooms/buildings under the PZ save buffer; no copyrighted assets.
