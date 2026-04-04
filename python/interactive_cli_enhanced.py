"""Enhanced interactive CLI mode for xmlcompare with performance features."""

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
    """Enhanced interactive command-line interface for XML comparison."""

    def __init__(self):
        self.file1: Optional[str] = None
        self.file2: Optional[str] = None
        self.diffs: List[Difference] = []
        self.filtered_diffs: List[Difference] = []
        self.current_filter: Dict = {}
        self.comparison_time: float = 0.0
        self.use_streaming: bool = False
        self.use_parallel: bool = False

    def run(self) -> None:
        """Start interactive CLI."""
        print("\n" + "=" * 70)
        print(" " * 20 + "XML Comparison - Interactive Mode")
        print("=" * 70)

        while True:
            if not self.file1 or not self.file2:
                if not self._select_files():
                    return
            else:
                self._main_menu()

    def _select_files(self) -> bool:
        """Select files to compare."""
        print("\n📁 Select files to compare:")
        print("-" * 70)

        while not self.file1:
            self.file1 = self._prompt_file("File 1")
            if not self.file1:
                return False

        while not self.file2:
            self.file2 = self._prompt_file("File 2")
            if not self.file2:
                return False

        # Check file sizes and suggest streaming
        if STREAMING_AVAILABLE:
            try:
                stats1 = get_stream_stats(self.file1)
                stats2 = get_stream_stats(self.file2)
                if stats1.suitable_for_streaming or stats2.suitable_for_streaming:
                    print(f"\n💡 Large files detected:")
                    print(f"   File 1: {stats1.file_size_mb:.1f}MB")
                    print(f"   File 2: {stats2.file_size_mb:.1f}MB")
                    print(f"   Streaming mode recommended for memory efficiency")
            except Exception:
                pass

        # Perform comparison
        print("\n⏳ Comparing files...")
        start_time = time.time()

        try:
            opts = CompareOptions()
            if hasattr(opts, 'streaming'):
                opts.streaming = self.use_streaming
            if hasattr(opts, 'parallel'):
                opts.parallel = self.use_parallel

            self.diffs = compare_xml_files(self.file1, self.file2, opts)
            self.filtered_diffs = list(self.diffs)
            self.comparison_time = time.time() - start_time

            print(f"✓ Comparison complete in {self.comparison_time:.3f}s")
            print(f"  Found {len(self.diffs)} difference(s)")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            self.file1 = None
            self.file2 = None
            return False

    def _prompt_file(self, label: str) -> Optional[str]:
        """Prompt for file path."""
        while True:
            path_str = input(f"  {label} [or 'q' to quit]: ").strip()
            if path_str.lower() in ('q', 'quit'):
                return None
            if path_str and Path(path_str).exists():
                return str(Path(path_str).resolve())
            print(f"  ❌ File not found: {path_str}")

    def _main_menu(self) -> None:
        """Display main menu."""
        print("\n" + "=" * 70)
        print(f"📊 Comparison Summary")
        print("=" * 70)
        print(f"  File 1: {Path(self.file1).name}")
        print(f"  File 2: {Path(self.file2).name}")
        print(f"  Time: {self.comparison_time:.3f}s | Differences: {len(self.diffs)} total")
        print(f"  Shown: {len(self.filtered_diffs)} | Mode: {self._get_mode()}")
        print("-" * 70)
        print("\n📋 Menu Options:")
        print("  1. View differences      4. Reset filters         7. Statistics")
        print("  2. Filter by type        5. Export results        8. Reselect files")
        print("  3. Filter by path        6. Performance info      0. Quit")
        print()

        choice = input("Choose option [0-8]: ").strip()

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
            self._show_performance_info()
        elif choice == '7':
            self._show_statistics()
        elif choice == '8':
            self.file1 = None
            self.file2 = None
        elif choice == '0':
            print("\n👋 Goodbye!")
            exit(0)

    def _get_mode(self) -> str:
        """Get current mode description."""
        modes = []
        if self.use_streaming:
            modes.append("Streaming")
        if self.use_parallel:
            modes.append("Parallel")
        if not modes:
            modes.append("Standard")
        return " + ".join(modes)

    def _view_differences(self) -> None:
        """View filtered differences."""
        if not self.filtered_diffs:
            print("\n❌ No differences to display.")
            return

        print(f"\n📝 Showing {len(self.filtered_diffs)} difference(s):")
        print("-" * 70)
        print(format_text_report(self.filtered_diffs, self.file1, self.file2))

    def _filter_by_type(self) -> None:
        """Filter by difference type."""
        diff_types = sorted(set(d.kind for d in self.diffs))
        print(f"\n🔍 Available types: {', '.join(diff_types)}")

        type_filter = input("Filter by type (or 'all' to reset): ").strip().lower()

        if type_filter == 'all':
            self.filtered_diffs = list(self.diffs)
            self.current_filter['type'] = None
            print(f"✓ Showing all {len(self.filtered_diffs)} differences")
        elif type_filter in diff_types:
            self.filtered_diffs = [d for d in self.diffs if d.kind == type_filter]
            self.current_filter['type'] = type_filter
            print(f"✓ Filtered to {len(self.filtered_diffs)} {type_filter} difference(s)")
        elif type_filter:
            print(f"❌ Unknown type: {type_filter}")

    def _filter_by_path(self) -> None:
        """Filter by path pattern."""
        path_filter = input("Filter by path (substring, or 'all' to reset): ").strip()

        if path_filter.lower() == 'all':
            self.filtered_diffs = list(self.diffs)
            self.current_filter['path'] = None
            print(f"✓ Showing all {len(self.filtered_diffs)} differences")
        elif path_filter:
            self.filtered_diffs = [d for d in self.diffs
                                   if path_filter.lower() in d.path.lower()]
            self.current_filter['path'] = path_filter
            print(f"✓ Filtered to {len(self.filtered_diffs)} difference(s)")
        else:
            print("❌ No filter specified")

    def _reset_filters(self) -> None:
        """Reset all filters."""
        self.filtered_diffs = list(self.diffs)
        self.current_filter = {}
        print(f"✓ Filters reset. Showing all {len(self.filtered_diffs)} differences")

    def _export_results(self) -> None:
        """Export results."""
        print("\n💾 Export format:")
        print("  1. Text")
        print("  2. JSON")
        fmt = input("Choose [1-2]: ").strip() or '1'

        filename = input("Output filename (without extension): ").strip()
        filename = filename or "comparison_results"

        if fmt == '2':
            self._export_json(filename)
        else:
            self._export_text(filename)

    def _export_text(self, basename: str) -> None:
        """Export as text."""
        filename = f"{basename}.txt"
        content = format_text_report(self.filtered_diffs, self.file1, self.file2)
        Path(filename).write_text(content)
        print(f"✓ Exported {len(self.filtered_diffs)} differences to {filename}")

    def _export_json(self, basename: str) -> None:
        """Export as JSON."""
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
                }
                for d in self.filtered_diffs
            ],
        }
        Path(filename).write_text(json.dumps(data, indent=2))
        print(f"✓ Exported {len(self.filtered_diffs)} differences to {filename}")

    def _show_performance_info(self) -> None:
        """Show performance information."""
        print("\n⚙️ Performance Information:")
        print("-" * 70)

        if STREAMING_AVAILABLE:
            try:
                stats1 = get_stream_stats(self.file1)
                print(f"File 1 Streaming Analysis: {stats1}")
            except Exception:
                pass

        if PARALLEL_AVAILABLE:
            try:
                pstats = get_parallel_stats()
                print(f"Parallel Processing: {pstats}")
            except Exception:
                pass

        print(f"Current Mode: {self._get_mode()}")

    def _show_statistics(self) -> None:
        """Show difference statistics."""
        if not self.diffs:
            print("\n📊 No differences to analyze")
            return

        print("\n📊 Difference Statistics:")
        print("-" * 70)

        # Count by type
        type_counts = {}
        for d in self.diffs:
            type_counts[d.kind] = type_counts.get(d.kind, 0) + 1

        for diff_type, count in sorted(type_counts.items()):
            pct = (count / len(self.diffs)) * 100
            print(f"  {diff_type:12s}: {count:4d} ({pct:5.1f}%)")

        print(f"  {'Total':12s}: {len(self.diffs):4d} (100.0%)")
        print(f"\nComparison time: {self.comparison_time:.3f}s")


def run_interactive():
    """Entry point for interactive mode."""
    cli = InteractiveCli()
    cli.run()


if __name__ == "__main__":
    run_interactive()
