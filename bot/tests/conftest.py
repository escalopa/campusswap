"""Storage fixtures: every database test runs on SQLite, and also on Firestore when configured.

Firestore tests need a real (test) database:
  CAMPUSSWAP_FIRESTORE_TEST_PROJECT=<gcp project>  CAMPUSSWAP_FIRESTORE_TEST_DATABASE=test  pytest
Each test writes under a unique collection prefix and deletes its data afterwards.
"""

from __future__ import annotations

import os
import uuid

import pytest

from campusswap_bot.db import Database

FS_PROJECT = os.environ.get("CAMPUSSWAP_FIRESTORE_TEST_PROJECT")
FS_DATABASE = os.environ.get("CAMPUSSWAP_FIRESTORE_TEST_DATABASE", "test")
BACKENDS = ["sqlite", pytest.param("firestore", marks=pytest.mark.skipif(not FS_PROJECT, reason="no Firestore test project"))]


def _credentials():
    """Application Default Credentials if set up, otherwise the current `gcloud` login."""
    import subprocess

    import google.auth
    from google.oauth2.credentials import Credentials

    try:
        google.auth.default()
        return None
    except google.auth.exceptions.DefaultCredentialsError:
        token = subprocess.run(["gcloud", "auth", "print-access-token"], check=True, capture_output=True, text=True)
        return Credentials(token.stdout.strip())


class _Firestore:
    def __init__(self):
        from campusswap_bot.firestore_db import FirestoreDatabase

        self.prefix = f"t_{uuid.uuid4().hex[:8]}_"
        self._db = FirestoreDatabase(project=FS_PROJECT, database=FS_DATABASE, prefix=self.prefix,
                                     credentials=_credentials())

    def db(self):
        return self._db

    def cleanup(self):
        for col in self._db.client.collections():
            if col.id.startswith(self.prefix):
                for doc in col.list_documents():
                    doc.delete()


@pytest.fixture(params=BACKENDS)
def make_db(request, tmp_path):
    if request.param == "sqlite":
        yield lambda: Database(tmp_path / "t.db")
        return
    fs = _Firestore()
    yield fs.db
    fs.cleanup()


@pytest.fixture
def firestore_env():
    if not FS_PROJECT:
        pytest.skip("no Firestore test project")
    fs = _Firestore()
    yield fs
    fs.cleanup()
