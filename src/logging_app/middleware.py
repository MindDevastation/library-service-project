from django.utils.deprecation import MiddlewareMixin
from logging_app.utils import log_error


class ExceptionLoggingMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        log_error(exception, request)

        return None
