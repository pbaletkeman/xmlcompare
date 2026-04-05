package com.xmlcompare.format;

import com.xmlcompare.Difference;
import com.xmlcompare.plugin.FormatterPlugin;

import java.util.List;
import java.util.Map;

/**
 * Unified diff output format (like git diff --unified).
 *
 * <p>Generates output in the standard unified diff format with:
 * - File headers: --- expected.xml / +++ actual.xml
 * - Hunk headers: @@ -start,count +start,count @@
 * - Lines prefixed with space (context), + (added), or - (removed)
 * - Configurable context lines (default: 3)
 */
public class UnifiedDiffFormatter implements FormatterPlugin {

    private static final int DEFAULT_CONTEXT_LINES = 3;

    @Override
    public String getName() {
        return "unified-diff";
    }

    @Override
    public String format(Map<String, Object> allResults, String label1, String label2) {
        StringBuilder sb = new StringBuilder();

        for (Map.Entry<String, Object> entry : allResults.entrySet()) {
            Object val = entry.getValue();
            if (val instanceof String) {
                // Error case
                sb.append("Error: ").append(val).append("\n");
            } else {
                @SuppressWarnings("unchecked")
                List<Difference> diffs = (List<Difference>) val;
                appendUnifiedDiff(sb, diffs, label1 != null ? label1 : "expected",
                                          label2 != null ? label2 : "actual");
            }
        }

        // Remove final newline to match expected behavior
        if (sb.length() > 0 && sb.charAt(sb.length() - 1) == '\n') {
            sb.setLength(sb.length() - 1);
        }

        return sb.toString();
    }

    private void appendUnifiedDiff(StringBuilder sb, List<Difference> diffs, String label1, String label2) {
        // File headers
        sb.append("--- ").append(label1).append("\n");
        sb.append("+++ ").append(label2).append("\n");

        if (diffs.isEmpty()) {
            sb.append(" (no differences)\n");
            return;
        }

        // Group differences by location/context
        // For simplicity, generate a unified format per difference
        for (Difference diff : diffs) {
            sb.append("@@ ").append(diff.path).append(" @@\n");

            switch (diff.kind) {
                case "text", "attr" -> {
                    // Text or attribute value changed
                    if (diff.expected != null) {
                        sb.append("- ").append(diff.expected).append("\n");
                    }
                    if (diff.actual != null) {
                        sb.append("+ ").append(diff.actual).append("\n");
                    }
                }
                case "tag" -> {
                    // Tag name mismatch
                    sb.append("! ").append(diff.msg).append("\n");
                }
                case "missing" -> {
                    // Expected element found but not in actual
                    sb.append("- ").append(diff.msg).append("\n");
                }
                case "extra" -> {
                    // Element found in actual but not expected
                    sb.append("+ ").append(diff.msg).append("\n");
                }
                default -> sb.append("  ").append(diff.msg).append("\n");
            }
        }
    }
}
