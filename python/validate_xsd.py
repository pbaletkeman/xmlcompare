import xml.etree.ElementTree as ET
import os
import sys


def validate_xml_with_xsd(xml_path, xsd_path):
    """Validate *xml_path* against *xsd_path* using lxml.

    Returns ``True`` if valid, ``False`` otherwise.
    Prints a human-readable result / error message to stdout/stderr.
    """
    try:
        from lxml import etree
    except ImportError:
        print("lxml is required for XSD validation. Please install with 'pip install lxml'.")
        sys.exit(2)
    with open(xsd_path, 'rb') as f:
        schema_root = etree.XML(f.read())
    schema = etree.XMLSchema(schema_root)
    parser = etree.XMLParser(schema=schema)
    try:
        with open(xml_path, 'rb') as f:
            etree.fromstring(f.read(), parser)
        print(f"{xml_path} is valid against {xsd_path}")
        return True
    except etree.XMLSyntaxError as e:
        print(f"Validation error in {xml_path}: {e}")
        return False


def get_validation_errors(xml_path, xsd_path):
    """Return a list of validation error strings for *xml_path* against *xsd_path*.

    Returns an empty list if the document is valid.
    Returns ``None`` if lxml is unavailable (caller should handle gracefully).
    """
    try:
        from lxml import etree
    except ImportError:
        return None

    try:
        with open(xsd_path, 'rb') as f:
            schema_root = etree.XML(f.read())
        schema = etree.XMLSchema(schema_root)
        with open(xml_path, 'rb') as f:
            doc = etree.parse(f)
        schema.validate(doc)
        return [str(e) for e in schema.error_log]
    except Exception as exc:
        return [str(exc)]


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python validate_xsd.py <xml_file> <xsd_file>")
        sys.exit(1)
    xml_file, xsd_file = sys.argv[1], sys.argv[2]
    valid = validate_xml_with_xsd(xml_file, xsd_file)
    sys.exit(0 if valid else 1)
