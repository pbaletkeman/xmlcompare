package com.xmlcompare;

import java.util.LinkedHashMap;
import java.util.Map;

public class Difference {
    public final String path;
    public final String kind;
    public final String msg;
    public final String expected;
    public final String actual;

    public Difference(String path, String kind, String msg, String expected, String actual) {
        this.path = path;
        this.kind = kind;
        this.msg = msg;
        this.expected = expected;
        this.actual = actual;
    }

    public Difference(String path, String kind, String msg) {
        this(path, kind, msg, null, null);
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("path", path);
        map.put("kind", kind);
        map.put("message", msg);
        if (expected != null) map.put("expected", expected);
        if (actual != null) map.put("actual", actual);
        return map;
    }

    @Override
    public String toString() {
        return "Difference{path='" + path + "', kind='" + kind + "', msg='" + msg + "'}";
    }
}
