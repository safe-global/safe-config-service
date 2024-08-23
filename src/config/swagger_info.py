from drf_yasg import openapi

SAFE_CONFIG_SERVICE_SWAGGER_INFO = openapi.Info(
    title="Safe Config Service API",
    default_version="v1",
    description="Service that provides configuration information in the context of the Safe clients environment",
    license=openapi.License(name="MIT License"),
)
