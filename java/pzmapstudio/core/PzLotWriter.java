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

    /** Rewrite one existing cell's tile records, preserving its header metadata. */
    public static void rewriteCell(Path source, Path out, int cellX, int cellY,
                                   Map<Long, String> overrides) throws IOException {
        PzLot.Header header = PzLot.readHeader(source.resolve(cellX + "_" + cellY + ".lotheader"));
        List<String> names = new ArrayList<>(header.names());
        for (String tile : overrides.values()) {
            if (!names.contains(tile)) names.add(tile);
        }
        byte[] raw = Files.readAllBytes(source.resolve(cellX + "_" + cellY + ".lotheader"));
        int pos = 4;
        if (raw[0] == 'L' && raw[1] == 'O' && raw[2] == 'T' && raw[3] == 'H') pos = 8;
        int namesStart = pos + 4;
        int cursor = namesStart;
        for (int i = 0; i < header.names().size(); i++) {
            while (raw[cursor] != '\n') cursor++;
            cursor++;
        }
        byte[] tail = Arrays.copyOfRange(raw, cursor, raw.length);
        ByteArrayOutputStream newHeader = new ByteArrayOutputStream();
        newHeader.write(raw, 0, pos);
        writeInt(newHeader, names.size());
        for (String name : names) {
            newHeader.write(name.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
            newHeader.write('\n');
        }
        newHeader.write(tail);
        Files.createDirectories(out);
        Files.write(out.resolve(cellX + "_" + cellY + ".lotheader"), newHeader.toByteArray());

        Map<String, Integer> ids = new HashMap<>();
        for (int i = 0; i < names.size(); i++) ids.put(names.get(i), i);
        Map<Long, PzLot.Square> squares = new HashMap<>();
        for (PzLot.Square square : PzLot.readSquares(source, cellX, cellY, header.high())) {
            long key = ((long) (square.x() - cellX * PzLot.CELL) << 32)
                    ^ ((square.y() - cellY * PzLot.CELL) & 0xffffffffL);
            squares.put(((long) square.z() << 48) ^ key, square);
        }
        List<byte[]> chunks = new ArrayList<>(PzLot.CHUNKS * PzLot.CHUNKS);
        for (int cx = 0; cx < PzLot.CHUNKS; cx++) {
            for (int cy = 0; cy < PzLot.CHUNKS; cy++) {
                ByteArrayOutputStream chunk = new ByteArrayOutputStream();
                int skip = 0;
                for (int z = header.low(); z <= header.high(); z++) {
                    for (int x = 0; x < PzLot.CHUNK; x++) {
                        for (int y = 0; y < PzLot.CHUNK; y++) {
                            long local = ((long) (cx * PzLot.CHUNK + x) << 32)
                                    ^ ((cy * PzLot.CHUNK + y) & 0xffffffffL);
                            PzLot.Square square = squares.get(((long) z << 48) ^ local);
                            if (square == null) { skip++; continue; }
                            if (skip > 0) { writeInt(chunk, -1); writeInt(chunk, skip); skip = 0; }
                            String override = overrides.get(local);
                            List<String> tiles = override != null ? List.of(override) : square.tiles();
                            writeInt(chunk, tiles.size() + 1);
                            writeInt(chunk, square.room());
                            for (String tile : tiles) writeInt(chunk, ids.getOrDefault(tile, ids.get("grass")));
                        }
                    }
                }
                if (skip > 0) { writeInt(chunk, -1); writeInt(chunk, skip); }
                chunks.add(chunk.toByteArray());
            }
        }
        int base = 4 + 4 + 4 + PzLot.CHUNKS * PzLot.CHUNKS * 8;
        long offset = base;
        long[] offsets = new long[PzLot.CHUNKS * PzLot.CHUNKS];
        for (int i = 0; i < chunks.size(); i++) { offsets[i] = offset; offset += chunks.get(i).length; }
        ByteArrayOutputStream pack = new ByteArrayOutputStream();
        pack.write("LOTP".getBytes(java.nio.charset.StandardCharsets.US_ASCII));
        writeInt(pack, 1);
        writeInt(pack, PzLot.CHUNKS * PzLot.CHUNKS);
        for (long off : offsets) writeLong(pack, off);
        for (byte[] chunk : chunks) pack.write(chunk);
        Files.write(out.resolve("world_" + cellX + "_" + cellY + ".lotpack"), pack.toByteArray());
    }
}
