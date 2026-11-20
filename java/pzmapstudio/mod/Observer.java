package pzmapstudio.mod;

import zombie.GameTime;
import zombie.characters.IsoPlayer;
import zombie.iso.weather.ClimateManager;

/** Compact live snapshot for the storyteller agent. */
public final class Observer {
    private Observer() {}

    public static String snapshot() {
        IsoPlayer player = IsoPlayer.getPlayer(0);
        if (player == null) return "{\"ok\":false,\"error\":\"no player\"}";
        GameTime time = GameTime.getInstance();
        float temperature = 0f;
        try {
            temperature = ClimateManager.getInstance()
                    .getClimateFloat(ClimateManager.FLOAT_TEMPERATURE).getInternalValue();
        } catch (Throwable ignored) {}
        int zombies = 0;
        int items = 0;
        int doors = 0;
        int rooms = 0;
        try {
            var cell = player.getCell();
            int px = (int) Math.floor(player.getX());
            int py = (int) Math.floor(player.getY());
            int pz = (int) Math.floor(player.getZ());
            for (int dx = -12; dx <= 12; dx++) {
                for (int dy = -12; dy <= 12; dy++) {
                    var square = cell.getGridSquare(px + dx, py + dy, pz);
                    if (square == null) continue;
                    for (var object : square.getMovingObjects()) {
                        if (object instanceof zombie.characters.IsoZombie) zombies++;
                    }
                    items += square.getWorldObjects().size();
                    if (square.getIsoDoor() != null) doors++;
                    if (square.getRoom() != null) rooms++;
                }
            }
        } catch (Throwable ignored) {}
        return "{\"ok\":true"
                + ",\"x\":" + player.getX()
                + ",\"y\":" + player.getY()
                + ",\"z\":" + player.getZ()
                + ",\"days\":" + (time != null ? time.getDaysSurvived() : -1)
                + ",\"minutes\":" + (time != null ? time.getMinutes() : -1)
                + ",\"temperature\":" + temperature
                + ",\"zombiesNear\":" + zombies
                + ",\"itemsNear\":" + items
                + ",\"doorsNear\":" + doors
                + ",\"roomsNear\":" + rooms
                + "}";
    }
}
