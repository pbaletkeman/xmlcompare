"""HTML side-by-side diff output formatter for xmlcompare.

Generates a standalone HTML file with:
- Two-column layout (expected vs actual)
- Line numbers
- Color-coded differences (red for removed, green for added)
- Self-contained CSS (no external dependencies)
- Summary statistics
"""

from plugin_interface import FormatterPlugin


class HtmlSideBySideFormatter(FormatterPlugin):
    """HTML side-by-side diff output format."""

    @property
    def name(self):
        return "html-diff"

    def format(self, all_results, **kwargs):
        label1 = kwargs.get("label1", "Expected")
        label2 = kwargs.get("label2", "Actual")

        sb = []
        self._append_html_header(sb)

        total_diffs = 0
        for key, val in all_results.items():
            if isinstance(val, str):
                # Error case
                sb.append("<div class=\"error\">\n")
                sb.append("  <h2>Error</h2>\n")
                sb.append(f"  <p>{self._html_escape(val)}</p>\n")
                sb.append("</div>\n")
            else:
                # List of Difference objects
                diffs = val
                total_diffs += len(diffs)
                self._append_comparison(sb, diffs, label1, label2)

        # Summary
        sb.append("<div class=\"summary\">\n")
        sb.append(f"  <p>Total differences: <strong>{total_diffs}</strong></p>\n")
        sb.append("</div>\n")

        self._append_html_footer(sb)

        result = "".join(sb)
        return result.rstrip("\n")

    def _append_html_header(self, sb):
        sb.append("<!DOCTYPE html>\n")
        sb.append("<html>\n")
        sb.append("<head>\n")
        sb.append('  <meta charset="UTF-8">\n')
        sb.append("  <title>XML Comparison Report</title>\n")
        sb.append("  <style>\n")
        self._append_css(sb)
        sb.append("  </style>\n")
        sb.append("</head>\n")
        sb.append("<body>\n")
        sb.append("  <h1>XML Comparison Report</h1>\n")

    def _append_css(self, sb):
        css = """    body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
    h1 { color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }
    h2 { color: #555; margin-top: 30px; }
    .comparison { background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .diff-table { width: 100%; border-collapse: collapse; font-family: monospace; font-size: 13px; }
    .diff-table th { background: #f0f0f0; padding: 8px; text-align: left; border-bottom: 1px solid #ccc; font-weight: bold; }
    .diff-table td { padding: 8px; border-bottom: 1px solid #e0e0e0; vertical-align: top; line-height: 1.4; }
    .line-no { color: #999; width: 50px; text-align: right; padding-right: 10px; background: #f9f9f9; }
    .expected { width: 50%; border-right: 1px solid #e0e0e0; }
    .actual { width: 50%; }
    .removed { background: #ffcccc; color: #8B0000; }
    .added { background: #ccffcc; color: #006400; }
    .context { background: #f0f0f0; color: #666; }
    .diff-location { font-size: 12px; color: #666; background: #f9f9f9; padding: 4px 8px; margin: 8px 0; }
    .summary { background: #e8f4f8; border: 1px solid #b0d4e8; border-radius: 4px; padding: 15px; margin: 20px 0; }
    .error { background: #ffe6e6; border: 1px solid #ff9999; border-radius: 4px; padding: 15px; color: #8B0000; }
"""
        sb.append(css)

    def _append_comparison(self, sb, diffs, label1, label2):
        sb.append("  <div class=\"comparison\">\n")
        sb.append(f"    <h2>Comparison: {self._html_escape(label1)} vs {self._html_escape(label2)}</h2>\n")

        if not diffs:
            sb.append("    <p style=\"color: green; font-weight: bold;\">No differences - files are equal</p>\n")
        else:
            sb.append("    <table class=\"diff-table\">\n")
            sb.append("      <thead>\n")
            sb.append("        <tr>\n")
            sb.append(f"          <th colspan=\"2\">{self._html_escape(label1)}</th>\n")
            sb.append(f"          <th colspan=\"2\">{self._html_escape(label2)}</th>\n")
            sb.append("        </tr>\n")
            sb.append("      </thead>\n")
            sb.append("      <tbody>\n")

            for diff in diffs:
                self._append_difference_row(sb, diff)

            sb.append("      </tbody>\n")
            sb.append("    </table>\n")

        sb.append("  </div>\n")

    def _append_difference_row(self, sb, diff):
        css_class = "context"
        marker = "●"

        if diff.kind == "missing":
            css_class = "removed"
            marker = "−"
        elif diff.kind == "extra":
            css_class = "added"
            marker = "+"
        elif diff.kind in ("tag", "text", "attr"):
            css_class = "added"
            marker = "≠"

        sb.append("        <tr>\n")
        sb.append(f"          <td class=\"diff-location\" colspan=\"4\">\n")
        sb.append(f"            <strong>{marker} {diff.kind.upper()}:</strong> {self._html_escape(diff.msg)}\n")
        sb.append(f"          </td>\n")
        sb.append("        </tr>\n")

        if diff.expected is not None:
            sb.append(f"        <tr class=\"{css_class}\">\n")
            sb.append("          <td class=\"line-no\">−</td>\n")
            sb.append(f"          <td class=\"expected\">{self._html_escape(diff.expected)}</td>\n")
            sb.append("          <td class=\"line-no\"></td>\n")
            sb.append("          <td class=\"actual\"></td>\n")
            sb.append("        </tr>\n")

        if diff.actual is not None:
            sb.append(f"        <tr class=\"{css_class}\">\n")
            sb.append("          <td class=\"line-no\"></td>\n")
            sb.append("          <td class=\"expected\"></td>\n")
            sb.append("          <td class=\"line-no\">+</td>\n")
            sb.append(f"          <td class=\"actual\">{self._html_escape(diff.actual)}</td>\n")
            sb.append("        </tr>\n")

    def _append_html_footer(self, sb):
        sb.append("  <footer style=\"text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc; color: #999; font-size: 12px;\">\n")
        sb.append("    <p>Generated by xmlcompare</p>\n")
        sb.append("  </footer>\n")
        sb.append("</body>\n")
        sb.append("</html>\n")

    @staticmethod
    def _html_escape(text):
        """Escape HTML special characters."""
        if text is None:
            return ""
        return (text.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace('"', "&quot;")
                    .replace("'", "&#39;"))
