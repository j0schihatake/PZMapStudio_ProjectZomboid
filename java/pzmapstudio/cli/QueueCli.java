package pzmapstudio.cli;

import pzmapstudio.mod.AgentQueue;

/** Headless smoke test for the live command queue. */
public final class QueueCli {
    public static void main(String[] args) throws Exception {
        var dir = java.nio.file.Path.of("java", "queue-test");
        System.setProperty("pzmapstudio.queueDir", dir.toString());
        java.nio.file.Files.createDirectories(dir);
        java.nio.file.Files.writeString(dir.resolve("queue.jsonl"),
                "{\"op\":\"observe\"}\n");
        String response = AgentQueue.poll();
        System.out.println(response);
        System.out.println("responses=" + java.nio.file.Files.readString(dir.resolve("responses.jsonl")));
    }
}
