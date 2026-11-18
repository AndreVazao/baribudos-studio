from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from studio_core.services.saga_runtime_service import _normalize_characters_master, validate_saga_runtime


class CharacterIdentityRuntimeTests(unittest.TestCase):
    def test_legacy_baribudos_characters_are_not_dropped_without_name_field(self) -> None:
        source = {
            "visual_dna": {
                "body_shape": "small_rounded",
                "fur_style": "short_soft",
                "eyes": "large_expressive",
                "nose": "small_round",
                "hands": "4_fingers",
                "feet": "short",
                "ears": "small_rounded",
                "texture": "soft_fuzzy",
            },
            "color_rules": {"fur_base": "#8B5E3C", "eye_color": "#3A7D44"},
            "family": [
                {"id": "magnus", "role": "father", "archetype": "mentor_protector", "personality": ["calm"], "scarf_color": "#2F5E2E"},
                {"id": "luma", "role": "mother", "archetype": "emotional_intuition", "personality": ["empathetic"], "scarf_color": "#6FA86A"},
                {"id": "roko", "role": "child", "age": 11, "personality": ["responsible"], "scarf_color": "#D4A73C"},
                {"id": "mila", "role": "child", "age": 6, "personality": ["curious"], "scarf_color": "#F4A259"},
                {"id": "tilo", "role": "child", "age": 4, "personality": ["curious"], "scarf_color": "#9BD770"},
            ],
        }

        normalized = _normalize_characters_master(source)
        family = normalized["family"]

        self.assertEqual([item["id"] for item in family], ["magnus", "luma", "roko", "mila", "tilo"])
        self.assertEqual([item["name"] for item in family], ["Magnus", "Luma", "Roko", "Mila", "Tilo"])
        self.assertEqual(family[0]["traits"], ["calm"])
        self.assertEqual(family[0]["identity_invariants"]["body_shape"], "small_rounded")
        self.assertEqual(family[0]["identity_invariants"]["fur_base"], "#8B5E3C")
        self.assertEqual(family[0]["identity_invariants"]["scarf_color"], "#2F5E2E")
        self.assertEqual(family[0]["visual_package"]["status"], "not_created")
        self.assertTrue(normalized["identity_policy"]["identity_invariants_locked"])

    def test_duplicate_character_ids_are_not_duplicated_in_runtime(self) -> None:
        normalized = _normalize_characters_master({
            "family": [
                {"id": "mila", "role": "child"},
                {"id": "mila", "name": "Mila duplicate", "role": "child"},
            ]
        })
        self.assertEqual(len(normalized["family"]), 1)
        self.assertEqual(normalized["family"][0]["name"], "Mila")

    def test_production_ready_ip_is_blocked_without_approved_visual_assets(self) -> None:
        runtime = {
            "slug": "test-ip",
            "name": "Test IP",
            "metadata": {},
            "palette": {},
            "permissions": {"status": "production_ready"},
            "canons": {
                "characters": {"family": [{"id": "hero", "visual_package": {"status": "not_created"}}]},
                "narrative": {},
                "visual": {},
            },
            "resolved": {},
        }
        result = validate_saga_runtime(runtime)
        self.assertFalse(result["ok"])
        self.assertIn(
            "character.hero.visual_package_not_approved_or_incomplete",
            result["errors"],
        )

    def test_draft_ip_receives_warning_instead_of_production_error(self) -> None:
        runtime = {
            "slug": "test-ip",
            "name": "Test IP",
            "metadata": {},
            "palette": {},
            "permissions": {"status": "draft"},
            "canons": {
                "characters": {"family": [{"id": "hero", "visual_package": {"status": "not_created"}}]},
                "narrative": {},
                "visual": {},
            },
            "resolved": {},
        }
        result = validate_saga_runtime(runtime)
        self.assertTrue(result["ok"])
        self.assertIn(
            "character.hero.visual_package_not_approved_or_incomplete",
            result["warnings"],
        )



    def test_existing_approved_visual_package_assets_survive_normalization(self) -> None:
        source = {
            "family": [{
                "id": "hero",
                "name": "Hero",
                "visual_package": {
                    "status": "approved",
                    "approved_revision": "hero-v1",
                    "model_source": "characters/hero/model.blend",
                    "rig_asset": "characters/hero/rig.blend",
                    "expression_sheet": "characters/hero/expressions.png",
                    "neutral_pose": "characters/hero/neutral.png",
                    "turnaround": {
                        "front": "characters/hero/front.png",
                        "three_quarter": "characters/hero/three-quarter.png",
                        "side": "characters/hero/side.png",
                        "back": "characters/hero/back.png",
                    },
                    "wardrobe_assets": ["characters/hero/wardrobe/default.blend"],
                },
            }],
        }

        normalized = _normalize_characters_master(source)
        package = normalized["family"][0]["visual_package"]

        self.assertEqual(package["status"], "approved")
        self.assertEqual(package["approved_revision"], "hero-v1")
        self.assertEqual(package["model_source"], "characters/hero/model.blend")
        self.assertEqual(package["rig_asset"], "characters/hero/rig.blend")
        self.assertEqual(package["expression_sheet"], "characters/hero/expressions.png")
        self.assertEqual(package["neutral_pose"], "characters/hero/neutral.png")
        self.assertEqual(package["turnaround"]["back"], "characters/hero/back.png")
        self.assertEqual(package["wardrobe_assets"], ["characters/hero/wardrobe/default.blend"])

    def test_complete_approved_visual_package_passes_production_gate(self) -> None:
        asset_paths = {
            "model_source": "characters/hero/model.blend",
            "rig_asset": "characters/hero/rig.blend",
            "expression_sheet": "characters/hero/expressions.png",
            "neutral_pose": "characters/hero/neutral.png",
            "turnaround.front": "characters/hero/front.png",
            "turnaround.three_quarter": "characters/hero/three-quarter.png",
            "turnaround.side": "characters/hero/side.png",
            "turnaround.back": "characters/hero/back.png",
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            checksums = {}
            for key, relative_path in asset_paths.items():
                asset = root / relative_path
                asset.parent.mkdir(parents=True, exist_ok=True)
                asset.write_bytes(f"approved-asset:{key}".encode("utf-8"))
                checksums[key] = hashlib.sha256(asset.read_bytes()).hexdigest()

            package = {
                "status": "approved",
                "approved_revision": "hero-v1",
                "model_source": asset_paths["model_source"],
                "rig_asset": asset_paths["rig_asset"],
                "expression_sheet": asset_paths["expression_sheet"],
                "neutral_pose": asset_paths["neutral_pose"],
                "turnaround": {
                    "front": asset_paths["turnaround.front"],
                    "three_quarter": asset_paths["turnaround.three_quarter"],
                    "side": asset_paths["turnaround.side"],
                    "back": asset_paths["turnaround.back"],
                },
                "asset_checksums": checksums,
            }
            runtime = {
                "slug": "test-ip",
                "name": "Test IP",
                "metadata": {},
                "palette": {},
                "permissions": {"status": "production_ready"},
                "root_path": str(root),
                "canons": {
                    "characters": {"family": [{"id": "hero", "visual_package": package}]},
                    "narrative": {},
                    "visual": {},
                },
                "resolved": {},
            }

            result = validate_saga_runtime(runtime)
            self.assertTrue(result["ok"], result["errors"])
            self.assertFalse(any("character.hero.visual_package" in item for item in result["errors"]))

            package["asset_checksums"]["model_source"] = "0" * 64
            mismatch_result = validate_saga_runtime(runtime)
            self.assertFalse(mismatch_result["ok"])
            self.assertTrue(any("SHA-256 não corresponde" in item for item in mismatch_result["errors"]))

            package["asset_checksums"]["model_source"] = checksums["model_source"]
            package["model_source"] = "../outside/model.blend"
            traversal_result = validate_saga_runtime(runtime)
            self.assertFalse(traversal_result["ok"])
            self.assertTrue(any("fora da diretoria canónica" in item for item in traversal_result["errors"]))



if __name__ == "__main__":
    unittest.main()
