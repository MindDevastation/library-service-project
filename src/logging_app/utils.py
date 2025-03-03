import logging
import traceback
from logging_app.models import ErrorLog, ActionLog

logger = logging.getLogger(__name__)


def log_error(exception, request=None):
    tb_str = "".join(
        traceback.format_exception(None, exception, exception.__traceback__)
    )
    path = request.path if request else "N/A"

    ErrorLog.objects.create(
        level="ERROR",
        message=str(exception),
        traceback=tb_str,
        request_path=path,
    )

    logger.error(f"Error: {exception}", exc_info=True)
