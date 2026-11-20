package pzmapstudio.mod;

import pzmapstudio.core.PzLot;
import pzmapstudio.core.Scene;

import java.nio.file.Path;

/** Java-mod entry point. B42 loads this class via javaPkgName. */
public final class Main {
    public static final String VERSION = "0.1.0";

    public static void main(String[] args) {
        System.out.println("[PZMapStudio] Java mod " + VERSION + " loaded");
        System.out.println("[PZMapStudio] " + help());
    }

    public static String help() {
        return "PZMapStudio Java core; use the standalone CLI/HTTP agent or the map tools. "
                + "This Workshop mod preview exposes the Java core; map editing UI is the next step.";
    }

    public static String audit(String folder) throws Exception {
        Path dir = Path.of(folder);
        int cells = 0, rooms = 0, buildings = 0;
        try (var stream = java.nio.file.Files.list(dir)) {
            for (Path header : stream.filter(p -> p.toString().endsWith(".lotheader")).toList()) {
                PzLot.Header h = PzLot.readHeader(header);
                cells++; rooms += h.rooms().size(); buildings += h.buildings().size();
            }
        }
        return "cells=" + cells + " rooms=" + rooms + " buildings=" + buildings;
    }

    public static String command(String scenePath, String json) throws Exception {
        Scene scene = Scene.load(Path.of(scenePath));
        String result = scene.apply(com.google.gson.JsonParser.parseString(json).getAsJsonObject()).toString();
        scene.save(Path.of(scenePath));
        return result;
    }
}
