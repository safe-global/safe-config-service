import shutil
import tempfile

import pytest


@pytest.fixture(autouse=True)
def use_file_system_storage(settings):
    settings.DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"


@pytest.fixture(autouse=True)
def use_tmp_media_root(settings):
    # Creates tmp directory for tests
    settings.MEDIA_ROOT = tempfile.mkdtemp()

    yield  # run test

    # After running each test remove the tmp directory
    shutil.rmtree(settings.MEDIA_ROOT)
