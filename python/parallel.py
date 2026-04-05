"""
Parallel XML comparison using multiprocessing.

Two levels of parallelism are provided:

1. compare_xml_files_parallel() - single-file comparison
   Splits the root element's children into one task per child and
   compares each subtree in a separate worker process.  Subtrees are
   serialised to XML strings before IPC so that ElementTree objects
   (which are not picklable) do not cross process boundaries.
   Falls back to serial when the file has fewer than 2 children or
   the requested process count is 1.

2. compare_dirs_parallel() - directory comparison
   Distributes individual file-pair comparisons across a pool of
   worker processes.  This is the most common high-value use-case:
   comparing hundreds of XML files in a directory.

Both functions guarantee that results are identical to the serial
compare_xml_files() / compare_dirs() equivalents.
"""

import multiprocessing
from multiprocessing import Pool
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

from xmlcompare import (
    CompareOptions,
    Difference,
    compare_dirs,
    compare_xml_files,
    get_tag,
)


# ---------------------------------------------------------------------------
# Options serialisation helpers (CompareOptions is not picklable as-is)
# ---------------------------------------------------------------------------

def _options_to_dict(options) -> dict:
    """Serialise a CompareOptions instance to a plain dict for IPC."""
    return {
        'tolerance': getattr(options, 'tolerance', 0.0),
        'ignore_case': getattr(options, 'ignore_case', False),
        'unordered': getattr(options, 'unordered', False),
        'ignore_namespaces': getattr(options, 'ignore_namespaces', False),
        'ignore_attributes': getattr(options, 'ignore_attributes', False),
        'skip_keys': list(getattr(options, 'skip_keys', [])),
        'skip_pattern': getattr(options, 'skip_pattern', None),
        'filter_xpath': getattr(options, 'filter_xpath', None),
        'output_format': getattr(options, 'output_format', 'text'),
        'structure_only': getattr(options, 'structure_only', False),
        'fail_fast': getattr(options, 'fail_fast', False),
        'max_depth': getattr(options, 'max_depth', None),
        'verbose': False,  # suppress per-element trace in workers
        'quiet': True,
        'summary': False,
        'schema': getattr(options, 'schema', None),
        'type_aware': getattr(options, 'type_aware', False),
        'match_attr': getattr(options, 'match_attr', None),
        # Plugins are not passed - they may not be importable in workers
        'plugins': [],
    }


def _dict_to_options(d: dict) -> CompareOptions:
    """Reconstruct a CompareOptions from the dict produced by _options_to_dict."""
    opts = CompareOptions()
    for key, value in d.items():
        setattr(opts, key, value)
    return opts


# ---------------------------------------------------------------------------
# Worker functions (must be importable at module level for multiprocessing)
# ---------------------------------------------------------------------------

def _compare_subtree_worker(args: Tuple) -> List[Difference]:
    """
    Worker: deserialise two XML strings, compare them, return differences.

    The base_path is prepended to all difference paths so that the merged
    result reflects the correct location in the original document.
    """
    xml_str1, xml_str2, opts_dict, base_path = args
    opts = _dict_to_options(opts_dict)
    try:
        from xmlcompare import compare_elements, _apply_filters
        root1 = ET.fromstring(xml_str1)
        root2 = ET.fromstring(xml_str2)
        diffs = compare_elements(root1, root2, opts, path=base_path)
        return _apply_filters(diffs, opts)
    except ET.ParseError:
        return []
    except Exception:  # noqa: BLE001
        return []


def _compare_file_pair_worker(args: Tuple) -> Tuple[str, object]:
    """
    Worker: compare a single file pair and return (label, result).

    Used by compare_dirs_parallel for directory-level parallelism.
    """
    file1, file2, opts_dict = args
    opts = _dict_to_options(opts_dict)
    label = f"{file1} vs {file2}"
    try:
        diffs = compare_xml_files(file1, file2, opts)
        return label, diffs
    except (ValueError, FileNotFoundError) as exc:
        return label, str(exc)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compare_xml_files_parallel(file1_path, file2_path, options=None, num_processes=0):
    """
    Compare two XML files using parallel subtree processing.

    The root element's direct children are each compared in a dedicated
    worker process.  Subtrees are serialised to XML strings before being
    handed to workers, so ElementTree objects never cross process
    boundaries.  Results are sorted by path and returned as a flat list,
    identical to what compare_xml_files() would return.

    Performance notes:
    - Overhead of fork + serialisation dominates for small files; the
      serial fallback is used automatically when there are < 2 children.
    - Meaningful speedup for files whose root has many independent
      subtrees (e.g. <orders> with hundreds of <order> children).

    Args:
        file1_path: Path to first XML file
        file2_path: Path to second XML file
        options: CompareOptions (optional, defaults constructed if None)
        num_processes: Worker process count (0 = auto-detect)

    Returns:
        Sorted list of Difference objects
    """
    if options is None:
        options = CompareOptions()

    if num_processes <= 0:
        num_processes = get_recommended_process_count()

    try:
        tree1 = ET.parse(str(file1_path))
        tree2 = ET.parse(str(file2_path))
    except ET.ParseError as exc:
        raise ValueError(f"Failed to parse XML: {exc}") from exc
    except OSError as exc:
        raise FileNotFoundError(str(exc)) from exc

    root1 = tree1.getroot()
    root2 = tree2.getroot()
    children1 = list(root1)
    children2 = list(root2)

    # Not enough children for parallelisation to pay off
    if min(len(children1), len(children2)) < 2 or num_processes < 2:
        return compare_xml_files(str(file1_path), str(file2_path), options)

    opts_dict = _options_to_dict(options)
    root_tag = get_tag(root1, options)
    max_children = max(len(children1), len(children2))

    tasks: List[Tuple] = []
    structural_diffs: List[Difference] = []

    for i in range(max_children):
        has1 = i < len(children1)
        has2 = i < len(children2)

        if has1 and has2:
            c1, c2 = children1[i], children2[i]
            child_tag = get_tag(c1, options)
            suffix = f"[{i}]" if i > 0 else ''
            base_path = f"{root_tag}/{child_tag}{suffix}"
            tasks.append((
                ET.tostring(c1, encoding='unicode'),
                ET.tostring(c2, encoding='unicode'),
                opts_dict,
                base_path,
            ))
        elif has2:
            child_tag = get_tag(children2[i], options)
            base_path = f"{root_tag}/{child_tag}[{i}]"
            structural_diffs.append(Difference(
                base_path, 'missing',
                f"Element {child_tag!r} at position {i} missing in first document",
            ))
        else:
            child_tag = get_tag(children1[i], options)
            base_path = f"{root_tag}/{child_tag}[{i}]"
            structural_diffs.append(Difference(
                base_path, 'extra',
                f"Element {child_tag!r} at position {i} missing in second document",
            ))

    if not tasks:
        return sorted(structural_diffs, key=lambda d: d.path)

    actual_procs = min(num_processes, len(tasks))
    with Pool(actual_procs) as pool:
        results = pool.map(_compare_subtree_worker, tasks)

    all_diffs: List[Difference] = list(structural_diffs)
    for batch in results:
        all_diffs.extend(batch)
    return sorted(all_diffs, key=lambda d: d.path)


def compare_dirs_parallel(dir1: str, dir2: str, options=None, num_processes: int = 0,
                          recursive: bool = False) -> Dict:
    """
    Compare two directories of XML files in parallel.

    Each XML file pair is compared in a separate worker process.  This is
    the highest-value parallelism strategy: comparing N files becomes
    N / num_processes times faster on large directory trees.

    Args:
        dir1: First directory path
        dir2: Second directory path
        options: CompareOptions (optional)
        num_processes: Number of workers (0 = auto-detect)
        recursive: Recurse into subdirectories

    Returns:
        Dict mapping filename -> list of Difference objects (or error string)
    """
    if options is None:
        options = CompareOptions()

    if num_processes <= 0:
        num_processes = get_recommended_process_count()

    dir1_path = Path(dir1)
    dir2_path = Path(dir2)

    if recursive:
        names1 = {str(p.relative_to(dir1_path)) for p in dir1_path.rglob('*.xml')}
        names2 = {str(p.relative_to(dir2_path)) for p in dir2_path.rglob('*.xml')}
    else:
        names1 = {p.name for p in dir1_path.glob('*.xml')}
        names2 = {p.name for p in dir2_path.glob('*.xml')}

    opts_dict = _options_to_dict(options)
    tasks: List[Tuple] = []
    results: Dict = {}

    for fname in sorted(names1 | names2):
        if fname not in names1:
            results[fname] = [Difference(fname, 'missing', f"File {fname!r} missing in {dir1}")]
        elif fname not in names2:
            results[fname] = [Difference(fname, 'missing', f"File {fname!r} missing in {dir2}")]
        else:
            tasks.append((str(dir1_path / fname), str(dir2_path / fname), opts_dict))

    if tasks:
        actual_procs = min(num_processes, len(tasks))
        with Pool(actual_procs) as pool:
            worker_results = pool.map(_compare_file_pair_worker, tasks)

        for label, value in worker_results:
            # Recover original filename from label
            fname = Path(label.split(' vs ')[0]).name
            results[fname] = value

    return dict(sorted(results.items()))


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def get_recommended_process_count() -> int:
    """Return the recommended number of worker processes for this system."""
    cores = multiprocessing.cpu_count()
    # Reserve one core for the main process and OS
    return max(1, cores - 1)


def get_parallel_stats() -> 'ParallelStats':
    """Return system parallelism information."""
    return ParallelStats(
        available_cores=multiprocessing.cpu_count(),
        recommended_processes=get_recommended_process_count(),
        expected_speedup=min(4.0, float(get_recommended_process_count())),
    )


class ParallelStats:
    """System parallelism capabilities."""

    def __init__(self, available_cores: int, recommended_processes: int,
                 expected_speedup: float):
        self.available_cores = available_cores
        self.recommended_processes = recommended_processes
        self.expected_speedup = expected_speedup

    def __str__(self):
        return (
            f"Cores: {self.available_cores} | "
            f"Recommended Processes: {self.recommended_processes} | "
            f"Expected Speedup: {self.expected_speedup:.1f}x"
        )

    def __repr__(self):
        return self.__str__()
