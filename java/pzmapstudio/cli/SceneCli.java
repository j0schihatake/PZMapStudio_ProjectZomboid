package pzmapstudio.cli;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import pzmapstudio.core.Scene;

import java.nio.file.Path;

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
            default -> System.out.println("unknown command");
        }
    }
}
