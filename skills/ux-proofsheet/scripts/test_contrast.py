#!/usr/bin/env python3
"""Unit tests for contrast.py — run: python test_contrast.py"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import contrast  # noqa: E402


class ContrastUnit(unittest.TestCase):
    def test_black_white(self):
        self.assertEqual(contrast.ratio("#000000", "#ffffff"), 21.0)

    def test_identical(self):
        self.assertEqual(contrast.ratio("#1069cf", "#1069cf"), 1.0)

    def test_short_hex(self):
        self.assertEqual(contrast.ratio("#000", "#fff"), 21.0)

    def test_sample_failing_grey(self):
        # From the example review: #798087 on #fff ≈ 4.0, fails AA normal
        a = contrast.assess("#798087", "#ffffff")
        self.assertAlmostEqual(a["ratio"], 4.0, delta=0.15)
        self.assertFalse(a["aa_normal"])
        self.assertTrue(a["aa_large"])

    def test_sample_pass_red(self):
        a = contrast.assess("#b50012", "#ffe8ea")
        self.assertGreaterEqual(a["ratio"], 4.5)
        self.assertTrue(a["aa_normal"])


class ContrastCLI(unittest.TestCase):
    def test_json_cli(self):
        script = Path(__file__).resolve().parent / "contrast.py"
        out = subprocess.check_output(
            [sys.executable, str(script), "#000", "#fff", "--json"],
            text=True,
        )
        data = json.loads(out)
        self.assertEqual(data[0]["ratio"], 21.0)

    def test_pairs_file(self):
        script = Path(__file__).resolve().parent / "contrast.py"
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("# comment\n#000000 #ffffff black-white\n")
            path = f.name
        out = subprocess.check_output(
            [sys.executable, str(script), "--pairs", path, "--json"],
            text=True,
        )
        data = json.loads(out)
        self.assertEqual(data[0]["label"], "black-white")
        self.assertEqual(data[0]["ratio"], 21.0)


if __name__ == "__main__":
    unittest.main()
