import logging
import time

from django.http import HttpRequest


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("LoggingMiddleware")

    @staticmethod
    def get_milliseconds_now():
        return int(time.time() * 1000)

    def __call__(self, request: HttpRequest):
        # before view (and other middleware) are called
        milliseconds = self.get_milliseconds_now()

        response = self.get_response(request)

        # after view is called
        if request.resolver_match:
            route = (
                request.resolver_match.route if request.resolver_match else request.path
            )
            self.logger.info(
                "MT::%s::%s::%s::%d::%s",
                request.method,
                route,
                self.get_milliseconds_now() - milliseconds,
                response.status_code,
                request.path,
            )
        return response
