from drf_yasg import openapi

SAFE_CONFIG_SERVICE_SWAGGER_INFO = openapi.Info(
    title="Gnosis Safe Config Service API",
    default_version="v1",
    description="Service that provides configuration information in the context of the Safe clients environment",
    contact=openapi.Contact(email="safe@gnosis.io"),
    license=openapi.License(name="MIT License"),
)
