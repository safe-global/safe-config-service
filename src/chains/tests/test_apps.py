from django.core.exceptions import ImproperlyConfigured
from pytest_django.asserts import assertRaisesMessage

from chains.apps import _validate_storage_setup


# Overriding settings on app configuration seems to be quite complex
# ie.: using @override_settings in a typical TestCase might not have
# the intended effect due to the other on which Django initializes
# some internals.
#
# Therefore a settings fixture is used:
# https://pytest-django.readthedocs.io/en/latest/helpers.html#settings
#
# More reading:
# https://stackoverflow.com/questions/31148172/django-override-setting-used-in-appconfig-ready-function
# https://code.djangoproject.com/ticket/22002
def test_validate_storage_setup(settings) -> None:  # type: ignore[no-untyped-def]
    settings.STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
    }
    settings.AWS_ACCESS_KEY_ID = None
    settings.AWS_SECRET_ACCESS_KEY = None
    settings.AWS_STORAGE_BUCKET_NAME = None

    assertRaisesMessage(
        ImproperlyConfigured,
        "Storage set to S3 but AWS is not configured",
        _validate_storage_setup,
    )
