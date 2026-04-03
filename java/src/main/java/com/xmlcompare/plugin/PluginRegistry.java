package com.xmlcompare.plugin;

import com.xmlcompare.Difference;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.ServiceLoader;
import java.util.stream.Collectors;

/**
 * Central registry for discovering and managing xmlcompare plugins.
 *
 * <p>Plugins can be registered programmatically or auto-discovered via the
 * Java {@link ServiceLoader} mechanism.
 *
 * <p>Typical usage:
 * <pre>
 *   PluginRegistry registry = new PluginRegistry();
 *   registry.loadServiceLoader();       // discover from META-INF/services
 *   registry.loadModule("com.example.MyFormatter");  // manual load
 *   FormatterPlugin fmt = registry.getFormatter("unified-diff");
 * </pre>
 */
public class PluginRegistry {

    private final Map<String, FormatterPlugin> formatters = new LinkedHashMap<>();
    private final List<DifferenceFilter> filters = new ArrayList<>();

    // ------------------------------------------------------------------
    // Registration

    /**
     * Register a {@link FormatterPlugin} by its {@link FormatterPlugin#getName()}.
     *
     * @param plugin non-null formatter plugin
     */
    public void registerFormatter(FormatterPlugin plugin) {
        if (plugin == null) throw new IllegalArgumentException("plugin must not be null");
        formatters.put(plugin.getName(), plugin);
    }

    /**
     * Register a {@link DifferenceFilter}.
     *
     * @param filter non-null filter
     */
    public void registerFilter(DifferenceFilter filter) {
        if (filter == null) throw new IllegalArgumentException("filter must not be null");
        filters.add(filter);
    }

    // ------------------------------------------------------------------
    // Retrieval

    /**
     * Return the {@link FormatterPlugin} registered under {@code name}, or
     * {@code null} if none is found.
     *
     * @param name plugin name
     * @return plugin or {@code null}
     */
    public FormatterPlugin getFormatter(String name) {
        return formatters.get(name);
    }

    /**
     * Return an immutable snapshot of all registered formatter names.
     *
     * @return list of formatter names
     */
    public List<String> listFormatters() {
        return List.copyOf(formatters.keySet());
    }

    /**
     * Return an unmodifiable view of all registered {@link DifferenceFilter}s.
     *
     * @return list of filters
     */
    public List<DifferenceFilter> getFilters() {
        return List.copyOf(filters);
    }

    // ------------------------------------------------------------------
    // Discovery

    /**
     * Discover and register plugins via the Java {@link ServiceLoader}.
     *
     * <p>Reads {@code META-INF/services/com.xmlcompare.plugin.FormatterPlugin}
     * and {@code META-INF/services/com.xmlcompare.plugin.DifferenceFilter}.
     */
    public void loadServiceLoader() {
        loadServiceLoader(Thread.currentThread().getContextClassLoader());
    }

    /**
     * Discover plugins using the given {@link ClassLoader}.
     *
     * @param classLoader class loader to use for service discovery
     */
    public void loadServiceLoader(ClassLoader classLoader) {
        for (FormatterPlugin plugin : ServiceLoader.load(FormatterPlugin.class, classLoader)) {
            try {
                registerFormatter(plugin);
            } catch (Exception e) {
                System.err.println("Warning: failed to load formatter plugin '"
                    + plugin.getClass().getName() + "': " + e.getMessage());
            }
        }
        for (DifferenceFilter filter : ServiceLoader.load(DifferenceFilter.class, classLoader)) {
            try {
                registerFilter(filter);
            } catch (Exception e) {
                System.err.println("Warning: failed to load filter plugin '"
                    + filter.getClass().getName() + "': " + e.getMessage());
            }
        }
    }

    /**
     * Load a plugin class by its fully-qualified name and register it.
     *
     * <p>The class must implement either {@link FormatterPlugin} or
     * {@link DifferenceFilter} and have a public no-arg constructor.
     *
     * @param className fully-qualified class name
     * @throws IllegalArgumentException if the class cannot be loaded or does
     *                                  not implement a recognised plugin interface
     */
    public void loadModule(String className) {
        loadModule(className, Thread.currentThread().getContextClassLoader());
    }

    /**
     * Load a plugin class using the given {@link ClassLoader}.
     *
     * @param className   fully-qualified class name
     * @param classLoader class loader to use
     */
    public void loadModule(String className, ClassLoader classLoader) {
        try {
            Class<?> cls = classLoader.loadClass(className);
            Object instance = cls.getDeclaredConstructor().newInstance();
            if (instance instanceof FormatterPlugin fp) {
                registerFormatter(fp);
            } else if (instance instanceof DifferenceFilter df) {
                registerFilter(df);
            } else {
                throw new IllegalArgumentException(
                    "Class " + className + " does not implement FormatterPlugin or DifferenceFilter");
            }
        } catch (Exception e) {
            System.err.println("Warning: failed to load plugin '" + className + "': " + e.getMessage());
        }
    }

    // ------------------------------------------------------------------
    // Filter application

    /**
     * Apply all registered {@link DifferenceFilter}s to the given list,
     * returning a new list with suppressed differences removed.
     *
     * @param differences input differences
     * @return filtered list
     */
    public List<Difference> applyFilters(List<Difference> differences) {
        if (filters.isEmpty()) return differences;
        return differences.stream()
            .filter(d -> filters.stream().noneMatch(f -> f.shouldIgnore(d)))
            .collect(Collectors.toList());
    }
}
