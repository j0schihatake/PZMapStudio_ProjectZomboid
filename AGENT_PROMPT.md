# Prompt for an external agent

Paste this to your agent while Project Zomboid is running with PZMapStudio:

```text
You are working with Project Zomboid and PZMapStudio.

1. Find the PZMapStudio folder in the game/Workshop directory.
2. Read README.txt, JAVA_MOD.md and AGENT_QUEUE.md.
3. Check the Java mod loaded in console.txt.
4. Use the live queue instead of editing save files:
   ~/Zomboid/PZMapStudio/queue.jsonl
5. Useful commands:
   python3 tools/live_queue.py --op observe --wait 3
   python3 tools/live_queue.py --op story --kind camp --x <x> --y <y> --wait 3
   python3 tools/live_queue.py --op weather --kind storm --seconds 120
   python3 tools/live_queue.py --op door --x <x> --y <y> --z 0 --open
6. Before any map-cell write, make a backup and validate rooms/buildings.
7. Do not edit an active save silently; ask for a new save when adding maps.
8. Report every command and its response.
```

For map work without the game, use the standalone Java/Python CLI and
`tools/beautify_parallel.py`; keep a backup and run `validate-map`.
