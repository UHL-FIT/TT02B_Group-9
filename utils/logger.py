import os
import sys
import logging
if getattr(sys, 'frozen', False):
    _BASE_DIR = os.path.join(os.path.expanduser("~"), "Supermarket_Data")
else:
    _BASE_DIR = os.path.dirname(os.path.dirname(__file__))
_LOG_DIR = os.path.join(_BASE_DIR, "data")
_LOG_FILE = os.path.join(_LOG_DIR, "supermarket.log")

def setup_logger(name="supermarket"):
    os.makedirs(_LOG_DIR, exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fmt_file = logging.Formatter("%(asctime)s | %(levelname)-8s | %(module)s.%(funcName)s | %(message)s", 
                                 datefmt = "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(fmt_file)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    fmt_console = logging.Formatter("[%(levelname)s]%(message)s")
    ch.setFormatter(fmt_console)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger