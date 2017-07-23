# -*- coding: utf-8 -*-
from vk_requests.session import VKSession
from vk_requests.api import API


__version__ = '0.9.9'


def create_api(app_id=None, login=None, password=None, phone_number=None,
               timeout=10, scope='offline', api_version=None,
               interactive=False, **method_default_args):
    """Factory method to explicitly create API with app_id, login, password
    and phone_number parameters.

    If the app_id, login, password are not passed, then token-free session
    will be created automatically

    :param app_id: int: vk application id, more info: https://vk.com/dev/main
    :param login: str: vk login
    :param password: str: vk password
    :param phone_number: str: phone number with country code (+71234568990)
    :param timeout: int: api timeout in seconds
    :param scope: str or list of str: vk session scope
    :param api_version: str: vk api version, check https://vk.com/dev/versions
    :param interactive: bool: flag which indicates to use InteractiveVKSession
    :param method_default_args: api kwargs
    :return: api instance
    :rtype : vk_requests.api.API
    """

    session = VKSession(app_id=app_id,
                        user_login=login,
                        user_password=password,
                        phone_number=phone_number,
                        scope=scope,
                        api_version=api_version,
                        interactive=interactive)
    return API(session=session, timeout=timeout, **method_default_args)


# Set default logging handler to avoid "No handler found" warnings.
import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger('vk-requests').addHandler(NullHandler())
