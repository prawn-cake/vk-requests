# coding=utf8

import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
)
logger = logging.getLogger('vk-requests')


class API(object):
    def __init__(self, session, timeout=10, **default_request_kwargs):
        self._session = session
        self._timeout = timeout
        self._default_request_kwargs = default_request_kwargs

    def get_default_kwargs(self):
        """Getter method.
        It is used in vk_requests.auth.VKSession.send_api_request

        :return: copy of default requests kwargs dict
        """
        return self._default_request_kwargs.copy()

    def get_timeout(self):
        return self._timeout

    def make_request(self, request_obj):
        """Make http request. This method is being called from Request object

        :param request_obj: vk_requests.api.Request
        :return: dict | VkAPIError
        """
        return self._session.make_request(request_obj)

    def __getattr__(self, method_name):
        return Request(self, method_name)


class Request(object):
    __slots__ = ('_api', '_method_name', '_method_args')

    def __init__(self, api, method_name):
        self._api = api
        self._method_name = method_name
        self._method_args = None  # will be set with __call__ execution

    def get_api(self):
        return self._api

    def get_method_name(self):
        return self._method_name

    def get_method_args(self):
        return self._method_args

    def __getattr__(self, method_name):
        return Request(self._api, '.'.join([self._method_name, method_name]))

    def __call__(self, **method_args):
        self._method_args = method_args
        return self._api.make_request(request_obj=self)

    def __repr__(self):  # pragma: no cover
        return "%s(method='%s', args=%s)" % (
            self.__class__.__name__, self.get_method_name(),
            self.get_method_args())
