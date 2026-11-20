import java.io.*;
import java.nio.*;
import java.nio.file.*;
import java.util.*;

/** Minimal Java seed for the in-game/standalone PZMapStudio core. */
public final class PZMapInfo {
    private static String readName(ByteBuffer buf) {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        while (buf.hasRemaining()) {
            byte b = buf.get();
            if (b == '\n') break;
            out.write(b);
        }
        return out.toString(java.nio.charset.StandardCharsets.ISO_8859_1);
    }

    private static void info(Path header) throws IOException {
        ByteBuffer buf = ByteBuffer.wrap(Files.readAllBytes(header)).order(ByteOrder.LITTLE_ENDIAN);
        int version = 1;
        if (buf.get(0) == 'L' && buf.get(1) == 'O' && buf.get(2) == 'T' && buf.get(3) == 'H') {
            buf.position(4); version = buf.getInt(); buf.position(8);
        } else {
            buf.position(4);
        }
        int count = buf.getInt();
        for (int i = 0; i < count; i++) readName(buf);
        int cw = buf.getInt(), ch = buf.getInt(), lo = buf.getInt(), hi = buf.getInt();
        System.out.printf("%s version=%d tiles=%d chunk=%dx%d levels=%d..%d%n",
                header.getFileName(), version, count, cw, ch, lo, hi);
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 1) {
            System.err.println("usage: PZMapInfo <map-folder>");
            System.exit(2);
        }
        Path dir = Path.of(args[0]);
        List<Path> headers;
        try (var stream = Files.list(dir)) {
            headers = stream.filter(p -> p.toString().endsWith(".lotheader")).sorted().toList();
        }
        for (Path header : headers) info(header);
        System.out.println("cells=" + headers.size());
    }
}
