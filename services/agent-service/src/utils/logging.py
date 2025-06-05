import logging
import colorlog

def setup_logger(level=logging.INFO):
    """
    Set up root logger and suppress verbose logs from dependencies.
    """
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s[%(asctime)s] - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    ))

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)

    # Silence noisy modules
    logging.getLogger("autogen_core").setLevel(logging.WARNING)
    logging.getLogger("autogen_core.events").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger by name after setup_logging().
    """
    return logging.getLogger(name)
