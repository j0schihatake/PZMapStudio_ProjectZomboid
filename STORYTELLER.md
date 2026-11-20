# Live storyteller architecture

Target: the player plays Project Zomboid while a local AI agent acts like a
RimWorld storyteller — observes the world, chooses incidents, changes the map
and generates story content in real time.

## What the game can do live

A Java/Lua mod can safely change the **loaded world layer**:

- spawn/remove zombies, animals, items and loot;
- place/remove props, furniture, barricades, doors and fences;
- spawn NPCs/events, trigger sounds, weather and messages;
- open/close routes, create temporary camps, crime scenes and story sites;
- read compact state around the player.

The **compiled terrain layer** (`.lotheader/.lotpack` cells) is not reliably
hot-reloaded. Terrain/buildings that require new cells must be:

1. staged and validated;
2. written to a map copy or an offline cell;
3. loaded after save/reload or a controlled chunk refresh.

So the narrator has two lanes:

```text
live lane   objects, spawns, loot, events, NPCs, routes
map lane    terrain/buildings/fences/roads -> staged cells -> reload
```

## Agent loop

```text
game state snapshot (compact JSON)
  -> storyteller planner (cooldowns, tension, player history)
  -> command batch
  -> Java mod applies live commands / stages map commands
  -> audit + backup + undo token
  -> event log and narrative memory
```

The agent never receives the whole map. It receives a bounded area, player
state, recent events and a small command vocabulary.

## Command families

```text
observe.player
observe.area {x,y,radius}
spawn.horde {x,y,count,kind}
spawn.loot {container,x,y,tier}
place.prop {tile,x,y,z}
place.story {kind,x,y,w,h}
route.open/close {x,y}
weather.set {kind,duration}
npc.spawn {kind,x,y}
map.stage {scene,cell}
map.apply {cell,backup:true}
narrator.event {id,cooldowns}
```

## Safety

- all map writes create a backup;
- live commands have budgets and rate limits;
- no silent rewrite of an active save;
- multiplayer/server authority;
- undo/dry-run for destructive commands;
- log every narrator decision for debugging and continuity.

## Phases

1. Observer bridge: player/time/weather/nearby entities.
2. Live incident commands: hordes, loot, props, sounds.
3. Story-site placement and NPC events.
4. Map staging/building edits with reload.
5. Narrative memory and RimWorld-like pacing.
6. Community API/UI and documentation.
