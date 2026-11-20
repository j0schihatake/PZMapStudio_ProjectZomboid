package pzmapstudio.mod;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;

/** File-based command queue for an external agent. */
public final class AgentQueue {
    private AgentQueue() {}

    private static Path base() {
        String override = System.getProperty("pzmapstudio.queueDir");
        if (override != null && !override.isBlank()) return Path.of(override);
        return Path.of(System.getProperty("user.home"), "Zomboid", "PZMapStudio");
    }

    public static String poll() {
        try {
            Path dir = base();
            Files.createDirectories(dir);
            Path queue = dir.resolve("queue.jsonl");
            Path responses = dir.resolve("responses.jsonl");
            if (!Files.exists(queue)) return "";
            List<String> lines = Files.readAllLines(queue);
            List<String> out = new ArrayList<>();
            for (String line : lines) {
                if (line.isBlank()) continue;
                try {
                    JsonObject cmd = JsonParser.parseString(line).getAsJsonObject();
                    String op = cmd.has("op") ? cmd.get("op").getAsString() : "";
                    String result = switch (op) {
                        case "observe" -> Observer.snapshot();
                        case "horde" -> "spawned=" + Live.horde(cmd.has("count") ? cmd.get("count").getAsInt() : 5);
                        case "loot" -> "loot=" + Live.loot(
                                cmd.has("item") ? cmd.get("item").getAsString() : "Base.Bandage",
                                cmd.has("count") ? cmd.get("count").getAsInt() : 1);
                        default -> "unknown=" + op;
                    };
                    JsonObject response = new JsonObject();
                    response.addProperty("op", op);
                    response.addProperty("result", result);
                    out.add(new Gson().toJson(response));
                } catch (Exception error) {
                    JsonObject response = new JsonObject();
                    response.addProperty("error", error.toString());
                    out.add(new Gson().toJson(response));
                }
            }
            if (!out.isEmpty()) {
                Files.write(responses, out, StandardOpenOption.CREATE, StandardOpenOption.APPEND);
            }
            Files.write(queue, new byte[0]);
            return String.join("\n", out);
        } catch (Exception error) {
            return "queue-error=" + error;
        }
    }
}
