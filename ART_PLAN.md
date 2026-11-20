# Omsk Expansion — art and tooling plan

## Vision

Turn the six generated maps into one coherent, cinematic-but-playable region:

- streets read as streets, not grass with outlines;
- yards, courtyards, fences and tree lines feel intentionally composed;
- benches, bins, lamps, tables, beds and shop furniture are placed where a
  person would actually use them;
- large buildings have believable roof access: external stairs or ladders,
  roof doors/hatches, railings and rooftop clutter;
- the result stays performant, save-safe and free of cell seams.

## Non-negotiables

- No duplicate compiled cells.
- Every map starts in a new save and loads from the standard map.
- Spawn points are inside owned cells.
- No furniture blocks doors, stairs or the only path through a room.
- No map exceeds the PZ building-state save limit.
- Every visual pass has an in-game screenshot and a before/after note.

## Phase 0 — stabilize the current mod

- [ ] Reinstall the trimmed `omsk-expansion` into a clean mods folder.
- [ ] Start a new save, spawn in Isilkul, walk the streets around the spawn.
- [ ] Record grass-on-road or split-road locations as tile coordinates and
      screenshots.
- [ ] Check all six maps for missing terrain, holes and hard seams.
- [ ] Verify cell ownership is still one map per compiled cell.
- [ ] Verify spawn points still resolve after trimming.

Exit: no duplicate cells, no invalid spawns, roads visible in game.

## Phase 1 — finish the editor foundation

- [x] Decode buildings, rooms and a first pass of furniture from compiled lots.
- [ ] Write `.lotheader`/`.lotpack` back, or bridge to the WorldEd/KnoxMap
      compiler for final cells.
- [ ] Round-trip a small Isilkul region: import, edit, export, load in game.
- [ ] Browser UI on the existing command API: pan/zoom, paint, house tool,
      floor selector, furniture palette, spawn markers, undo/redo.
- [ ] Batch command plans for agents with validation and rollback.
- [ ] Preview renders that use real PZ tile names and colours.

Exit: an edit in PZMapStudio becomes a changed tile in a PZ map.

## Phase 2 — art direction and street design

- [ ] Define a reference board: Russian provincial streets, courtyards,
      industrial edges, forest/field transitions.
- [ ] Road hierarchy: highways, town streets, lanes, dirt roads, sidewalks,
      kerbs, crossings, bus stops.
- [ ] Village roads: realistic width, soft shoulders, drainage ditches,
      gravel/dirt sections, gates and driveways instead of road-to-lawn cuts.
- [ ] Village fences: picket, board, metal and woven fences with readable
      gates, posts and gaps; fences follow yards instead of cutting roads.
- [ ] Fences must not block doors, paths, hydrants, bins or vehicle access.
- [ ] Street cross-sections: road, kerb, sidewalk, front yard, fence, building
      line, backyard.
- [ ] Remove grass overlays from paved surfaces and repair the grass/road
      blend at cell boundaries.
- [ ] Tree lines along roads and fields, not random tree confetti.
- [ ] Utility poles, signs, fences, gates, bins, garages, parking.
- [ ] Palette pass: consistent ground, roofs, walls and vegetation.

Exit: screenshots read as a designed settlement, not a random tile field.
Village roads and fences must read as lived-in property boundaries, not a
single fence line pasted through every yard.

## Phase 3 — practical furniture rules

- [ ] Build the asset catalog from the installed game: every tile, item and
      story-clutter table must be queryable by the agent.
- [ ] Story sites: place murder scenes, camps, road accidents, parties and
      other randomized-story anchors with item palettes and clear footprints.
- [ ] Rule engine keyed by room type, entrance, window and circulation.
- [ ] Benches: along walking routes and in yards, facing the view, clear of
      doors and paths.
- [ ] Bins: beside benches, entrances and parking, not in the middle of a lawn.
- [ ] Lamps: intersections, entrances, yards and long paths.
- [ ] Kitchens: counter run, sink, stove, fridge, table with clear approach.
- [ ] Bedrooms: bed against a wall, wardrobe, desk near window, clear door.
- [ ] Living rooms: sofa/TV relationship, table, circulation behind seating.
- [ ] Shops/offices: counters, shelves, staff path, customer path.
- [ ] Outdoors: picnic tables, playgrounds, drying racks, sheds, woodpiles.
- [ ] Audit: no furniture on stairs, no blocked doors, no sealed rooms.

Exit: every furnished room has a use and a walkable path.

## Phase 4 — roof access and verticality

- [x] Model exterior stairs/ladders in the scene (`add_roof_access`).
- [ ] Add external stairs or wall ladders with valid PZ stair/ladder tiles.
- [ ] Roof doors/hatches, railings, parapets and safe landings.
- [ ] Rooftop props: AC units, vents, water tanks, antennas, crates.
- [ ] Ensure ground access is readable and not hidden inside a wall.
- [ ] Verify collision/navigation: player and zombies can use the route.
- [ ] Optional loot/zombie spawns on accessible roofs.

Exit: at least the main large buildings have a believable, usable roof route.

## Phase 5 — map-wide composition

- [ ] Stitch map seams so roads, rails and rivers continue.
- [ ] Fill gaps between cities with fields, shelterbelts, lakes and villages.
- [ ] Add landmarks and silhouettes: water towers, factory chimneys, church
      spires, bridges, grain elevators.
- [ ] Break repetitive blocks with courtyards, vacant lots and varied setbacks.
- [ ] Density pass: fewer, better props rather than noise.
- [ ] Performance pass: cell counts, object counts, zombie density, load time.

Exit: a drive through the region has rhythm, landmarks and no dead voids.

## Phase 6 — validation

- [ ] Automated map audit: cells, spawns, door/stair/furniture blockers.
- [ ] Save-state size check for every map.
- [ ] In-game drive test through all six maps.
- [ ] Before/after screenshot set for every city.
- [ ] Regression run after every art batch.

Exit: all checks green; no new overlap or save warning.

## Phase 7 — release

- [ ] One combined mod with all maps.
- [ ] GitHub release archive.
- [ ] Steam Workshop upload, split into regional items if the 6+ GB item is
      rejected.
- [ ] Public PZMapStudio docs and API examples.
- [ ] Credits: OpenStreetMap ODbL, KnoxMap, tile authors.

## Milestones

| Milestone | Result |
|---|---|
| M0 | Current mod reinstalled and street problem reproduced/fixed |
| M1 | One real Isilkul region edited and loaded back in game |
| M2 | Road/sidewalk/yard art pass on Isilkul |
| M3 | Furniture rule engine + audits |
| M4 | Roof stairs/ladders on large buildings |
| M5 | All six maps art pass |
| M6 | Performance/save audit and release |

## Definition of done

A new player can start in Isilkul, drive through Omsk, Krasnodar, Novosibirsk
and Moscow, see continuous roads and believable streets, enter furnished
buildings with practical layouts, climb to selected roofs, and play for a long
session without lag, missing cells or save warnings.
