"""Offline ComfyUI bridge tests; do not need a running server or GPU."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
PATH = HERE / "scripts" / "comfyui_bridge.py"
spec = importlib.util.spec_from_file_location("comfyui_bridge", PATH)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

WORKFLOW = {
    "1": {"class_type": "CLIPTextEncode", "inputs": {"text": "original", "clip": ["5", 1]}},
    "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "negative", "clip": ["5", 1]}},
    "3": {"class_type": "KSampler", "inputs": {"seed": 42, "steps": 25}},
    "4": {"class_type": "EmptyLatentImage", "inputs": {"batch_size": 3, "width": 768, "height": 1152}},
}
IDS = {"positive_node": "1", "negative_node": "2", "sampler_node": "3", "latent_node": "4"}

class ComfyBridgeTests(unittest.TestCase):
    def test_mapping_isolated_and_single_batch(self):
        result = bridge.prepare(WORKFLOW, IDS, "fresh concept", 123, "low quality")
        self.assertEqual(result["1"]["inputs"]["text"], "fresh concept")
        self.assertEqual(result["2"]["inputs"]["text"], "low quality")
        self.assertEqual(result["3"]["inputs"]["seed"], 123)
        self.assertEqual(result["4"]["inputs"]["batch_size"], 1)
        self.assertEqual(WORKFLOW["1"]["inputs"]["text"], "original")
        self.assertEqual(WORKFLOW["4"]["inputs"]["batch_size"], 3)

    def test_missing_nodes_fail_before_submit(self):
        with self.assertRaises(ValueError):
            bridge.prepare(WORKFLOW, {**IDS, "positive_node": "999"}, "x", 10)

    def test_only_local_comfy_endpoint(self):
        for url in ("https://evil.com", "http://192.168.0.4:8188", "file:///etc/passwd"):
            with self.assertRaises(ValueError):
                bridge.validate_base(url)
        self.assertEqual(bridge.validate_base("http://127.0.0.1:8188/"), "http://127.0.0.1:8188")

    def test_seeds_reproducible_and_distinct(self):
        self.assertEqual(bridge.job_seed(1000, 1), bridge.job_seed(1000, 1))
        self.assertNotEqual(bridge.job_seed(1000, 1), bridge.job_seed(1000, 2))

    def test_manifest_respects_style_and_count(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            prompts = root / "prompts"
            prompts.mkdir()
            (prompts / "character-01.md").write_text("## Locked independent blueprint", encoding="utf-8")
            manifest = {"render_style": "anime-2d", "designs": [{"id": "one", "number": 1}], "master_seed": 9}
            self.assertEqual(len(bridge.validate_manifest(manifest, prompts, 1)), 1)
            with self.assertRaises(ValueError):
                bridge.validate_manifest(manifest, prompts, 2)

    def test_dry_run_does_not_need_server(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "prompts").mkdir()
            (root / "prompts" / "character-01.md").write_text(
                "# One original character sheet\n## Locked independent blueprint\n- Narrative role: sculptor\n"
                "## PRESELECTED RENDERING STYLE\n- Style ID: anime-2d\n", encoding="utf-8")
            (root / "manifest.json").write_text(json.dumps({
                "render_style": "anime-2d", "master_seed": 112,
                "designs": [{"id": "test-1", "number": 1}]}), encoding="utf-8")
            (root / "workflow.json").write_text(json.dumps(WORKFLOW), encoding="utf-8")
            code = bridge.main(["--manifest", str(root / "manifest.json"), "--workflow", str(root / "workflow.json"),
                                "--positive-node", "1", "--negative-node", "2", "--sampler-node", "3",
                                "--latent-node", "4", "--count", "1", "--dry-run",
                                "--ledger", str(root / "jobs.json")])
            self.assertEqual(code, 0)
            self.assertFalse((root / "jobs.json").exists())

if __name__ == "__main__":
    unittest.main()
