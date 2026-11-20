package pzmapstudio.mod;

import zombie.characters.IsoPlayer;
import zombie.characters.IsoZombie;
import zombie.iso.IsoWorld;

/** Small live-incident bridge; budgeted and player-relative. */
public final class Live {
    private Live() {}

    public static int loot(String itemId, int count) {
        IsoPlayer player = IsoPlayer.getPlayer(0);
        if (player == null || IsoWorld.instance == null) return 0;
        var cell = IsoWorld.instance.getCell();
        if (cell == null) return 0;
        var square = cell.getGridSquare((int) player.getX(), (int) player.getY(), (int) player.getZ());
        if (square == null) return 0;
        int spawned = 0;
        for (int i = 0; i < Math.min(20, count); i++) {
            try {
                square.AddWorldInventoryItem(itemId, 0.2f + 0.1f * i, 0.2f, 0f);
                spawned++;
            } catch (Throwable ignored) {}
        }
        return spawned;
    }

    public static int lootAt(String itemId, int x, int y, int count) {
        if (IsoWorld.instance == null) return 0;
        var cell = IsoWorld.instance.getCell();
        if (cell == null) return 0;
        var square = cell.getGridSquare(x, y, 0);
        if (square == null) return 0;
        int spawned = 0;
        for (int i = 0; i < Math.min(20, count); i++) {
            try {
                square.AddWorldInventoryItem(itemId, 0.2f + 0.1f * i, 0.2f, 0f);
                spawned++;
            } catch (Throwable ignored) {}
        }
        return spawned;
    }

    public static int hordeAt(int x, int y, int count) {
        if (IsoWorld.instance == null) return 0;
        var cell = IsoWorld.instance.getCell();
        if (cell == null) return 0;
        int spawned = 0;
        int budget = Math.max(0, Math.min(40, count));
        for (int i = 0; i < budget; i++) {
            try {
                IsoZombie zombie = new IsoZombie(cell);
                double angle = (Math.PI * 2 * i) / budget;
                zombie.setX((float) (x + Math.cos(angle) * (2 + i % 4)));
                zombie.setY((float) (y + Math.sin(angle) * (2 + i % 4)));
                zombie.setZ(0);
                cell.addMovingObject(zombie);
                spawned++;
            } catch (Throwable ignored) {}
        }
        return spawned;
    }

    public static String story(String kind, int x, int y) {
        return switch (kind) {
            case "horde" -> "horde=" + hordeAt(x, y, 6);
            case "loot" -> "loot=" + lootAt("Base.Bandage", x, y, 3);
            case "camp" -> "camp loot=" + lootAt("Base.CampfireKit", x, y, 1);
            case "crime" -> "crime loot=" + lootAt("Base.Knife", x, y, 1);
            default -> "unknown story=" + kind;
        };
    }

    public static int horde(int count) {
        IsoPlayer player = IsoPlayer.getPlayer(0);
        if (player == null || IsoWorld.instance == null) return 0;
        var cell = IsoWorld.instance.getCell();
        if (cell == null) return 0;
        int spawned = 0;
        int budget = Math.max(0, Math.min(40, count));
        for (int i = 0; i < budget; i++) {
            try {
                IsoZombie zombie = new IsoZombie(cell);
                double angle = (Math.PI * 2 * i) / budget;
                zombie.setX((float) (player.getX() + Math.cos(angle) * (4 + i % 5)));
                zombie.setY((float) (player.getY() + Math.sin(angle) * (4 + i % 5)));
                zombie.setZ(player.getZ());
                cell.addMovingObject(zombie);
                spawned++;
            } catch (Throwable ignored) {}
        }
        return spawned;
    }
}
