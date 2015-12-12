
from vk_requests.auth import InteractiveVKSession, VKSession
from vk_requests.api import API


__version__ = '0.9.0'


def create_api(app_id=None, login=None, password=None, phone_number=None,
               timeout=10, **method_default_args):
    """Factory method to explicitly create API with app_id, login, password
    and phone_number parameters.
    If it's not passed (app_id, login, password) - token-free session will be
    created automatically

    :return: api instance
    :rtype : vk_requests.api.API
    """
    session = VKSession(app_id, login, password, phone_number=phone_number)
    return API(session=session, timeout=timeout, **method_default_args)