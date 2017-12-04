# -*- coding: utf-8 -*-

import logging
import logging.handlers
import os
import sys
from datetime import datetime

def init_logger(filename="", add_timestamp=True):
    if add_timestamp:
        current_time = datetime.now()
        file_timestamp = current_time.strftime('%Y%m%d%H%M%S')
    else :
        file_timestamp = ""

    logger = logging.getLogger("Hotsan_diary")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler((os.path.join(os.path.expanduser("~"), 'Desktop','CarpeDM2017', 'Logs', filename+file_timestamp+'.log')))
    sh = logging.StreamHandler()
    er = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter(fmt ='%(asctime)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    er.setFormatter(formatter)
    er.setLevel(logging.WARNING)

    logger.addHandler(fh)
    logger.addHandler(sh)
    logger.addHandler(er)

    return logger
