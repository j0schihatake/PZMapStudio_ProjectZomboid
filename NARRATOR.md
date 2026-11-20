# External storyteller loop

`tools/narrator.py` is a small RimWorld-like loop that talks to the game through
the same file queue as an agent:

```bash
python3 tools/narrator.py --once
python3 tools/narrator.py --interval 10
```

It asks for `observe`, then:

- many zombies nearby → fog/weather beat;
- many items nearby → crime scene;
- otherwise → camp.

There is a 90-second cooldown between story beats. It never edits map cells or
the save; all effects go through the Java mod.
