# -*- coding: utf-8 -*-
import logging
import os

log_level = os.getenv('VK_REQUESTS_TEST_LOG_LEVEL', 'INFO')

logging.basicConfig(
    level=getattr(logging, log_level.upper()),
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
)
