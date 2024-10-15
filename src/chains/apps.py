from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _validate_storage_setup() -> None:
    if (
        settings.STORAGES["default"]["BACKEND"]
        == "storages.backends.s3boto3.S3Boto3Storage"
        and settings.AWS_ACCESS_KEY_ID is None
        and settings.AWS_SECRET_ACCESS_KEY is None
        and settings.AWS_STORAGE_BUCKET_NAME is None
    ):
        raise ImproperlyConfigured("Storage set to S3 but AWS is not configured")


class AppsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chains"

    def ready(self) -> None:
        import chains.signals  # noqa: F401

        # This application depends on S3 configuration (if set)
        # so we validate if its django.conf.settings contains the required parameters
        _validate_storage_setup()
