package pzmapstudio.core;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/** Reader for compiled Project Zomboid .lotheader/.lotpack cells. */
public final class PzLot {
    public static final int CELL = 256;
    public static final int CHUNKS = 32;
    public static final int CHUNK = 8;

    public record Room(String name, int level, List<int[]> rects) {}
    public record Building(List<Integer> roomIds) {}
    public record Header(int version, List<String> names, int chunkWidth, int chunkHeight,
                         int low, int high, List<Room> rooms, List<Building> buildings) {}
    public record Square(int x, int y, int z, int room, List<String> tiles) {}

    private PzLot() {}

    private static String name(ByteBuffer buf) {
        var out = new java.io.ByteArrayOutputStream();
        while (buf.hasRemaining()) {
            byte b = buf.get();
            if (b == '\n') break;
            out.write(b);
        }
        return out.toString(StandardCharsets.ISO_8859_1);
    }

    public static Header readHeader(Path path) throws IOException {
        ByteBuffer buf = ByteBuffer.wrap(Files.readAllBytes(path)).order(ByteOrder.LITTLE_ENDIAN);
        int version = 1;
        if (buf.get(0) == 'L' && buf.get(1) == 'O' && buf.get(2) == 'T' && buf.get(3) == 'H') {
            version = buf.getInt(4);
            buf.position(8);
        } else {
            buf.position(4);
        }
        int count = buf.getInt();
        List<String> names = new ArrayList<>(count);
        for (int i = 0; i < count; i++) names.add(name(buf));
        int cw = buf.getInt(), ch = buf.getInt(), low = buf.getInt(), high = buf.getInt();
        int nrooms = buf.getInt();
        List<Room> rooms = new ArrayList<>(nrooms);
        for (int i = 0; i < nrooms; i++) {
            String roomName = name(buf);
            int level = buf.getInt();
            int nrects = buf.getInt();
            List<int[]> rects = new ArrayList<>(nrects);
            for (int r = 0; r < nrects; r++) {
                rects.add(new int[]{buf.getInt(), buf.getInt(), buf.getInt(), buf.getInt()});
            }
            int objects = buf.getInt();
            buf.position(buf.position() + objects * 12);
            rooms.add(new Room(roomName, level, rects));
        }
        int nbuildings = buf.getInt();
        List<Building> buildings = new ArrayList<>(nbuildings);
        for (int i = 0; i < nbuildings; i++) {
            int n = buf.getInt();
            List<Integer> ids = new ArrayList<>(n);
            for (int r = 0; r < n; r++) ids.add(buf.getInt());
            buildings.add(new Building(ids));
        }
        return new Header(version, names, cw, ch, low, high, rooms, buildings);
    }

    public static List<Square> readSquares(Path folder, int cellX, int cellY, int maxLevel)
            throws IOException {
        Header header = readHeader(folder.resolve(cellX + "_" + cellY + ".lotheader"));
        ByteBuffer buf = ByteBuffer.wrap(
                Files.readAllBytes(folder.resolve("world_" + cellX + "_" + cellY + ".lotpack")))
                .order(ByteOrder.LITTLE_ENDIAN);
        int pos = 4;
        if (buf.get(0) == 'L' && buf.get(1) == 'O' && buf.get(2) == 'T' && buf.get(3) == 'P') {
            pos = 8;
        }
        buf.position(pos);
        int n = buf.getInt();
        long[] offsets = new long[n];
        for (int i = 0; i < n; i++) offsets[i] = buf.getLong();
        List<Square> result = new ArrayList<>();
        int high = Math.min(header.high(), maxLevel);
        for (int cx = 0; cx < CHUNKS; cx++) {
            for (int cy = 0; cy < CHUNKS; cy++) {
                long offset = offsets[cx * CHUNKS + cy];
                if (offset < 0) continue;
                buf.position((int) offset);
                int bx = cx * CHUNK, by = cy * CHUNK;
                int skip = 0;
                for (int z = header.low(); z <= high; z++) {
                    for (int x = 0; x < CHUNK; x++) {
                        for (int y = 0; y < CHUNK; y++) {
                            if (skip > 0) { skip--; continue; }
                            int count = buf.getInt();
                            if (count == -1) {
                                skip = buf.getInt() - 1;
                                continue;
                            }
                            int room = buf.getInt();
                            List<String> tiles = new ArrayList<>(Math.max(0, count - 1));
                            for (int t = 0; t < count - 1; t++) {
                                int id = buf.getInt();
                                if (id >= 0 && id < header.names().size()) tiles.add(header.names().get(id));
                            }
                            if (!tiles.isEmpty()) {
                                result.add(new Square(cellX * CELL + bx + x,
                                        cellY * CELL + by + y, z, room, tiles));
                            }
                        }
                    }
                }
            }
        }
        return result;
    }
}
