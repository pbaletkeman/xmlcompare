import xml.etree.ElementTree as ET
import os
import sys

def validate_xml_with_xsd(xml_path, xsd_path):
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

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python validate_xsd.py <xml_file> <xsd_file>")
        sys.exit(1)
    xml_file, xsd_file = sys.argv[1], sys.argv[2]
    valid = validate_xml_with_xsd(xml_file, xsd_file)
    sys.exit(0 if valid else 1)
