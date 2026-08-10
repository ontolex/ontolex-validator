#!/usr/bin/env python3
"""
Compares ontolex-validator.py against src/ontolex-shapes.ttl (SHACL) for
each fixture in tests/data/, so the two can be checked for behavioural
parity. For every fixture, both validators are run and the resulting
(code, severity) multisets are compared.

Severity mapping: err/[ERROR] <-> sh:Violation, warn/[WARN] <-> sh:Warning,
note/[NOTE] <-> sh:Info.

Usage: .venv/bin/python3 tests/compare.py [tests/data/*.ttl]
"""
import glob
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

from pyshacl import validate
from rdflib import Graph
from rdflib.namespace import RDF

REPO = Path(__file__).resolve().parent.parent
VALIDATOR = REPO / "src" / "ontolex-validator.py"
SHAPES = REPO / "src" / "ontolex-shapes.ttl"

SEVERITY_FROM_XML_TAG = {"error": "Violation", "warn": "Warning", "note": "Info"}

# MULT_TYPES is a diagnostic about ontolex-validator.py's own
# type-inference confidence (see harmonizeType() / computeTypes()), not
# a check on the RDF data, and has no SHACL equivalent -- see the
# top-of-file comment in src/ontolex-shapes.ttl. It is intentionally
# never produced by the SHACL side, so it is excluded from the diff
# here rather than reported as a mismatch on every file that hits it.
IGNORED_CODES = {"MULT_TYPES"}


def run_python_validator(path):
    out = subprocess.run(
        [sys.executable, str(VALIDATOR), "-f", "turtle", "-o", "xml", str(path)],
        capture_output=True,
        text=True,
    ).stdout
    counts = Counter()
    for tag, code in re.findall(r"<(error|warn|note) code=\"([^\"]+)\">", out):
        if code in IGNORED_CODES:
            continue
        counts[(code, SEVERITY_FROM_XML_TAG[tag])] += 1
    return counts


SH_SEVERITY_LOCAL = {
    "http://www.w3.org/ns/shacl#Violation": "Violation",
    "http://www.w3.org/ns/shacl#Warning": "Warning",
    "http://www.w3.org/ns/shacl#Info": "Info",
}


def run_shacl_validator(path):
    conforms, results_graph, _ = validate(
        str(path),
        shacl_graph=str(SHAPES),
        data_graph_format="turtle",
        shacl_graph_format="turtle",
        advanced=True,
    )
    q = """
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    SELECT ?message ?severity WHERE {
        ?r a sh:ValidationResult ;
           sh:resultMessage ?message ;
           sh:resultSeverity ?severity .
    }
    """
    counts = Counter()
    for message, severity in results_graph.query(q):
        code = str(message).split(":", 1)[0]
        counts[(code, SH_SEVERITY_LOCAL[str(severity)])] += 1
    return counts


def compare_file(path):
    py_counts = run_python_validator(path)
    sh_counts = run_shacl_validator(path)
    codes = sorted(set(py_counts) | set(sh_counts))
    ok = True
    lines = []
    for code in codes:
        p = py_counts.get(code, 0)
        s = sh_counts.get(code, 0)
        status = "OK  " if p == s else "FAIL"
        if p != s:
            ok = False
        lines.append(f"  {status} {code[0]:20s} {code[1]:10s} python={p} shacl={s}")
    return ok, lines


def main():
    paths = sys.argv[1:] or sorted(glob.glob(str(REPO / "tests" / "data" / "*.ttl")))
    all_ok = True
    for path in paths:
        ok, lines = compare_file(path)
        all_ok = all_ok and ok
        print(f"[{'PASS' if ok else 'FAIL'}] {path}")
        for line in lines:
            print(line)
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
