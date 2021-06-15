from rest_framework.response import Response
from rest_framework.views import APIView

from version import __name__, __version__


class AboutView(APIView):
    def get(self, request, format=None):
        response = {
            "name": __name__,
            "version": __version__,
            "api_version": self.request.version,
            "secure": self.request.is_secure(),
        }
        return Response(response)
