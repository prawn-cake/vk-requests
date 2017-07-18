# -*- coding: utf-8 -*-
"""Test settings"""

import os

# Set your environment variables for testing or put values here

# user email or phone number
USER_LOGIN = os.getenv('VK_USER_LOGIN', '')
USER_PASSWORD = os.getenv('VK_USER_PASSWORD', '')
# aka API/Client ID
APP_ID = os.getenv('VK_APP_ID')
PHONE_NUMBER = os.getenv('VK_PHONE_NUMBER')
