import logging
import sys

def setup_logging():
    """Configure structured logging for production."""
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    
    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        datefmt=datefmt,
        stream=sys.stdout,
        force=True,
    )
    
    # Silence noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("snap7").setLevel(logging.WARNING)
    logging.getLogger("pymodbus").setLevel(logging.WARNING)
    logging.getLogger("pylogix").setLevel(logging.WARNING)
