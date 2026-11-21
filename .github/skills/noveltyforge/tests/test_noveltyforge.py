"""Offline tests: python -m unittest discover -s .../tests -v"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "noveltyforge.py"
spec = importlib.util.spec_from_file_location("noveltyforge", SCRIPT)
opg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(opg)


def example_profile():
    # Fictitious user preferences for tests only, not the real author's tastes.
    return {
        "status": "confirmed", "confirmed_by_user": True,
        "confirmation_evidence": "User explicitly confirmed preferences during discussion.",
        "medium": "character reference sheets",
        "likes": ["expressive eyes", "cohesive material choices", "clear silhouette hierarchy"],
        "dislikes": ["over-repeated outfit architecture", "muddy face rendering"],
        "rated_examples": [{"label": "Example One", "appeal": 7}],
    }


class ProfileGateTests(unittest.TestCase):
    def test_template_is_rejected(self):
        obj = opg.load_json(SCRIPT.parents[1] / "references" / "profile-template.json")
        with self.assertRaises(opg.PreferenceError):
            opg.validate_profile(obj)

    def test_implicit_or_invented_preference_is_rejected(self):
        profile = example_profile()
        profile["confirmed_by_user"] = False
        with self.assertRaises(opg.PreferenceError):
            opg.validate_profile(profile)

    def test_not_enough_evidence_rejected(self):
        p = example_profile()
        p["dislikes"] = ["one dislike"]
        with self.assertRaises(opg.PreferenceError):
            opg.validate_profile(p)

    def test_ratings_or_summary_confirmation_required(self):
        p = example_profile()
        p["rated_examples"] = []
        with self.assertRaises(opg.PreferenceError):
            opg.validate_profile(p)
        p["preference_summary_confirmed"] = True
        self.assertEqual(len(opg.validate_profile(p)["likes"]), 3)

    def test_valid_profile(self):
        self.assertEqual(opg.validate_profile(example_profile())["status"], "confirmed")


class PlanningTests(unittest.TestCase):
    def test_aspects_seeded_independently(self):
        x = opg.make_candidate(20261121, 1, 1)
        y = opg.make_candidate(20261121, 1, 1)
        z = opg.make_candidate(20261121, 2, 1)
        self.assertEqual(x, y)
        self.assertNotEqual(x["rolls_1_to_1000"], z["rolls_1_to_1000"])
        self.assertTrue(all(1 <= n <= 1000 for n in x["rolls_1_to_1000"].values()))
        self.assertEqual(len(x["rolls_1_to_1000"]), len(opg.CATALOG) + 1)

    def test_plan_unique_roles_and_clothing(self):
        result = opg.create_plan(example_profile(), {"entries": []}, 10, 1024)
        ds = result["designs"]
        self.assertEqual(len({d["selected"]["role"] for d in ds}), 10)
        self.assertEqual(len({d["selected"]["garment_architecture"] for d in ds}), 10)
        self.assertEqual(len({d["id"] for d in ds}), 10)

    def test_avoid_history(self):
        p = example_profile()
        seed = 999
        initial = opg.create_plan(p, {"entries": []}, 1, seed)
        orig = initial["designs"][0]
        again = opg.create_plan(p, {"entries": [{"selected": orig["selected"]}]}, 1, seed)
        self.assertNotEqual(orig["selected"]["role"], again["designs"][0]["selected"]["role"])
        self.assertNotEqual(orig["selected"]["garment_architecture"], again["designs"][0]["selected"]["garment_architecture"])

    def test_prompt_has_actual_preference_evidence(self):
        d = opg.create_plan(example_profile(), {"entries": []}, 1, 1)["designs"][0]
        prompt = opg.make_prompt(d, example_profile())
        self.assertIn("expressive eyes", prompt)
        self.assertIn("muddy face rendering", prompt)
        self.assertIn("exactly one", prompt.lower())

    def test_unpersonalized_requires_explicit_disclaimer(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            out = base / "out"
            self.assertEqual(opg.main(["plan", "--count", "1", "--output", str(out)]), 2)
            self.assertEqual(opg.main(["plan", "--force-unpersonalized", "--count", "1",
                                       "--output", str(out)]), 2)
            self.assertFalse((out / "manifest.json").exists())

    def test_forced_mode_is_honestly_labeled_and_functional(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            out = base / "out"
            self.assertEqual(opg.main(["plan", "--force-unpersonalized", "--acknowledge-disclaimer",
                                       "--count", "2", "--seed", "874", "--output", str(out)]), 0)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["generation_mode"], "unpersonalized-forced")
            self.assertFalse(manifest["personalization_claimed"])
            self.assertIsNone(manifest["profile_digest"])
            prompt = (out / "prompts" / "character-01.md").read_text(encoding="utf-8")
            self.assertIn("NOT personalized", prompt)
            self.assertNotIn("The current user confirmed", prompt)

    def test_cli_record_requires_visual_check(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            manifest = opg.create_plan(example_profile(), {"entries": []}, 1, 44)
            (path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(opg.main(["record", "--manifest", str(path / "manifest.json"),
                                       "--index", "1", "--history", str(path / "history.json"),
                                       "--status", "accepted", "--notes", "Looks good"]), 2)
            self.assertEqual(opg.main(["record", "--manifest", str(path / "manifest.json"),
                                       "--index", "1", "--history", str(path / "history.json"),
                                       "--status", "accepted", "--notes", "Visually reviewed distinct shape",
                                       "--visual-check"]), 0)
            history = json.loads((path / "history.json").read_text(encoding="utf-8"))
            self.assertEqual(len(history["entries"]), 1)
            self.assertTrue(history["entries"][0]["visual_check_attested"])


if __name__ == "__main__":
    unittest.main()
