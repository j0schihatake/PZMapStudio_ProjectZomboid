package pzmapstudio.core;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;

/** Terrain-only compiled-cell writer for the Java core. */
public final class PzLotWriter {
    private PzLotWriter() {}

    public static void writeCell(Path folder, int cellX, int cellY,
                                 Map<Long, String> tiles, String fallback) throws IOException {
        Files.createDirectories(folder);
        Set<String> names = new TreeSet<>();
        names.add(fallback);
        names.addAll(tiles.values());
        List<String> ordered = new ArrayList<>(names);
        Map<String, Integer> ids = new HashMap<>();
        for (int i = 0; i < ordered.size(); i++) ids.put(ordered.get(i), i);

        ByteArrayOutputStream header = new ByteArrayOutputStream();
        header.write("LOTH".getBytes(StandardCharsets.US_ASCII));
        header.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(1).array());
        header.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(ordered.size()).array());
        for (String name : ordered) {
            header.write(name.getBytes(StandardCharsets.ISO_8859_1));
            header.write('\n');
        }
        header.write(ByteBuffer.allocate(16).order(ByteOrder.LITTLE_ENDIAN)
                .putInt(8).putInt(8).putInt(0).putInt(0).array());
        header.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(0).array());
        header.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(0).array());
        Files.write(folder.resolve(cellX + "_" + cellY + ".lotheader"), header.toByteArray());

        List<byte[]> chunks = new ArrayList<>(PzLot.CHUNKS * PzLot.CHUNKS);
        for (int cx = 0; cx < PzLot.CHUNKS; cx++) {
            for (int cy = 0; cy < PzLot.CHUNKS; cy++) {
                ByteArrayOutputStream chunk = new ByteArrayOutputStream();
                for (int z = 0; z < 1; z++) {
                    for (int x = 0; x < PzLot.CHUNK; x++) {
                        for (int y = 0; y < PzLot.CHUNK; y++) {
                            int wx = cx * PzLot.CHUNK + x, wy = cy * PzLot.CHUNK + y;
                            String tile = tiles.getOrDefault(key(wx, wy), fallback);
                            int id = ids.getOrDefault(tile, ids.get(fallback));
                            writeInt(chunk, 2);
                            writeInt(chunk, 0);
                            writeInt(chunk, id);
                        }
                    }
                }
                chunks.add(chunk.toByteArray());
            }
        }
        int base = 4 + 4 + 4 + PzLot.CHUNKS * PzLot.CHUNKS * 8;
        long pos = base;
        long[] offsets = new long[PzLot.CHUNKS * PzLot.CHUNKS];
        for (int i = 0; i < chunks.size(); i++) {
            offsets[i] = pos;
            pos += chunks.get(i).length;
        }
        ByteArrayOutputStream pack = new ByteArrayOutputStream();
        pack.write("LOTP".getBytes(StandardCharsets.US_ASCII));
        writeInt(pack, 1);
        writeInt(pack, PzLot.CHUNKS * PzLot.CHUNKS);
        for (long offset : offsets) writeLong(pack, offset);
        for (byte[] chunk : chunks) pack.write(chunk);
        Files.write(folder.resolve("world_" + cellX + "_" + cellY + ".lotpack"), pack.toByteArray());
    }

    private static void writeInt(ByteArrayOutputStream out, int value) {
        out.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(value).array(), 0, 4);
    }

    private static void writeLong(ByteArrayOutputStream out, long value) {
        out.write(ByteBuffer.allocate(8).order(ByteOrder.LITTLE_ENDIAN).putLong(value).array(), 0, 8);
    }

    private static long key(int x, int y) { return ((long) x << 32) ^ (y & 0xffffffffL); }
}
