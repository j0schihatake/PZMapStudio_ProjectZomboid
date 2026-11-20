package pzmapstudio.mod;

import zombie.characters.IsoPlayer;
import zombie.characters.IsoZombie;
import zombie.iso.IsoWorld;

/** Small live-incident bridge; budgeted and player-relative. */
public final class Live {
    private Live() {}

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
