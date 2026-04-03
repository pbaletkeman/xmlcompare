package com.xmlcompare.plugin;

import com.xmlcompare.Difference;

/**
 * Plugin interface for custom difference filtering rules.
 *
 * <p>Implementations can suppress or transform {@link Difference} objects
 * before the final report is produced.  Register via the Service Loader
 * (add to {@code META-INF/services/com.xmlcompare.plugin.DifferenceFilter})
 * or via {@link PluginRegistry#registerFilter(DifferenceFilter)}.
 */
public interface DifferenceFilter extends ComparisonPluginSPI {

    /**
     * Return {@code true} if the given {@link Difference} should be excluded
     * from the final results.
     *
     * @param difference the detected difference (never {@code null})
     * @return {@code true} to suppress; {@code false} to keep
     */
    boolean shouldIgnore(Difference difference);
}
