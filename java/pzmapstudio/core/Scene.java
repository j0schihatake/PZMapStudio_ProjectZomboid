package pzmapstudio.core;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;

/** Sparse scene and JSON commands; no Project Zomboid dependency. */
public final class Scene {
    public int width, height;
    public String name = "Untitled";
    public Map<String, Map<Long, String>> layers = new LinkedHashMap<>();
    public List<JsonObject> spawns = new ArrayList<>();
    public List<JsonObject> buildings = new ArrayList<>();
    private final transient Deque<String> undo = new ArrayDeque<>();
    private final transient Deque<String> redo = new ArrayDeque<>();
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();

    public Scene() {}
    public Scene(int width, int height, String name) {
        this.width = width; this.height = height; this.name = name;
        for (String layer : List.of("terrain", "roads", "sidewalks", "water", "floors", "walls", "objects", "props", "zones")) {
            layers.put(layer, new HashMap<>());
        }
    }

    public static Scene load(Path path) throws IOException {
        Scene scene = GSON.fromJson(Files.readString(path), Scene.class);
        if (scene.layers == null) scene.layers = new LinkedHashMap<>();
        for (String layer : List.of("terrain", "roads", "sidewalks", "water", "floors", "walls", "objects", "props", "zones")) {
            scene.layers.computeIfAbsent(layer, ignored -> new HashMap<>());
        }
        return scene;
    }

    public void save(Path path) throws IOException {
        Files.writeString(path, GSON.toJson(this));
    }

    private String snapshot() { return GSON.toJson(this); }

    private void restore(String json) {
        Scene other = GSON.fromJson(json, Scene.class);
        this.width = other.width; this.height = other.height; this.name = other.name;
        this.layers = other.layers; this.spawns = other.spawns; this.buildings = other.buildings;
    }

    public JsonObject apply(JsonObject cmd) {
        String op = cmd.get("op").getAsString();
        if (!op.equals("undo") && !op.equals("redo")) undo.push(snapshot());
        JsonObject result = new JsonObject();
        result.addProperty("op", op);
        switch (op) {
            case "paint" -> result.addProperty("painted", paint(
                    cmd.get("layer").getAsString(), cmd.get("x").getAsInt(), cmd.get("y").getAsInt(),
                    cmd.get("w").getAsInt(), cmd.get("h").getAsInt(), cmd.get("tile").getAsString()));
            case "erase" -> result.addProperty("erased", erase(
                    cmd.get("layer").getAsString(), cmd.get("x").getAsInt(), cmd.get("y").getAsInt(),
                    cmd.get("w").getAsInt(), cmd.get("h").getAsInt()));
            case "build_house" -> buildHouse(cmd, result);
            case "place_object" -> {
                int x = cmd.get("x").getAsInt(), y = cmd.get("y").getAsInt();
                if (x < 0 || y < 0 || x >= width || y >= height) {
                    throw new IllegalArgumentException("object outside scene");
                }
                layers.computeIfAbsent("props", ignored -> new HashMap<>()).put(key(x, y), cmd.get("tile").getAsString());
                result.addProperty("x", x); result.addProperty("y", y);
                result.addProperty("tile", cmd.get("tile").getAsString());
            }
            case "add_spawn" -> {
                if (cmd.has("x") && cmd.has("y")) {
                    spawns.add(cmd.deepCopy());
                    result.addProperty("spawns", spawns.size());
                }
            }
            case "undo" -> {
                if (undo.isEmpty()) throw new IllegalStateException("nothing to undo");
                redo.push(snapshot()); restore(undo.pop()); result.addProperty("undone", true);
            }
            case "redo" -> {
                if (redo.isEmpty()) throw new IllegalStateException("nothing to redo");
                undo.push(snapshot()); restore(redo.pop()); result.addProperty("redone", true);
            }
            default -> throw new IllegalArgumentException("unknown op: " + op);
        }
        return result;
    }

    private int paint(String layer, int x, int y, int w, int h, String tile) {
        check(x, y, w, h);
        Map<Long, String> cells = layers.computeIfAbsent(layer, ignored -> new HashMap<>());
        for (int yy = y; yy < y + h; yy++) for (int xx = x; xx < x + w; xx++) {
            cells.put(key(xx, yy), tile);
        }
        return w * h;
    }

    private int erase(String layer, int x, int y, int w, int h) {
        check(x, y, w, h);
        Map<Long, String> cells = layers.computeIfAbsent(layer, ignored -> new HashMap<>());
        int removed = 0;
        for (int yy = y; yy < y + h; yy++) for (int xx = x; xx < x + w; xx++) {
            if (cells.remove(key(xx, yy)) != null) removed++;
        }
        return removed;
    }

    private void buildHouse(JsonObject cmd, JsonObject result) {
        int x = cmd.get("x").getAsInt(), y = cmd.get("y").getAsInt();
        int w = cmd.get("w").getAsInt(), h = cmd.get("h").getAsInt();
        int floors = cmd.has("floors") ? cmd.get("floors").getAsInt() : 1;
        check(x, y, w, h);
        JsonObject building = new JsonObject();
        building.addProperty("x", x); building.addProperty("y", y);
        building.addProperty("w", w); building.addProperty("h", h);
        building.addProperty("floors", Math.max(1, floors));
        buildings.add(building);
        paint("floors", x + 1, y + 1, Math.max(1, w - 2), Math.max(1, h - 2), "floor");
        result.addProperty("building", buildings.size() - 1);
        result.addProperty("floors", Math.max(1, floors));
    }

    private void check(int x, int y, int w, int h) {
        if (w <= 0 || h <= 0 || x < 0 || y < 0 || x + w > width || y + h > height) {
            throw new IllegalArgumentException("rectangle outside scene");
        }
    }

    private static long key(int x, int y) { return ((long) x << 32) ^ (y & 0xffffffffL); }
}
