
from vk_requests.auth import InteractiveVKSession, VKSession
from vk_requests.api import API


__version__ = '0.9.6'


def create_api(app_id=None, login=None, password=None, phone_number=None,
               timeout=10, scope='offline', api_version=None,
               session_cls=VKSession, **method_default_args):
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
    :param api_version: str: vk api version
    :param session_cls: VKSession: session implementation class
    :param method_default_args: api kwargs
    :return: api instance
    :rtype : vk_requests.api.API
    """
    session = session_cls(app_id, login, password, phone_number=phone_number,
                          scope=scope, api_version=api_version)
    return API(session=session, timeout=timeout, **method_default_args)