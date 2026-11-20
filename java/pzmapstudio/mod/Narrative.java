package pzmapstudio.mod;

import java.util.HashMap;
import java.util.Map;

/** Tiny cooldown memory so the agent cannot spam the same story beat. */
public final class Narrative {
    private static final Map<String, Long> LAST = new HashMap<>();
    private Narrative() {}

    public static synchronized String story(String kind, int x, int y, int cooldownSeconds) {
        long now = System.currentTimeMillis() / 1000L;
        long last = LAST.getOrDefault(kind, 0L);
        long wait = cooldownSeconds - (now - last);
        if (wait > 0) {
            return "cooldown=" + wait + "s kind=" + kind;
        }
        LAST.put(kind, now);
        return Live.story(kind, x, y);
    }
}
