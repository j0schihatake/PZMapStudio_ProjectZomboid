package pzmapstudio.cli;

import pzmapstudio.core.PzLot;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

/** Standalone Java CLI seed for PZMapStudio. */
public final class Main {
    private static final long META_CELL = 8, META_ROOM = 10, META_BUILDING = 23;

    private static void help() {
        System.out.println("""
                PZMapStudio Java core
                  audit <map-folder>   count cells/rooms/buildings and estimate save state
                  info <map-folder>    print per-cell header summary
                  help                 this text
                """);
    }

    private static int audit(Path dir) throws Exception {
        int cells = 0, rooms = 0, buildings = 0;
        try (var stream = Files.list(dir)) {
            List<Path> headers = stream.filter(p -> p.toString().endsWith(".lotheader")).sorted().toList();
            for (Path header : headers) {
                PzLot.Header h = PzLot.readHeader(header);
                cells++;
                rooms += h.rooms().size();
                buildings += h.buildings().size();
            }
        }
        long state = cells * META_CELL + rooms * META_ROOM + buildings * META_BUILDING;
        System.out.printf("cells=%d rooms=%d buildings=%d stateBytes=%d%n", cells, rooms, buildings, state);
        return 0;
    }

    private static int info(Path dir) throws Exception {
        try (var stream = Files.list(dir)) {
            List<Path> headers = stream.filter(p -> p.toString().endsWith(".lotheader")).sorted().toList();
            for (Path header : headers) {
                PzLot.Header h = PzLot.readHeader(header);
                System.out.printf("%s version=%d tiles=%d levels=%d..%d rooms=%d buildings=%d%n",
                        header.getFileName(), h.version(), h.names().size(), h.low(), h.high(),
                        h.rooms().size(), h.buildings().size());
            }
        }
        return 0;
    }

    public static void main(String[] args) throws Exception {
        if (args.length == 0 || args[0].equals("help")) {
            help();
            return;
        }
        Path dir = Path.of(args.length > 1 ? args[1] : ".");
        int code = switch (args[0]) {
            case "audit" -> audit(dir);
            case "info" -> info(dir);
            default -> { help(); yield 2; }
        };
        System.exit(code);
    }
}
