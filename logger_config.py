import os
import logging

from queue import SimpleQueue
from logging.handlers import TimedRotatingFileHandler, QueueHandler, QueueListener


cwd = os.path.dirname(os.path.abspath(__file__))


def setup_logger(name=None, log_dir=cwd, level=logging.INFO):
    """
    Set up a logger for the library, optimized for production use.

    Args:
    - name: Name of the logger.
    - log_dir: Directory where log files should be stored. If None, logs will be displayed to console.
    - level: Logging level. By default, it's set to logging.INFO.

    Returns:
    - A configured logger instance.
    """
    # Get or create a logger
    logger = logging.getLogger(name if name else __name__)

    # If the logger has handlers, it's already set up and we don't want to duplicate handlers
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Using a Queue to enable asynchronous logging
    log_queue = SimpleQueue()
    queue_handler = QueueHandler(log_queue)
    logger.addHandler(queue_handler)

    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            os.path.join(log_dir, "maths.log"),
            when="midnight",
            interval=1,
            backupCount=7,
        )
        file_handler.setFormatter(formatter)
    else:
        file_handler = logging.StreamHandler()
        file_handler.setFormatter(formatter)

    # The QueueListener will asynchronously handle logs
    queue_listener = QueueListener(log_queue, file_handler)
    queue_listener.start()

    return logger
