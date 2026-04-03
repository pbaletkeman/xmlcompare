package com.xmlcompare.plugin;

import com.xmlcompare.Difference;

import java.util.List;
import java.util.Map;

/**
 * Plugin interface for custom output formatters.
 *
 * <p>Implementations are discovered via the Java Service Loader (add the
 * fully-qualified class name to
 * {@code META-INF/services/com.xmlcompare.plugin.FormatterPlugin}) or
 * registered programmatically via {@link PluginRegistry}.
 *
 * <p>Example registration in {@code META-INF/services}:
 * <pre>
 *   com.example.MyCustomFormatter
 * </pre>
 */
public interface FormatterPlugin extends ComparisonPluginSPI {

    /**
     * Format all comparison results into a printable string.
     *
     * @param allResults mapping of comparison key (e.g. "file1 vs file2") to a
     *                   {@link List} of {@link Difference} objects, or an error
     *                   {@link String}.  The value type mirrors what
     *                   {@code XmlCompare.compareXmlFiles} returns.
     * @param label1     optional label for the first file (may be {@code null})
     * @param label2     optional label for the second file (may be {@code null})
     * @return formatted report string (never {@code null})
     */
    String format(Map<String, Object> allResults, String label1, String label2);
}
