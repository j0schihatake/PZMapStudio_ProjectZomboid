package pzmapstudio.cli;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import pzmapstudio.core.PzLotWriter;
import pzmapstudio.core.Scene;

import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

/** JSON command CLI seed for the Java core. */
public final class SceneCli {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.out.println("usage: SceneCli new W H FILE | SceneCli apply FILE JSON | SceneCli undo FILE");
            return;
        }
        switch (args[0]) {
            case "new" -> {
                Scene scene = new Scene(Integer.parseInt(args[1]), Integer.parseInt(args[2]), "Untitled");
                scene.save(Path.of(args[3]));
                System.out.println(args[3]);
            }
            case "apply" -> {
                Scene scene = Scene.load(Path.of(args[1]));
                JsonObject result = scene.apply(JsonParser.parseString(args[2]).getAsJsonObject());
                scene.save(Path.of(args[1]));
                System.out.println(result);
            }
            case "undo" -> {
                Scene scene = Scene.load(Path.of(args[1]));
                System.out.println(scene.apply(JsonParser.parseString("{\"op\":\"undo\"}").getAsJsonObject()));
                scene.save(Path.of(args[1]));
            }
            case "rewrite-cell" -> {
                Map<Long, String> overrides = new HashMap<>();
                overrides.put(0L, args[5]);
                PzLotWriter.rewriteCell(Path.of(args[1]), Path.of(args[2]),
                        Integer.parseInt(args[3]), Integer.parseInt(args[4]), overrides);
                System.out.println(args[2]);
            }
            case "export-cell" -> {
                Scene scene = Scene.load(Path.of(args[1]));
                int cx = Integer.parseInt(args[2]), cy = Integer.parseInt(args[3]);
                Map<Long, String> tiles = new HashMap<>();
                for (String layer : new String[]{"roads", "sidewalks", "water", "terrain"}) {
                    scene.layers.getOrDefault(layer, Map.of()).forEach((key, tile) -> {
                        int x = (int) (key >> 32);
                        int y = (int) (key & 0xffffffffL);
                        if (x / 256 == cx && y / 256 == cy) {
                            tiles.put(((long) (x % 256) << 32) ^ (y % 256), tile);
                        }
                    });
                }
                PzLotWriter.writeCell(Path.of(args[4]), cx, cy, tiles, "grass");
                System.out.println(args[4]);
            }
            default -> System.out.println("unknown command");
        }
    }
}
