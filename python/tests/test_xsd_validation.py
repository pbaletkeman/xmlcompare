import pytest
import subprocess
import sys
from pathlib import Path

@pytest.mark.parametrize("xml_file,xsd_file,should_pass", [
    ("tests/valid.xml", "tests/schema.xsd", True),
    ("tests/invalid.xml", "tests/schema.xsd", False),
])
def test_xsd_validation(xml_file, xsd_file, should_pass):
    # Adjust path based on current working directory
    script_path = Path(__file__).parent.parent / "validate_xsd.py"
    result = subprocess.run([
        sys.executable, str(script_path), xml_file, xsd_file
    ], capture_output=True, cwd=Path(__file__).parent.parent)
    if should_pass:
        assert result.returncode == 0
    else:
        assert result.returncode != 0
