from __future__ import annotations

import unittest
from unittest.mock import patch

from studio_core.services import job_service


class JobServiceOwnershipTests(unittest.TestCase):
    def test_created_job_persists_project_and_creator_as_first_class_fields(self):
        with patch.object(job_service, "read_json", return_value=[]), patch.object(job_service, "write_json") as write:
            job = job_service.create_job("render", {
                "project_id": "project-1",
                "created_by": "user-1",
                "user_id": "attacker",
                "user_role": "owner",
            })
        self.assertEqual(job["project_id"], "project-1")
        self.assertEqual(job["created_by"], "user-1")
        self.assertEqual(job["payload"]["user_id"], "attacker")
        self.assertEqual(write.call_args.args[1][0]["project_id"], "project-1")
        self.assertEqual(write.call_args.args[1][0]["created_by"], "user-1")


if __name__ == "__main__":
    unittest.main()
