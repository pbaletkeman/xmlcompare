"""Plugin interface for xmlcompare.

Provides base classes and a registry for extending xmlcompare with
custom formatters and difference filters.

Usage (entry_points in pyproject.toml)::

    [project.entry-points."xmlcompare.formatters"]
    my-formatter = "mypackage.mymodule:MyFormatter"

    [project.entry-points."xmlcompare.filters"]
    my-filter = "mypackage.mymodule:MyFilter"

Usage (programmatic)::

    from plugin_interface import get_registry, FormatterPlugin

    class MyFormatter(FormatterPlugin):
        @property
        def name(self):
            return "my-formatter"

        def format(self, all_results, **kwargs):
            return str(all_results)

    get_registry().register_formatter(MyFormatter())
"""

import importlib
import importlib.metadata
import sys
from abc import ABC, abstractmethod


class FormatterPlugin(ABC):
    """Base class for output formatter plugins.

    Subclasses must implement :attr:`name` and :meth:`format`.
    Register instances via :class:`PluginRegistry`.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name identifier for this formatter (e.g. ``'unified-diff'``)."""

    @abstractmethod
    def format(self, all_results: dict, **kwargs) -> str:
        """Format comparison results.

        Parameters
        ----------
        all_results:
            Mapping of comparison key → list of ``Difference`` objects (or
            error string).  The structure mirrors what ``compare_xml_files``
            and ``compare_dirs`` return.
        kwargs:
            Optional extra context (e.g. ``label1``, ``label2``).

        Returns
        -------
        str
            The formatted report as a string.
        """


class DifferenceFilter(ABC):
    """Base class for custom difference filtering / rule plugins.

    Subclasses can suppress certain differences from the final report.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name identifier for this filter."""

    @abstractmethod
    def should_ignore(self, difference) -> bool:
        """Return ``True`` if *difference* should be excluded from results.

        Parameters
        ----------
        difference:
            A ``Difference`` instance from ``xmlcompare``.
        """


class PluginRegistry:
    """Registry for discovering and loading xmlcompare plugins."""

    def __init__(self):
        self._formatters: dict = {}
        self._filters: list = []

    # ------------------------------------------------------------------
    # Registration

    def register_formatter(self, plugin: FormatterPlugin) -> None:
        """Register a :class:`FormatterPlugin` by its :attr:`~FormatterPlugin.name`."""
        self._formatters[plugin.name] = plugin

    def register_filter(self, plugin: DifferenceFilter) -> None:
        """Register a :class:`DifferenceFilter`."""
        self._filters.append(plugin)

    # ------------------------------------------------------------------
    # Retrieval

    def get_formatter(self, name: str):
        """Return the :class:`FormatterPlugin` registered under *name*, or ``None``."""
        return self._formatters.get(name)

    def get_filters(self) -> list:
        """Return a copy of all registered :class:`DifferenceFilter` instances."""
        return list(self._filters)

    def list_formatters(self) -> list:
        """Return the names of all registered formatters."""
        return list(self._formatters.keys())

    # ------------------------------------------------------------------
    # Discovery

    def load_entry_points(self) -> None:
        """Discover and load plugins from installed packages via ``entry_points``.

        Reads ``xmlcompare.formatters`` and ``xmlcompare.filters`` groups.
        """
        try:
            eps = importlib.metadata.entry_points()
            # Python 3.12+ / 3.9+ unified API
            if hasattr(eps, 'select'):
                formatter_eps = eps.select(group='xmlcompare.formatters')
                filter_eps = eps.select(group='xmlcompare.filters')
            else:
                formatter_eps = eps.get('xmlcompare.formatters', [])
                filter_eps = eps.get('xmlcompare.filters', [])
        except Exception:
            return

        for ep in formatter_eps:
            try:
                plugin_cls = ep.load()
                self.register_formatter(plugin_cls())
            except Exception as exc:
                print(f"Warning: failed to load formatter plugin {ep.name!r}: {exc}",
                      file=sys.stderr)

        for ep in filter_eps:
            try:
                plugin_cls = ep.load()
                self.register_filter(plugin_cls())
            except Exception as exc:
                print(f"Warning: failed to load filter plugin {ep.name!r}: {exc}",
                      file=sys.stderr)

    def load_module(self, module_path: str) -> None:
        """Load plugins from a Python module path (e.g. ``'mypackage.myplugin'``).

        Scans the module for concrete subclasses of :class:`FormatterPlugin`
        and :class:`DifferenceFilter` and registers them automatically.
        """
        try:
            module = importlib.import_module(module_path)
        except ImportError as exc:
            print(f"Warning: cannot import plugin module {module_path!r}: {exc}",
                  file=sys.stderr)
            return

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if not isinstance(attr, type) or attr_name.startswith('_'):
                continue
            if attr is FormatterPlugin:
                continue
            if attr is DifferenceFilter:
                continue
            if issubclass(attr, FormatterPlugin):
                try:
                    self.register_formatter(attr())
                except Exception as exc:
                    print(f"Warning: failed to instantiate {attr_name}: {exc}",
                          file=sys.stderr)
            elif issubclass(attr, DifferenceFilter):
                try:
                    self.register_filter(attr())
                except Exception as exc:
                    print(f"Warning: failed to instantiate {attr_name}: {exc}",
                          file=sys.stderr)


# ---------------------------------------------------------------------------
# Module-level default registry
# ---------------------------------------------------------------------------

_default_registry = PluginRegistry()


def get_registry() -> PluginRegistry:
    """Return the module-level default :class:`PluginRegistry`."""
    return _default_registry
