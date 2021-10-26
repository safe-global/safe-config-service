from django.apps import AppConfig


class AppsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "safe_apps"

    def ready(self) -> None:
        import safe_apps.signals  # noqa: F401
