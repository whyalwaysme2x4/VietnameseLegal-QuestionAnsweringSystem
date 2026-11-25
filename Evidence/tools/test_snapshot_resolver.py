"""Regression tests for historical hash resolution; no external services."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from snapshot_resolver import resolve_artifact


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.live=self.root/'app.py';self.live.write_bytes(b'current')
        self.archive=self.root/'Evidence/_history/W07/app.py';self.archive.parent.mkdir(parents=True)
        self.archive.write_bytes(b'previous')
        self.digest=hashlib.sha256(b'previous').hexdigest()
        self.index=self.root/'Evidence/_history/index.json'
        self.record={'week':'W07','path':'app.py','sha256':self.digest,'snapshot_path':'Evidence/_history/W07/app.py'}
        self.save()
    def save(self):self.index.write_text(json.dumps({'entries':[self.record]}),encoding='utf-8')
    def tearDown(self):self.temp.cleanup()
    def test_current_match_preferred(self):
        self.assertEqual(resolve_artifact(self.root,'W07','app.py',hashlib.sha256(b'current').hexdigest()),self.live)
    def test_exact_old_snapshot_resolved(self):
        self.assertEqual(resolve_artifact(self.root,'W07','app.py',self.digest),self.archive)
    def test_tampered_snapshot_not_accepted(self):
        self.archive.write_bytes(b'tampered')
        self.assertEqual(resolve_artifact(self.root,'W07','app.py',self.digest),self.live)
    def test_new_week_cannot_use_old_snapshot(self):
        self.assertEqual(resolve_artifact(self.root,'W08','app.py',self.digest),self.live)
    def test_outside_path_rejected(self):
        with self.assertRaises(ValueError):resolve_artifact(self.root,'W07','../escape',self.digest)
    def test_snapshot_path_outside_archive_not_accepted(self):
        (self.root/'untrusted.py').write_bytes(b'previous')
        self.record['snapshot_path']='untrusted.py';self.save()
        self.assertEqual(resolve_artifact(self.root,'W07','app.py',self.digest),self.live)


if __name__=='__main__':unittest.main()
