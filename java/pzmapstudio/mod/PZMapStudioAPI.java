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

    public String command(String scenePath, String json) throws Exception {
        Scene scene = Scene.load(Path.of(scenePath));
        String result = scene.apply(com.google.gson.JsonParser.parseString(json).getAsJsonObject()).toString();
        scene.save(Path.of(scenePath));
        return result;
    }
}
