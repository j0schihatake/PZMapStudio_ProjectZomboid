package pzmapstudio.mod;

import pzmapstudio.core.PzLot;
import pzmapstudio.core.Scene;

import java.nio.file.Path;
import java.util.List;

/** Java API exposed to the B42 Lua layer. */
public final class PZMapStudioAPI {
    private static final PZMapStudioAPI INSTANCE = new PZMapStudioAPI();

    private PZMapStudioAPI() {}

    public static PZMapStudioAPI getInstance() { return INSTANCE; }

    public String status() {
        return "PZMapStudio Java " + Main.VERSION + " loaded; scene/lot core ready";
    }

    public String weather(String kind, float seconds) {
        return Live.weather(kind, seconds);
    }

    public String story(String kind, int x, int y) {
        return Live.story(kind, x, y);
    }

    public int loot(String itemId, int count) {
        return Live.loot(itemId, count);
    }

    public int horde(int count) {
        return Live.horde(count);
    }

    public String pollAgentQueue() {
        return AgentQueue.poll();
    }

    public String observe() {
        return Observer.snapshot();
    }

    public String help() {
        return "PZMapStudio: Java core ready. Commands: audit <map-folder>, "
                + "command <scene.json> <json>. Standalone CLI/HTTP has the full toolkit.";
    }

    public String audit(String folder) throws Exception {
        Path dir = Path.of(folder);
        int cells = 0, rooms = 0, buildings = 0;
        try (var stream = java.nio.file.Files.list(dir)) {
            List<Path> headers = stream.filter(p -> p.toString().endsWith(".lotheader")).toList();
            for (Path header : headers) {
                PzLot.Header h = PzLot.readHeader(header);
                cells++;
                rooms += h.rooms().size();
                buildings += h.buildings().size();
            }
        }
        return "cells=" + cells + " rooms=" + rooms + " buildings=" + buildings;
    }

    public String newScene(String scenePath, int width, int height) throws Exception {
        Scene scene = new Scene(width, height, "PZMapStudio in-game");
        scene.save(Path.of(scenePath));
        return "scene=" + scenePath + " " + width + "x" + height;
    }

    public String exportCell(String scenePath, int cellX, int cellY,
                             String outFolder) throws Exception {
        Scene scene = Scene.load(Path.of(scenePath));
        java.util.Map<Long, String> tiles = new java.util.HashMap<>();
        for (String layer : new String[]{"roads", "sidewalks", "water", "terrain"}) {
            for (var entry : scene.layers.getOrDefault(layer, java.util.Map.of()).entrySet()) {
                int x = (int) (entry.getKey() >> 32);
                int y = (int) (entry.getKey() & 0xffffffffL);
                if (x / 256 == cellX && y / 256 == cellY) {
                    tiles.put(((long) (x % 256) << 32) ^ (y % 256), entry.getValue());
                }
            }
        }
        pzmapstudio.core.PzLotWriter.writeCell(Path.of(outFolder), cellX, cellY, tiles, "grass");
        var header = pzmapstudio.core.PzLot.readHeader(
                Path.of(outFolder).resolve(cellX + "_" + cellY + ".lotheader"));
        return "exported cell " + cellX + "_" + cellY + " to " + outFolder
                + " (version=" + header.version() + ", tiles=" + header.names().size()
                + ", rooms=" + header.rooms().size() + ", buildings=" + header.buildings().size() + ")";
    }

    public String applyCell(String scenePath, String mapFolder, int cellX, int cellY)
            throws Exception {
        Path map = Path.of(mapFolder);
        Scene scene = Scene.load(Path.of(scenePath));
        java.util.Map<Long, String> overrides = new java.util.HashMap<>();
        for (String layer : new String[]{"roads", "sidewalks", "props"}) {
            for (var entry : scene.layers.getOrDefault(layer, java.util.Map.of()).entrySet()) {
                int x = (int) (entry.getKey() >> 32);
                int y = (int) (entry.getKey() & 0xffffffffL);
                if (x / 256 == cellX && y / 256 == cellY) {
                    overrides.put(((long) (x % 256) << 32) ^ (y % 256), entry.getValue());
                }
            }
        }
        Path temp = java.nio.file.Files.createTempDirectory("pzmapstudio-cell");
        try {
            pzmapstudio.core.PzLotWriter.rewriteCell(map, temp, cellX, cellY, overrides);
            var check = pzmapstudio.core.PzLot.readHeader(temp.resolve(cellX + "_" + cellY + ".lotheader"));
            Path backup = map.resolve("PZMapStudioBackup")
                    .resolve(java.time.LocalDateTime.now().toString().replace(':', '-'));
            java.nio.file.Files.createDirectories(backup);
            for (String name : new String[]{cellX + "_" + cellY + ".lotheader",
                    "world_" + cellX + "_" + cellY + ".lotpack"}) {
                Path source = map.resolve(name);
                if (java.nio.file.Files.exists(source)) {
                    java.nio.file.Files.copy(source, backup.resolve(name),
                            java.nio.file.StandardCopyOption.REPLACE_EXISTING);
                }
            }
            for (String name : new String[]{cellX + "_" + cellY + ".lotheader",
                    "world_" + cellX + "_" + cellY + ".lotpack"}) {
                java.nio.file.Files.copy(temp.resolve(name), map.resolve(name),
                        java.nio.file.StandardCopyOption.REPLACE_EXISTING);
            }
            return "applied cell " + cellX + "_" + cellY + " rooms=" + check.rooms().size()
                    + " buildings=" + check.buildings().size() + " backup=" + backup;
        } finally {
            try (var stream = java.nio.file.Files.walk(temp)) {
                stream.sorted(java.util.Comparator.reverseOrder()).forEach(p -> {
                    try { java.nio.file.Files.deleteIfExists(p); } catch (Exception ignored) {}
                });
            }
        }
    }

    public String command(String scenePath, String json) throws Exception {
        Scene scene = Scene.load(Path.of(scenePath));
        String result = scene.apply(com.google.gson.JsonParser.parseString(json).getAsJsonObject()).toString();
        scene.save(Path.of(scenePath));
        return result;
    }
}
