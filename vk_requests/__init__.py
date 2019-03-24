# -*- coding: utf-8 -*-
import sys
from vk_requests.session import VKSession
from vk_requests.api import API


__version__ = '1.2.0'


PY_VERSION = sys.version_info.major, sys.version_info.minor

if PY_VERSION < (3, 4):
    import warnings

    warnings.simplefilter('default')
    warnings.warn('Support of all python version less than 3.4 will be stopped '
                  'in 2.0.0, please migrate your code to python 3.4+',
                  DeprecationWarning)


def create_api(app_id=None, login=None, password=None, phone_number=None,
               scope='offline', api_version='5.92', http_params=None,
               interactive=False, service_token=None, client_secret=None,
               two_fa_supported=False, two_fa_force_sms=False):
    """Factory method to explicitly create API with app_id, login, password
    and phone_number parameters.

    If the app_id, login, password are not passed, then token-free session
    will be created automatically

    :param app_id: int: vk application id, more info: https://vk.com/dev/main
    :param login: str: vk login
    :param password: str: vk password
    :param phone_number: str: phone number with country code (+71234568990)
    :param scope: str or list of str: vk session scope
    :param api_version: str: vk api version, check https://vk.com/dev/versions
    :param interactive: bool: flag which indicates to use InteractiveVKSession
    :param service_token: str: new way of querying vk api, instead of getting
    oauth token
    :param http_params: dict: requests http parameters passed along
    :param client_secret: str: secure application key for Direct Authorization,
    more info: https://vk.com/dev/auth_direct
    :param two_fa_supported: bool: enable two-factor authentication for Direct Authorization,
    more info: https://vk.com/dev/auth_direct
    :param two_fa_force_sms: bool: force SMS two-factor authentication for Direct Authorization
    if two_fa_supported is True, more info: https://vk.com/dev/auth_direct
    :return: api instance
    :rtype : vk_requests.api.API
    """
    session = VKSession(app_id=app_id,
                        user_login=login,
                        user_password=password,
                        phone_number=phone_number,
                        scope=scope,
                        service_token=service_token,
                        api_version=api_version,
                        interactive=interactive,
                        client_secret=client_secret,
                        two_fa_supported = two_fa_supported,
                        two_fa_force_sms=two_fa_force_sms)
    return API(session=session, http_params=http_params)


# Set default logging handler to avoid "No handler found" warnings.
import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger('vk-requests').addHandler(NullHandler())
