package com.xmlcompare.cache;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Incremental comparison cache for directory mode.
 *
 * <p>Stores SHA-256 checksums of compared file pairs in a JSON file.
 * On subsequent {@code --dirs} runs, file pairs whose hashes have not changed
 * and were equal last time are skipped, speeding up large directory comparisons.
 */
public class CacheManager {

    private final File cacheFile;
    private final Map<String, CacheEntry> entries = new HashMap<>();
    private static final ObjectMapper MAPPER = new ObjectMapper();

    public CacheManager(String cacheFilePath) {
        this.cacheFile = new File(cacheFilePath);
        load();
    }

    private void load() {
        if (!cacheFile.exists()) {
            return;
        }
        try {
            List<?> arr = MAPPER.readValue(cacheFile, List.class);
            for (Object item : arr) {
                if (item instanceof Map<?, ?> m) {
                    String key = (String) m.get("key");
                    String hash1 = (String) m.get("hash1");
                    String hash2 = (String) m.get("hash2");
                    Boolean equal = (Boolean) m.get("equal");
                    if (key != null) {
                        entries.put(key, new CacheEntry(key, hash1, hash2, Boolean.TRUE.equals(equal)));
                    }
                }
            }
        } catch (Exception ignored) {
            // Corrupt cache is silently ignored; fresh comparison will rebuild it
        }
    }

    /**
     * Persist the cache to disk.
     *
     * @throws IOException if the file cannot be written
     */
    public void save() throws IOException {
        Collection<CacheEntry> values = entries.values();
        MAPPER.writerWithDefaultPrettyPrinter().writeValue(cacheFile, new ArrayList<>(values));
    }

    /**
     * Return {@code true} if both files have the same SHA-256 hashes as the last
     * recorded run and the previous comparison result was equal.
     *
     * @param file1 first file
     * @param file2 second file
     * @return {@code true} if the cached result is still valid and equal
     */
    public boolean isCachedEqual(File file1, File file2) {
        String key = cacheKey(file1, file2);
        CacheEntry entry = entries.get(key);
        if (entry == null || !entry.equal) {
            return false;
        }
        try {
            return entry.hash1.equals(sha256(file1)) && entry.hash2.equals(sha256(file2));
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Record the comparison result for this file pair.
     *
     * @param file1 first file
     * @param file2 second file
     * @param equal {@code true} if the files were equal
     */
    public void update(File file1, File file2, boolean equal) {
        try {
            String key = cacheKey(file1, file2);
            entries.put(key, new CacheEntry(key, sha256(file1), sha256(file2), equal));
        } catch (Exception ignored) {
            // If hashing fails we simply skip the cache update
        }
    }

    private static String cacheKey(File f1, File f2) {
        return f1.getAbsolutePath() + "|" + f2.getAbsolutePath();
    }

    private static String sha256(File file) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        try (InputStream is = Files.newInputStream(file.toPath())) {
            byte[] buf = new byte[65536];
            int n;
            while ((n = is.read(buf)) > 0) {
                digest.update(buf, 0, n);
            }
        }
        byte[] hash = digest.digest();
        StringBuilder sb = new StringBuilder(64);
        for (byte b : hash) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    /** Single cache entry recording file hashes and the last comparison result. */
    public static class CacheEntry {
        public String key;
        public String hash1;
        public String hash2;
        public boolean equal;

        @SuppressWarnings("unused")
        public CacheEntry() {
            // Jackson no-arg constructor
        }

        public CacheEntry(String key, String hash1, String hash2, boolean equal) {
            this.key = key;
            this.hash1 = hash1;
            this.hash2 = hash2;
            this.equal = equal;
        }
    }
}
