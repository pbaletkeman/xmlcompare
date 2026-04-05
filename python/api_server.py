#!/usr/bin/env python3
"""
xmlcompare REST API server.

Exposes xmlcompare as an HTTP service for CI/CD pipelines and webhook integration.

Usage:
    pip install flask
    python api_server.py [--host HOST] [--port PORT] [--debug]

Endpoints:
    GET  /health               – liveness check
    POST /compare/files        – compare two files by filesystem path
    POST /compare/content      – compare two XML strings directly

Example (compare by path):
    curl -s -X POST http://localhost:5000/compare/files \\
         -H 'Content-Type: application/json' \\
         -d '{"file1": "a.xml", "file2": "b.xml", "options": {"ignore_case": true}}'

Example (compare by content):
    curl -s -X POST http://localhost:5000/compare/content \\
         -H 'Content-Type: application/json' \\
         -d '{"xml1": "<r><v>1</v></r>", "xml2": "<r><v>1.0</v></r>"}'
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

try:
    from flask import Flask, request, jsonify
except ImportError:
    print("Flask is required: pip install flask", file=sys.stderr)
    sys.exit(1)

# Ensure the python/ directory is on the path when running from project root
sys.path.insert(0, str(Path(__file__).parent))

from xmlcompare import compare_xml_files, CompareOptions, _opts_from_dict  # noqa: E402

app = Flask(__name__)


def _build_opts(data: dict) -> CompareOptions:
    opts_data = data.get('options')
    if opts_data and isinstance(opts_data, dict):
        return _opts_from_dict(opts_data)
    return CompareOptions()


def _diffs_to_list(diffs) -> list:
    return [d.to_dict() for d in diffs]


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'xmlcompare-api'})


@app.route('/compare/files', methods=['POST'])
def compare_files():
    """Compare two XML files by filesystem path.

    Request body (JSON):
        {
            "file1": "/absolute/or/relative/path/a.xml",
            "file2": "/absolute/or/relative/path/b.xml",
            "options": { "ignore_case": true, ... }  // optional
        }

    Response:
        { "equal": true|false, "differences": [...] }
    """
    data = request.get_json(force=True, silent=True) or {}
    file1 = data.get('file1')
    file2 = data.get('file2')

    if not file1 or not file2:
        return jsonify({'error': 'file1 and file2 are required'}), 400

    try:
        f1 = Path(file1).resolve()
        f2 = Path(file2).resolve()
    except Exception as exc:
        return jsonify({'error': str(exc)}), 400

    if not f1.is_file():
        return jsonify({'error': f'file1 not found: {file1}'}), 400
    if not f2.is_file():
        return jsonify({'error': f'file2 not found: {file2}'}), 400

    opts = _build_opts(data)
    try:
        diffs = compare_xml_files(str(f1), str(f2), opts)
        return jsonify({'equal': len(diffs) == 0, 'differences': _diffs_to_list(diffs)})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/compare/content', methods=['POST'])
def compare_content():
    """Compare two XML strings directly (no filesystem access required).

    Request body (JSON):
        {
            "xml1": "<root><item>A</item></root>",
            "xml2": "<root><item>B</item></root>",
            "options": { "tolerance": 0.01, ... }  // optional
        }

    Response:
        { "equal": true|false, "differences": [...] }
    """
    data = request.get_json(force=True, silent=True) or {}
    xml1 = data.get('xml1')
    xml2 = data.get('xml2')

    if not xml1 or not xml2:
        return jsonify({'error': 'xml1 and xml2 are required'}), 400

    opts = _build_opts(data)
    with tempfile.TemporaryDirectory() as tmpdir:
        f1 = os.path.join(tmpdir, 'a.xml')
        f2 = os.path.join(tmpdir, 'b.xml')
        try:
            Path(f1).write_text(xml1, encoding='utf-8')
            Path(f2).write_text(xml2, encoding='utf-8')
        except Exception as exc:
            return jsonify({'error': f'Failed to write temp files: {exc}'}), 500

        try:
            diffs = compare_xml_files(f1, f2, opts)
            return jsonify({'equal': len(diffs) == 0, 'differences': _diffs_to_list(diffs)})
        except Exception as exc:
            return jsonify({'error': str(exc)}), 500


def main():
    parser = argparse.ArgumentParser(description='xmlcompare REST API server')
    parser.add_argument('--host', default='127.0.0.1',
                        help='Bind host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Bind port (default: 5000)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable Flask debug mode (development only)')
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
