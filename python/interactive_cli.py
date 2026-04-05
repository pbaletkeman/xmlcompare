"""Interactive CLI mode for xmlcompare.

Provides an interactive menu for:
- Selecting files to compare
- Filtering results by type, path, depth
- Viewing detailed differences
- Exporting filtered results
- Performance analysis (streaming/parallel)
"""

from pathlib import Path
from typing import List, Dict, Optional
import json
import time

from xmlcompare import compare_xml_files, Difference, CompareOptions, format_text_report

try:
    from parse_streaming import get_stream_stats
    from parallel import get_parallel_stats
    STREAMING_AVAILABLE = True
    PARALLEL_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False
    PARALLEL_AVAILABLE = False


class InteractiveCli:
    """Interactive command-line interface for XML comparison."""

    def __init__(self):
        self.file1: Optional[str] = None
        self.file2: Optional[str] = None
        self.diffs: List[Difference] = []
        self.filtered_diffs: List[Difference] = []
        self.current_filter: Dict[str, str] = {}
        self.comparison_time: float = 0.0
        self.use_streaming: bool = False
        self.use_parallel: bool = False
        self.diff_index: int = 0  # For navigation

    def run(self) -> None:
        """Start the interactive CLI."""
        print("\n" + "=" * 60)
        print("XML Comparison - Interactive Mode")
        print("=" * 60 + "\n")

        while True:
            if not self.file1 or not self.file2:
                if not self._select_files():
                    return
            else:
                self._main_menu()

    def _select_files(self) -> bool:
        """Prompt user to select files for comparison."""
        print("\nSelect files to compare:")
        print("-" * 40)

        while not self.file1:
            self.file1 = self._prompt_file("File 1")
            if not self.file1:
                return False

        while not self.file2:
            self.file2 = self._prompt_file("File 2")
            if not self.file2:
                return False

        # Perform comparison
        print("\nComparing files...")
        start_time = time.time()

        # Check if streaming is beneficial
        if STREAMING_AVAILABLE:
            try:
                stats = get_stream_stats(self.file1)
                if stats.suitable_for_streaming:
                    print(f"Note: File is {stats.file_size_mb:.1f}MB - streaming recommended")
            except Exception:
                pass

        try:
            opts = CompareOptions()
            opts.stream = self.use_streaming
            opts.parallel = self.use_parallel
            self.diffs = compare_xml_files(self.file1, self.file2, opts)
            self.filtered_diffs = list(self.diffs)
            self.comparison_time = time.time() - start_time

            print(f"✓ Comparison complete in {self.comparison_time:.2f}s")
            print(f"  Found {len(self.diffs)} difference(s)")
            return True
        except Exception as e:
            print(f"Error: {e}")
            self.file1 = None
            self.file2 = None
            return False

    def _prompt_file(self, label: str) -> Optional[str]:
        """Prompt user for a file path."""
        while True:
            path_str = input(f"{label} [or 'q' to quit]: ").strip()
            if path_str.lower() in ('q', 'quit'):
                return None
            if path_str and Path(path_str).exists():
                return str(Path(path_str).resolve())
            print(f"  File not found: {path_str}")

    def _main_menu(self) -> None:
        """Display main menu."""
        print("\n" + "=" * 60)
        print(f"Files: {Path(self.file1).name} vs {Path(self.file2).name}")
        print(f"Differences: {len(self.filtered_diffs)} (filtered from {len(self.diffs)} total)")
        stream_label = "ON" if self.use_streaming else "off"
        parallel_label = "ON" if self.use_parallel else "off"
        print(f"Mode: streaming={stream_label}  parallel={parallel_label}")
        print("=" * 60)
        print("1. View differences")
        print("2. Filter by type")
        print("3. Filter by path")
        print("4. Reset filters")
        print("5. Export results")
        print("6. Toggle streaming mode")
        print("7. Toggle parallel mode")
        print("8. Show statistics")
        print("9. Show performance info")
        print("0. Select new files / Exit")
        print("-" * 60)

        choice = input("Choose option: ").strip()

        if choice == '1':
            self._view_differences()
        elif choice == '2':
            self._filter_by_type()
        elif choice == '3':
            self._filter_by_path()
        elif choice == '4':
            self._reset_filters()
        elif choice == '5':
            self._export_results()
        elif choice == '6':
            self._toggle_streaming()
        elif choice == '7':
            self._toggle_parallel()
        elif choice == '8':
            self._show_statistics()
        elif choice == '9':
            self._show_performance_info()
        elif choice == '0':
            self.file1 = None
            self.file2 = None
            print("\nGoodbye!")
            exit(0)

    def _view_differences(self) -> None:
        """Display filtered differences."""
        if not self.filtered_diffs:
            print("\nNo differences to display.")
            return

        print(f"\n{format_text_report(self.filtered_diffs, self.file1, self.file2)}")

    def _filter_by_type(self) -> None:
        """Filter differences by type."""
        types = set(d.kind for d in self.diffs)
        print(f"\nAvailable difference types: {', '.join(sorted(types))}")
        type_filter = input("Filter by type (or 'all' to reset): ").strip().lower()

        if type_filter == 'all':
            self.filtered_diffs = list(self.diffs)
            self.current_filter['type'] = None
        elif type_filter in types:
            self.filtered_diffs = [d for d in self.diffs if d.kind == type_filter]
            self.current_filter['type'] = type_filter
            print(f"Filtered to {len(self.filtered_diffs)} differences of type '{type_filter}'")
        elif type_filter:
            print(f"Invalid type: {type_filter}")

    def _filter_by_path(self) -> None:
        """Filter differences by path substring."""
        path_filter = input("Filter by path (substring match, or 'all' to reset): ").strip()

        if path_filter.lower() == 'all':
            self.filtered_diffs = list(self.diffs)
            self.current_filter['path'] = None
        elif path_filter:
            self.filtered_diffs = [d for d in self.diffs if path_filter.lower() in d.path.lower()]
            self.current_filter['path'] = path_filter
            print(f"Filtered to {len(self.filtered_diffs)} differences matching path '{path_filter}'")
        else:
            print("No filter specified")

    def _reset_filters(self) -> None:
        """Reset all filters."""
        self.filtered_diffs = list(self.diffs)
        self.current_filter = {}
        print(f"Filters reset. Showing all {len(self.filtered_diffs)} differences.")

    def _toggle_streaming(self) -> None:
        """Toggle streaming parser mode and re-run comparison."""
        self.use_streaming = not self.use_streaming
        status = "enabled" if self.use_streaming else "disabled"
        print(f"\nStreaming mode {status}.")
        if self.use_streaming and self.use_parallel:
            print("  Note: streaming and parallel both active.")
        # Re-run comparison with new mode
        self._rerun_comparison()

    def _toggle_parallel(self) -> None:
        """Toggle parallel processing mode and re-run comparison."""
        self.use_parallel = not self.use_parallel
        status = "enabled" if self.use_parallel else "disabled"
        print(f"\nParallel mode {status}.")
        self._rerun_comparison()

    def _rerun_comparison(self) -> None:
        """Re-run comparison with current mode settings."""
        if not self.file1 or not self.file2:
            return
        print("Re-running comparison...")
        import time
        start_time = time.time()
        try:
            opts = CompareOptions()
            opts.stream = self.use_streaming
            opts.parallel = self.use_parallel
            if self.use_streaming:
                from parse_streaming import compare_xml_files_streaming
                self.diffs = compare_xml_files_streaming(self.file1, self.file2, opts)
            elif self.use_parallel:
                from parallel import compare_xml_files_parallel
                self.diffs = compare_xml_files_parallel(self.file1, self.file2, opts)
            else:
                self.diffs = compare_xml_files(self.file1, self.file2, opts)
            self.filtered_diffs = list(self.diffs)
            elapsed = time.time() - start_time
            print(f"✓ Done in {elapsed:.2f}s — {len(self.diffs)} difference(s)")
        except Exception as exc:
            print(f"Error: {exc}")

    def _export_results(self) -> None:
        """Export filtered results to file."""
        print("\nExport format:")
        print("1. Text (default)")
        print("2. JSON")
        fmt = input("Choose format [1-2]: ").strip() or '1'

        filename = input("Output filename (without extension): ").strip() or "comparison_results"

        if fmt == '2':
            self._export_json(filename)
        else:
            self._export_text(filename)

    def _show_statistics(self) -> None:
        """Show difference statistics broken down by kind."""
        if not self.diffs:
            print("\nNo differences to analyze.")
            return

        print("\nDifference Statistics:")
        print("-" * 60)
        type_counts: Dict[str, int] = {}
        for d in self.diffs:
            type_counts[d.kind] = type_counts.get(d.kind, 0) + 1
        for kind, count in sorted(type_counts.items()):
            pct = (count / len(self.diffs)) * 100
            print(f"  {kind:20s}: {count:4d}  ({pct:5.1f}%)")
        print(f"  {'Total':20s}: {len(self.diffs):4d}  (100.0%)")
        print(f"\nComparison time: {self.comparison_time:.3f}s")

    def _show_performance_info(self) -> None:
        """Show streaming and parallel performance diagnostics."""
        print("\nPerformance Information:")
        print("-" * 60)
        if STREAMING_AVAILABLE and self.file1:
            try:
                stats = get_stream_stats(self.file1)
                print(f"  File 1 streaming analysis: {stats}")
            except Exception:
                pass
        if PARALLEL_AVAILABLE:
            try:
                pstats = get_parallel_stats()
                print(f"  Parallel processing:       {pstats}")
            except Exception:
                pass
        mode = []
        if self.use_streaming:
            mode.append("streaming")
        if self.use_parallel:
            mode.append("parallel")
        print(f"  Current mode:              {', '.join(mode) or 'standard DOM'}")

    def _export_text(self, basename: str) -> None:
        """Export results as text."""
        filename = f"{basename}.txt"
        content = format_text_report(self.filtered_diffs, self.file1, self.file2)
        Path(filename).write_text(content)
        print(f"Exported {len(self.filtered_diffs)} differences to {filename}")

    def _export_json(self, basename: str) -> None:
        """Export results as JSON."""
        filename = f"{basename}.json"
        data = {
            "file1": self.file1,
            "file2": self.file2,
            "total_differences": len(self.diffs),
            "filtered_count": len(self.filtered_diffs),
            "filters": self.current_filter,
            "differences": [
                {
                    "path": d.path,
                    "kind": d.kind,
                    "msg": d.msg,
                    "expected": d.expected,
                    "actual": d.actual,
                }
                for d in self.filtered_diffs
            ],
        }
        Path(filename).write_text(json.dumps(data, indent=2))
        print(f"Exported {len(self.filtered_diffs)} differences to {filename}")


def run_interactive():
    """Entry point for interactive CLI."""
    cli = InteractiveCli()
    cli.run()


if __name__ == "__main__":
    run_interactive()
