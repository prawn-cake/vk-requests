# -*- coding: utf-8 -*-
import logging


logger = logging.getLogger('vk-requests')


class API(object):
    def __init__(self, session, http_params=None):
        """

        :param session: vk_requests.session.VKSession instance
        :param http_params: dict: requests HTTP parameters
        """
        self._session = session
        self._http_params = http_params
        if http_params is None:
            self._http_params = dict(timeout=10)

    @property
    def version(self):
        return self._session.api_version

    def __getattr__(self, method_name):
        return Request(session=self._session,
                       method_name=method_name,
                       http_params=self._http_params)


class Request(object):
    __slots__ = ('_session', 'http_params', '_method_name', '_method_args')

    def __init__(self, session, method_name, http_params):
        """
        :param session: vk_requests.session.VKSession instance
        :param method_name: str: method name
        """
        self._session = session
        self._method_name = method_name
        self._method_args = None  # will be set with __call__ execution
        self.http_params = http_params

    @property
    def method_name(self):
        return self._method_name

    @method_name.setter
    def method_name(self, val):
        raise AttributeError('method_name is immutable')

    @property
    def method_args(self):
        return self._method_args

    @method_args.setter
    def method_args(self, val):
        raise AttributeError('method_args is immutable')

    def __getattr__(self, method_name):
        new_method = '.'.join([self._method_name, method_name])
        return Request(session=self._session,
                       method_name=new_method,
                       http_params=self.http_params)

    def __call__(self, **method_args):
        self._method_args = method_args
        return self._session.make_request(request=self)

    def __repr__(self):  # pragma: no cover
        return "%s(method='%s', args=%s)" % (
            self.__class__.__name__,
            self.method_name,
            self.method_args)
