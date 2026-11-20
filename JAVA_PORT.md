# Java-first PZMapStudio

The external Python editor was a prototype. The long-term tool should be a Java
core that runs both:

1. **standalone** as an agent-friendly CLI/HTTP toolkit, without the game;
2. **inside Project Zomboid B42** as a Java mod with a Lua/Java UI.

## Modules

```text
pzmapstudio-core   pure Java: scene, commands, lot reader/writer, audits
pzmapstudio-cli    standalone JSON CLI/HTTP for agents
pzmapstudio-mod    B42 Java mod: file bridge, in-game commands/UI
```

`core` must not depend on `projectzomboid.jar`, so its tests run without the
game. The mod module compiles against the B42 jar with JDK 25 (class major 69),
not Java 21.

## In-game limits

PZ does not hot-reload compiled cells reliably. A live Java mod must therefore:

- edit the scene model and preview immediately;
- write/compile map cells to disk;
- ask the player to save/exit and reload the cell, or use a controlled
  in-memory chunk refresh if the B42 API allows it;
- never silently rewrite an active save.

The agent API is the same JSON command vocabulary as the current Python tool.

## First step

`java/PZMapInfo.java` is the seed: it reads a compiled cell header without any
game dependency. The next port is the lotpack room/tile reader and the scene
command model.

Compile with the bundled JDK 25:

```bash
JAVA=/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/toolchain/oracle-jdk-25/bin
$JAVA/javac -d java/build java/PZMapInfo.java
$JAVA/java -cp java/build PZMapInfo "/path/to/map"
```
