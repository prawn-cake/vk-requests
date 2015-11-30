
from vk_requests.api import logger
from vk_requests.auth import InteractiveVKSession, VKSession
from vk_requests.api import API


__version__ = '0.9.0'


def create_api(app_id=None, login=None, password=None, timeout=10,
               **method_default_args):
    """Factory method to explicitly create API with app_id, login and
    password parameters.
    If those are not passed - token-free session will be created
    automatically

    :return: vk_requests.api.API api
    """
    session = VKSession(app_id, login, password)
    return API(session=session, timeout=timeout, **method_default_args)