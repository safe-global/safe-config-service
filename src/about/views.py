from rest_framework.response import Response
from rest_framework.views import APIView

from config import settings
from version import __name__


class AboutView(APIView):
    def get(self, request, format=None):
        response = {
            "name": __name__,
            "version": settings.application_version,
            "api_version": self.request.version,
            "secure": self.request.is_secure(),
        }
        return Response(response)
