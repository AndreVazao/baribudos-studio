from __future__ import annotations

import unittest
from unittest.mock import patch

from studio_core.services import production_pipeline_service as pipeline


class ProductionPipelineRuntimeTests(unittest.TestCase):
    def test_auto_pipeline_loads_ip_runtime_before_factory_execution(self) -> None:
        project = {
            "id": "project-runtime-test",
            "title": "História de teste",
            "saga_slug": "baribudos",
            "language": "pt-PT",
        }
        runtime = {
            "slug": "baribudos",
            "name": "Os Baribudos",
            "validation": {"ok": True},
        }
        factory_result = {
            "story": {"title": "História de teste", "raw_text": "Texto de teste."},
            "language_variants": {"pt-PT": {"status": "needs_review"}},
            "cover": None,
            "ebook": {},
            "audiobook": {},
            "video": {},
            "guide": None,
            "summary": {"project_id": "project-runtime-test"},
        }
        updated_project = {**project, "production": {"state": "completed"}}

        with patch.object(pipeline, "_get_project", return_value=project), patch.object(
            pipeline, "load_ip_runtime", return_value=runtime
        ) as load_runtime, patch.object(
            pipeline, "run_project_factory_engine", return_value=factory_result
        ) as run_factory, patch.object(
            pipeline, "_update_project_outputs", return_value=updated_project
        ), patch.object(pipeline, "append_json_item"):
            result = pipeline.run_production_pipeline("project-runtime-test", {"mode": "auto"})

        load_runtime.assert_called_once_with("baribudos")
        run_factory.assert_called_once()
        self.assertTrue(result["ok"])
        self.assertEqual(result["state"], "completed")
        self.assertEqual(result["runtime"]["slug"], "baribudos")
        self.assertEqual(result["project"], updated_project)


if __name__ == "__main__":
    unittest.main()
