from django.http import JsonResponse
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.deprecation import MiddlewareMixin
from logging_app.utils import log_error
from django.db import DatabaseError
from requests.exceptions import RequestException


class ExceptionLoggingMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        log_error(exception, request)

        if isinstance(exception, ValidationError):
            return JsonResponse(
                {"error": "Invalid data", "details": str(exception)}, status=400
            )
        elif isinstance(exception, RequestException):
            return JsonResponse(
                {"error": "External API error", "details": str(exception)}, status=502
            )
        elif isinstance(exception, DatabaseError):
            return JsonResponse(
                {"error": "Database failure", "details": str(exception)}, status=500
            )
        elif isinstance(exception, PermissionDenied):
            return JsonResponse({"error": "Permission denied"}, status=403)
        elif isinstance(exception, KeyError):
            return JsonResponse(
                {"error": "Missing required field", "details": str(exception)},
                status=400,
            )
        elif isinstance(exception, AttributeError):
            return JsonResponse(
                {"error": "Invalid attribute usage", "details": str(exception)},
                status=400,
            )
        elif isinstance(exception, TypeError):
            return JsonResponse(
                {"error": "Invalid data type", "details": str(exception)}, status=400
            )
        elif isinstance(exception, ValueError):
            return JsonResponse(
                {"error": "Invalid value", "details": str(exception)}, status=400
            )

        return JsonResponse({"error": "Something went wrong"}, status=500)
