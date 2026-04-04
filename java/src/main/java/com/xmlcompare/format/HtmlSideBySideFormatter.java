package com.xmlcompare.format;

import com.xmlcompare.Difference;
import com.xmlcompare.plugin.FormatterPlugin;

import java.util.List;
import java.util.Map;

/**
 * HTML side-by-side diff output format.
 *
 * <p>Generates a standalone HTML file with:
 * - Two-column layout (expected vs actual)
 * - Line numbers
 * - Color-coded differences (red for removed, green for added)
 * - Self-contained CSS (no external dependencies)
 * - Summary statistics
 */
public class HtmlSideBySideFormatter implements FormatterPlugin {

    @Override
    public String getName() {
        return "html-diff";
    }

    @Override
    public String format(Map<String, Object> allResults, String label1, String label2) {
        StringBuilder sb = new StringBuilder();

        appendHtmlHeader(sb);

        int totalDiffs = 0;
        for (Map.Entry<String, Object> entry : allResults.entrySet()) {
            Object val = entry.getValue();
            if (val instanceof String) {
                // Error case
                sb.append("<div class=\"error\">\n");
                sb.append("  <h2>Error</h2>\n");
                sb.append("  <p>").append(htmlEscape((String) val)).append("</p>\n");
                sb.append("</div>\n");
            } else {
                @SuppressWarnings("unchecked")
                List<Difference> diffs = (List<Difference>) val;
                totalDiffs += diffs.size();
                appendComparison(sb, diffs, label1 != null ? label1 : "Expected",
                                           label2 != null ? label2 : "Actual");
            }
        }

        // Summary
        sb.append("<div class=\"summary\">\n");
        sb.append("  <p>Total differences: <strong>").append(totalDiffs).append("</strong></p>\n");
        sb.append("</div>\n");

        appendHtmlFooter(sb);

        return sb.toString();
    }

    private void appendHtmlHeader(StringBuilder sb) {
        sb.append("<!DOCTYPE html>\n");
        sb.append("<html>\n");
        sb.append("<head>\n");
        sb.append("  <meta charset=\"UTF-8\">\n");
        sb.append("  <title>XML Comparison Report</title>\n");
        sb.append("  <style>\n");
        appendCss(sb);
        sb.append("  </style>\n");
        sb.append("</head>\n");
        sb.append("<body>\n");
        sb.append("  <h1>XML Comparison Report</h1>\n");
    }

    private void appendCss(StringBuilder sb) {
        sb.append("    body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }\n");
        sb.append("    h1 { color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }\n");
        sb.append("    h2 { color: #555; margin-top: 30px; }\n");
        sb.append("    .comparison { background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }\n");
        sb.append("    .diff-table { width: 100%; border-collapse: collapse; font-family: monospace; font-size: 13px; }\n");
        sb.append("    .diff-table th { background: #f0f0f0; padding: 8px; text-align: left; border-bottom: 1px solid #ccc; font-weight: bold; }\n");
        sb.append("    .diff-table td { padding: 8px; border-bottom: 1px solid #e0e0e0; vertical-align: top; line-height: 1.4; }\n");
        sb.append("    .line-no { color: #999; width: 50px; text-align: right; padding-right: 10px; background: #f9f9f9; }\n");
        sb.append("    .expected { width: 50%; border-right: 1px solid #e0e0e0; }\n");
        sb.append("    .actual { width: 50%; }\n");
        sb.append("    .removed { background: #ffcccc; color: #8B0000; }\n");
        sb.append("    .added { background: #ccffcc; color: #006400; }\n");
        sb.append("    .context { background: #f0f0f0; color: #666; }\n");
        sb.append("    .diff-location { font-size: 12px; color: #666; background: #f9f9f9; padding: 4px 8px; margin: 8px 0; }\n");
        sb.append("    .summary { background: #e8f4f8; border: 1px solid #b0d4e8; border-radius: 4px; padding: 15px; margin: 20px 0; }\n");
        sb.append("    .error { background: #ffe6e6; border: 1px solid #ff9999; border-radius: 4px; padding: 15px; color: #8B0000; }\n");
    }

    private void appendComparison(StringBuilder sb, List<Difference> diffs, String label1, String label2) {
        sb.append("  <div class=\"comparison\">\n");
        sb.append("    <h2>Comparison: ").append(htmlEscape(label1)).append(" vs ").append(htmlEscape(label2)).append("</h2>\n");

        if (diffs.isEmpty()) {
            sb.append("    <p style=\"color: green; font-weight: bold;\">No differences - files are equal</p>\n");
        } else {
            sb.append("    <table class=\"diff-table\">\n");
            sb.append("      <thead>\n");
            sb.append("        <tr>\n");
            sb.append("          <th colspan=\"2\">").append(htmlEscape(label1)).append("</th>\n");
            sb.append("          <th colspan=\"2\">").append(htmlEscape(label2)).append("</th>\n");
            sb.append("        </tr>\n");
            sb.append("      </thead>\n");
            sb.append("      <tbody>\n");

            for (Difference diff : diffs) {
                appendDifferenceRow(sb, diff);
            }

            sb.append("      </tbody>\n");
            sb.append("    </table>\n");
        }

        sb.append("  </div>\n");
    }

    private void appendDifferenceRow(StringBuilder sb, Difference diff) {
        String cssClass = "context";
        String marker = "●";

        switch (diff.kind) {
            case "missing" -> {
                cssClass = "removed";
                marker = "−";
            }
            case "extra" -> {
                cssClass = "added";
                marker = "+";
            }
            case "tag", "text", "attr" -> {
                cssClass = "added";
                marker = "≠";
            }
        }

        sb.append("        <tr>\n");
        sb.append("          <td class=\"diff-location\" colspan=\"4\"><strong>").append(marker).append(" ").append(diff.kind.toUpperCase()).append(":</strong> ").append(htmlEscape(diff.msg)).append("</td>\n");
        sb.append("        </tr>\n");

        if (diff.expected != null) {
            sb.append("        <tr class=\"").append(cssClass).append("\">\n");
            sb.append("          <td class=\"line-no\">−</td>\n");
            sb.append("          <td class=\"expected\">").append(htmlEscape(diff.expected)).append("</td>\n");
            sb.append("          <td class=\"line-no\"></td>\n");
            sb.append("          <td class=\"actual\"></td>\n");
            sb.append("        </tr>\n");
        }

        if (diff.actual != null) {
            sb.append("        <tr class=\"").append(cssClass).append("\">\n");
            sb.append("          <td class=\"line-no\"></td>\n");
            sb.append("          <td class=\"expected\"></td>\n");
            sb.append("          <td class=\"line-no\">+</td>\n");
            sb.append("          <td class=\"actual\">").append(htmlEscape(diff.actual)).append("</td>\n");
            sb.append("        </tr>\n");
        }
    }

    private void appendHtmlFooter(StringBuilder sb) {
        sb.append("  <footer style=\"text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc; color: #999; font-size: 12px;\">\n");
        sb.append("    <p>Generated by xmlcompare</p>\n");
        sb.append("  </footer>\n");
        sb.append("</body>\n");
        sb.append("</html>\n");
    }

    private String htmlEscape(String text) {
        if (text == null) return "";
        return text.replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;")
                   .replace("\"", "&quot;")
                   .replace("'", "&#39;");
    }
}
