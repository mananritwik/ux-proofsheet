#!/usr/bin/env python3
"""Unit tests for token_check.py. Run: python test_token_check.py"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import token_check  # noqa: E402

FIX = HERE / "fixtures"
NODES = FIX / "home-nodes.json"
VARS = FIX / "home-variables.json"
CODE = FIX / "home-design-context.tsx"
META = FIX / "home-metadata.xml"


def by_kind(result):
    return {f["kind"]: f for f in result["findings"]}


def write_tmp(obj, suffix=".json"):
    f = tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8")
    f.write(obj if isinstance(obj, str) else json.dumps(obj))
    f.close()
    return f.name


class Baselines(unittest.TestCase):
    """Guard the cited numbers against accidental edits (see token-baselines.md)."""

    def setUp(self):
        self.b = token_check.load_baselines()

    def test_material3_sizes(self):
        sizes = token_check.baseline_sizes(self.b["material3"])
        self.assertEqual(sizes, [11, 12, 14, 16, 22, 24, 28, 32, 36, 45, 57])
        self.assertEqual(len(self.b["material3"]["type_scale"]), 15)
        self.assertEqual(self.b["material3"]["type_ratio"], 1.125)

    def test_material3_line_heights_on_4dp(self):
        for row in self.b["material3"]["type_scale"]:
            self.assertEqual(row["line_height"] % 4, 0, row["style"])

    def test_hig_sizes(self):
        sizes = token_check.baseline_sizes(self.b["hig_ios"])
        self.assertEqual(sizes, [11, 12, 13, 15, 16, 17, 20, 22, 28, 34])
        body = [r for r in self.b["hig_ios"]["type_scale"] if r["style"] == "Body"][0]
        self.assertEqual((body["size"], body["line_height"]), (17, 22))

    def test_hig_has_no_spacing_grid(self):
        # Apple publishes none; the tool must not invent one.
        self.assertIsNone(self.b["hig_ios"]["spacing"])
        self.assertIsNone(self.b["hig_ios"]["type_ratio"])

    def test_every_baseline_cites_a_source(self):
        for key, b in self.b.items():
            self.assertTrue(b["type_source"].startswith("https://"), key)
        self.assertTrue(self.b["material3"]["spacing"]["source"].startswith("https://"))


class Parsing(unittest.TestCase):
    def test_font_string(self):
        s = 'Font(family: "Inter", style: Regular, size: 16, weight: 400, lineHeight: 24, letterSpacing: 0)'
        self.assertEqual(token_check._parse_font_string(s), (16, 24))

    def test_font_string_percent_line_height(self):
        s = 'Font(family: "Inter", style: Regular, size: 20, weight: 400, lineHeight: 120, letterSpacing: 0)'
        self.assertEqual(token_check._parse_font_string(s), (20, 24))

    def test_variable_defs_ignore_colors_and_radius(self):
        texts, spacing = token_check.from_variable_defs(json.loads(VARS.read_text()))
        self.assertEqual(len(texts), 8)
        self.assertEqual(sorted(s["value"] for s in spacing), [2, 4, 8, 12, 14, 16, 24])

    def test_node_tree_skips_single_child_gap(self):
        tree = {"type": "FRAME", "id": "1:1", "layoutMode": "VERTICAL", "itemSpacing": 7,
                "children": [{"type": "TEXT", "id": "1:2", "style": {"fontSize": 16, "lineHeightPx": 24}}]}
        texts, spacing = token_check.from_node_tree(tree)
        self.assertEqual(texts[0]["size"], 16)
        self.assertEqual(texts[0]["line_height"], 24)
        self.assertEqual(spacing, [])

    def test_plugin_line_height_shape(self):
        tree = {"type": "TEXT", "id": "1:2", "fontSize": 20, "lineHeight": {"unit": "PERCENT", "value": 150}}
        texts, _ = token_check.from_node_tree(tree)
        self.assertEqual(texts[0]["line_height"], 30)

    def test_design_context_tailwind_and_css(self):
        texts, spacing = token_check.from_design_context(CODE.read_text())
        pairs = {(t["size"], t["line_height"]) for t in texts}
        self.assertIn((32, 38), pairs)
        self.assertIn((13, 18), pairs)  # style={{ fontSize, lineHeight }}
        values = sorted({s["value"] for s in spacing})
        self.assertEqual(values, [4, 6, 8, 12, 14, 16])  # gap-2 -> 8, p-3 -> 12
        hero = [s for s in spacing if s["value"] == 14][0]
        self.assertEqual(hero["node"], "529:14078")

    def test_metadata_geometry_gaps(self):
        texts, spacing = token_check.from_metadata_xml(META.read_text())
        self.assertEqual(texts, [])
        values = sorted(s["value"] for s in spacing)
        self.assertEqual(values, [10, 10, 10, 14, 16, 16])

    def test_input_kind_detection(self):
        _, _, kinds = token_check.read_inputs([NODES, VARS, CODE, META])
        self.assertEqual([k["kind"] for k in kinds],
                         ["node_tree", "variable_defs", "design_context", "metadata_xml"])


class Analysis(unittest.TestCase):
    """The committed sample report quotes these numbers (golden check re-runs them)."""

    @classmethod
    def setUpClass(cls):
        cls.r = token_check.check([NODES], file_url="https://figma.com/design/AbC123/Home")

    def test_type_ramp_and_ratio(self):
        t = self.r["type"]
        self.assertEqual(t["ramp"], [11, 12, 13, 14, 15, 16, 20, 32])
        self.assertAlmostEqual(t["overall_ratio"], 1.165, places=3)
        self.assertEqual(t["baseline"], "hig_ios")  # 6/8 HIG vs 5/8 Material
        self.assertEqual(t["baseline_fit"]["material3"]["matched"], 5)

    def test_spacing_scale_and_base_unit(self):
        s = self.r["spacing"]
        self.assertEqual(s["scale"], [2, 4, 6, 8, 10, 12, 14, 16, 24])
        self.assertIsNone(s["base_unit"])
        self.assertEqual(s["closest_unit"], 4)
        self.assertEqual(s["share_on_4"], 0.63)

    def test_findings_order_and_ids(self):
        kinds = [f["kind"] for f in self.r["findings"]]
        self.assertEqual(kinds, ["spacing_off_grid", "type_crowded", "type_off_baseline", "type_jump"])
        self.assertEqual([f["id"] for f in self.r["findings"]], ["T1", "T2", "T3", "T4"])

    def test_off_grid_suggestions_round_up(self):
        f = by_kind(self.r)["spacing_off_grid"]
        self.assertEqual(f["values"], [2, 6, 10, 14])
        self.assertEqual({d["value"]: d["suggest"] for d in f["detail"]}, {2: 4, 6: 8, 10: 12, 14: 16})
        self.assertEqual(f["severity"], "medium")

    def test_crowded_and_jump(self):
        k = by_kind(self.r)
        self.assertEqual(k["type_crowded"]["values"], [13, 14, 15])
        self.assertEqual(k["type_off_baseline"]["values"], [14, 32])
        self.assertEqual(k["type_jump"]["detail"][0]["baseline_sizes_between"], [22, 28])

    def test_figma_links(self):
        for f in self.r["findings"]:
            self.assertTrue(f["figma_url"].startswith("https://figma.com/design/AbC123/Home?node-id="), f["id"])
            self.assertNotIn(":", f["figma_url"].split("node-id=")[1])

    def test_material_forced_flags_line_heights(self):
        r = token_check.check([NODES], baseline="material3")
        k = by_kind(r)
        self.assertEqual(k["type_off_baseline"]["values"], [13, 15, 20])
        self.assertIn("line_height_off_grid", k)  # 13/18, 16/21, 20/25, 32/38 ...

    def test_clean_design_has_no_findings(self):
        path = write_tmp({
            "Body": 'Font(family: "Roboto", style: Regular, size: 14, weight: 400, lineHeight: 20, letterSpacing: 0)',
            "Title": 'Font(family: "Roboto", style: Medium, size: 16, weight: 500, lineHeight: 24, letterSpacing: 0)',
            "Headline": 'Font(family: "Roboto", style: Regular, size: 24, weight: 400, lineHeight: 32, letterSpacing: 0)',
            "spacing/sm": "8", "spacing/md": "16", "spacing/lg": "24",
        })
        r = token_check.check([path])
        self.assertEqual(r["findings"], [])
        self.assertEqual(r["type"]["baseline"], "material3")
        self.assertEqual(r["spacing"]["base_unit"], 8)

    def test_hig_baseline_sizes_not_crowded(self):
        # 15/16/17 are 1pt apart but all are HIG styles: no crowded finding.
        path = write_tmp({k: f'Font(family: "SF Pro", style: Regular, size: {v}, weight: 400, lineHeight: 20, letterSpacing: 0)'
                          for k, v in {"a": 15, "b": 16, "c": 17}.items()})
        r = token_check.check([path], baseline="hig_ios")
        self.assertEqual(r["findings"], [])

    def test_metadata_only_notes_missing_type(self):
        r = token_check.check([META])
        self.assertIsNone(r["type"])
        self.assertTrue(any("get_metadata" in n for n in r["notes"]))

    def test_empty_input(self):
        r = token_check.check([write_tmp({"brand/blue": "#1069CF"})])
        self.assertEqual(r["findings"], [])
        self.assertIsNone(r["spacing"])


class CLI(unittest.TestCase):
    def test_json_cli(self):
        out = subprocess.check_output(
            [sys.executable, str(HERE / "token_check.py"), str(NODES), "--json"], text=True)
        data = json.loads(out)
        self.assertEqual(len(data["findings"]), 4)

    def test_text_cli_card_format(self):
        out = subprocess.check_output(
            [sys.executable, str(HERE / "token_check.py"), str(NODES),
             "--file-url", "https://figma.com/design/AbC123/Home"], text=True)
        self.assertIn("[T1 · MEDIUM]", out)
        self.assertIn("Fix: ", out)
        self.assertIn("Figma: https://figma.com/design/AbC123/Home?node-id=", out)
        self.assertIn("Backs: Material 4dp/8dp grid", out)


if __name__ == "__main__":
    unittest.main()
