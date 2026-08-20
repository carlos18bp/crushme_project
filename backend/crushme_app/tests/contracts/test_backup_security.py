from copy import deepcopy
from pathlib import Path
from stat import S_IMODE

import pytest
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import StorageHandler


@pytest.fixture
def saved_backup(tmp_path):
    backends = deepcopy(settings.STORAGES)
    backends['dbbackup']['OPTIONS']['location'] = tmp_path
    storage = StorageHandler(backends=backends)['dbbackup']

    name = storage.save('nested/backup.dump', ContentFile(b'private backup'))

    return Path(storage.path(name)), tmp_path / 'nested'


def test_backup_storage_creates_owner_only_files(saved_backup):
    backup_path, _ = saved_backup

    assert S_IMODE(backup_path.stat().st_mode) == 0o600


def test_backup_storage_creates_owner_only_directories(saved_backup):
    _, backup_directory = saved_backup

    assert S_IMODE(backup_directory.stat().st_mode) == 0o700
