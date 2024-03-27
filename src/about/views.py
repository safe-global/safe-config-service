from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from version import __name__


class AboutView(APIView):
    def get(self, request, format=None):
        response = {
            "name": __name__,
            "version": settings.APPLICATION_VERSION,
            "api_version": self.request.version,
            "secure": self.request.is_secure(),
        }
        return Response(response)
