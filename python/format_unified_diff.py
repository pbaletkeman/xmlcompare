"""Unified diff output formatter for xmlcompare.

Generates output in the standard unified diff format with:
- File headers: --- expected.xml / +++ actual.xml
- Hunk headers: @@ location @@
- Lines prefixed with space (context), + (added), or - (removed)
"""

from plugin_interface import FormatterPlugin


class UnifiedDiffFormatter(FormatterPlugin):
    """Unified diff output format (like git diff --unified)."""

    @property
    def name(self):
        return "unified-diff"

    def format(self, all_results, **kwargs):
        label1 = kwargs.get("label1", "expected")
        label2 = kwargs.get("label2", "actual")

        parts = []

        for key, val in all_results.items():
            if isinstance(val, str):
                # Error case
                parts.append(f"Error: {val}\n")
            else:
                # List of Difference objects
                diffs = val
                parts.append(self._format_diffs(diffs, label1, label2))

        result = "".join(parts)
        # Remove final newline to match expected behavior
        return result.rstrip("\n")

    def _format_diffs(self, diffs, label1, label2):
        """Format a list of differences in unified diff style."""
        sb = []

        # File headers
        sb.append(f"--- {label1}\n")
        sb.append(f"+++ {label2}\n")

        if not diffs:
            sb.append(" (no differences)\n")
            return "".join(sb)

        # Group differences by location/context
        for diff in diffs:
            sb.append(f"@@ {diff.path} @@\n")

            if diff.kind in ("text", "attr"):
                # Text or attribute value changed
                if diff.expected is not None:
                    sb.append(f"- {diff.expected}\n")
                if diff.actual is not None:
                    sb.append(f"+ {diff.actual}\n")
            elif diff.kind == "tag":
                # Tag name mismatch
                sb.append(f"! {diff.msg}\n")
            elif diff.kind == "missing":
                # Expected element found but not in actual
                sb.append(f"- {diff.msg}\n")
            elif diff.kind == "extra":
                # Element found in actual but not expected
                sb.append(f"+ {diff.msg}\n")
            else:
                sb.append(f"  {diff.msg}\n")

        return "".join(sb)
