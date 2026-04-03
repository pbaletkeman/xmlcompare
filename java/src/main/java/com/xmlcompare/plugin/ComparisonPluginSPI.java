package com.xmlcompare.plugin;

import java.util.Map;

/**
 * Service Provider Interface for xmlcompare plugins.
 *
 * <p>All plugin types extend or implement this marker interface.
 * Use the Java Service Loader mechanism (META-INF/services) or
 * programmatic registration via {@link PluginRegistry}.
 */
public interface ComparisonPluginSPI {

    /**
     * Returns the unique name that identifies this plugin
     * (e.g. {@code "unified-diff"}, {@code "ignore-whitespace"}).
     *
     * @return non-null, non-empty plugin name
     */
    String getName();

    /**
     * Optional initialisation hook called by {@link PluginRegistry} after
     * the plugin is loaded.  The default implementation is a no-op.
     *
     * @param config key/value configuration map (may be empty)
     */
    default void init(Map<String, String> config) {
        // default no-op
    }
}
