import asyncio
import tempfile
import unittest
from pathlib import Path

from app.evidence_pipeline.contracts.evidence import Observation
from app.evidence_pipeline.persistence.sqlite import SQLiteEvidenceRepository


class ObservationPersistenceTests(unittest.TestCase):
    def test_duplicate_observation_ids_are_saved_once(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = SQLiteEvidenceRepository(f"sqlite:///{Path(directory) / 'test.db'}")
            observation = Observation(
                observation_id="obs_duplicate", source_id="src_1", predicate="location",
                object_text="Austin", observed_at="2026-01-01T00:00:00Z",
                source_url="https://example.com/profile", extraction_model="test", extraction_version="1",
            )
            asyncio.run(repository.save_investigation_observations("inv_1", [observation, observation]))
            self.assertEqual(len(repository.get_observations("inv_1")), 1)


if __name__ == "__main__":
    unittest.main()
