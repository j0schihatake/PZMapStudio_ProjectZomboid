# Agent command queue

The Java mod polls a file queue while the game runs:

```text
~/Zomboid/PZMapStudio/queue.jsonl
~/Zomboid/PZMapStudio/responses.jsonl
```

Write one JSON command per line:

```json
{"op":"observe"}
{"op":"horde","count":5}
{"op":"loot","item":"Base.Bandage","count":3}
```

The Lua layer calls the Java queue every ~2 seconds and prints responses to
`console.txt`. The queue is truncated after processing; responses are appended.

This is the first live agent bridge that does not require an external HTTP
server inside the game. It is intentionally restricted to live commands; map
cell writes still use the explicit Apply cell button with backup/validation.
