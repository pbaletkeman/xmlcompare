import pytest
import subprocess
import sys

@pytest.mark.parametrize("xml_file,xsd_file,should_pass", [
    ("tests/valid.xml", "tests/schema.xsd", True),
    ("tests/invalid.xml", "tests/schema.xsd", False),
])
def test_xsd_validation(xml_file, xsd_file, should_pass):
    result = subprocess.run([
        sys.executable, "python/validate_xsd.py", xml_file, xsd_file
    ], capture_output=True)
    if should_pass:
        assert result.returncode == 0
    else:
        assert result.returncode != 0
