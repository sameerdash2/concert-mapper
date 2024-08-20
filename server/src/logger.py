# logger.py
# Set up the logger for use by other modules

import logging
import sys
from datetime import datetime
import pytz

def initialize_logger():
    file_handler = logging.FileHandler("cm.log")
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]

    # Set up Pacific time zone formatter
    TARGET_TZ = pytz.timezone("America/Los_Angeles")

    # Python makes this so convoluted, it's not even worth it
    class CustomFormatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            dt = datetime.fromtimestamp(record.created, TARGET_TZ)
            ms = dt.microsecond // 1000
            datefmt = f"%Y-%m-%d %H:%M:%S.{ms} %Z"
            return dt.strftime(datefmt)

    # Apply the formatter to handlers
    custom_formatter = CustomFormatter("[%(asctime)s] - %(levelname)s - %(message)s")
    for handler in handlers:
        handler.setFormatter(custom_formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=handlers
    )

    # Disable propagation of werkzeug server logs
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
