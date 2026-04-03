package com.xmlcompare.schema;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Optional;
import java.util.Set;

/**
 * Utility class for type-aware value comparison based on XSD types.
 *
 * <p>Uses schema type information to apply smarter equality checks:
 * <ul>
 *   <li>{@code xs:boolean}: {@code "true"} and {@code "1"} are equal</li>
 *   <li>{@code xs:integer}/{@code xs:decimal}/{@code xs:float}: numeric equality</li>
 *   <li>{@code xs:date}/{@code xs:dateTime}: ISO date parsing and comparison</li>
 * </ul>
 */
public final class TypeAwareComparator {

    private TypeAwareComparator() { }

    /** XSD types treated as date/datetime. */
    private static final Set<String> DATE_TYPES = Set.of(
        "date", "dateTime", "time", "gYear", "gYearMonth",
        "gMonth", "gMonthDay", "gDay", "duration"
    );

    /** XSD types treated as numeric. */
    private static final Set<String> NUMERIC_TYPES = Set.of(
        "integer", "int", "long", "short", "byte",
        "unsignedInt", "unsignedLong", "unsignedShort", "unsignedByte",
        "positiveInteger", "nonNegativeInteger", "negativeInteger", "nonPositiveInteger",
        "decimal", "float", "double"
    );

    /** XSD types treated as boolean. */
    private static final Set<String> BOOLEAN_TYPES = Set.of("boolean");

    /**
     * Determine the broad category of an XSD type.
     *
     * @param xsType XSD type string (e.g. {@code "xs:date"}) or {@code null}
     * @return {@code "date"}, {@code "numeric"}, {@code "boolean"}, or {@code null}
     */
    public static String typeCategory(String xsType) {
        if (xsType == null) return null;
        String local = xsType.contains(":") ? xsType.substring(xsType.indexOf(':') + 1) : xsType;
        if (DATE_TYPES.contains(local)) return "date";
        if (NUMERIC_TYPES.contains(local)) return "numeric";
        if (BOOLEAN_TYPES.contains(local)) return "boolean";
        return null;
    }

    /**
     * Compare two string values using schema type awareness.
     *
     * @param a      first value (may be {@code null})
     * @param b      second value (may be {@code null})
     * @param xsType XSD type string, or {@code null}
     * @return {@code Optional.of(true/false)} if the comparison could be applied,
     *         {@code Optional.empty()} if the type is unrecognised (caller should
     *         fall back to default comparison)
     */
    public static Optional<Boolean> typeAwareEqual(String a, String b, String xsType) {
        String cat = typeCategory(xsType);
        if (cat == null) return Optional.empty();

        String na = (a != null) ? a.strip() : "";
        String nb = (b != null) ? b.strip() : "";

        return switch (cat) {
            case "boolean" -> Optional.of(isTruthy(na) == isTruthy(nb));
            case "numeric" -> compareNumeric(na, nb);
            case "date" -> compareDate(na, nb);
            default -> Optional.empty();
        };
    }

    // ------------------------------------------------------------------
    // Private helpers
    // ------------------------------------------------------------------

    private static boolean isTruthy(String value) {
        return "true".equalsIgnoreCase(value) || "1".equals(value);
    }

    private static Optional<Boolean> compareNumeric(String a, String b) {
        try {
            double da = Double.parseDouble(a);
            double db = Double.parseDouble(b);
            return Optional.of(da == db);
        } catch (NumberFormatException e) {
            return Optional.empty();
        }
    }

    private static final DateTimeFormatter[] DATE_FORMATTERS = {
        DateTimeFormatter.ISO_LOCAL_DATE,
        DateTimeFormatter.ISO_LOCAL_DATE_TIME,
        DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ssX"),
        DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSX"),
    };

    private static Optional<Boolean> compareDate(String a, String b) {
        // Try LocalDate first
        try {
            LocalDate da = LocalDate.parse(a, DateTimeFormatter.ISO_LOCAL_DATE);
            LocalDate db = LocalDate.parse(b, DateTimeFormatter.ISO_LOCAL_DATE);
            return Optional.of(da.equals(db));
        } catch (DateTimeParseException ignored) { }

        // Try LocalDateTime
        try {
            LocalDateTime da = LocalDateTime.parse(a, DateTimeFormatter.ISO_LOCAL_DATE_TIME);
            LocalDateTime db = LocalDateTime.parse(b, DateTimeFormatter.ISO_LOCAL_DATE_TIME);
            return Optional.of(da.equals(db));
        } catch (DateTimeParseException ignored) { }

        return Optional.empty();
    }
}
