# -*- coding: utf-8 -*-
import logging


logger = logging.getLogger('vk-requests')


class API(object):
    def __init__(self, session, timeout=10, **default_request_kwargs):
        self._session = session
        self._timeout = timeout
        self._default_request_kwargs = default_request_kwargs

    def get_default_kwargs(self):
        """Getter method.
        It is used in vk_requests.session.VKSession.send_api_request

        :return: copy of default requests kwargs dict
        """
        return self._default_request_kwargs.copy()

    def __getattr__(self, method_name):
        return Request(session=self._session,
                       method_name=method_name,
                       timeout=self._timeout)


class Request(object):
    __slots__ = ('_session', 'timeout', '_method_name', '_method_args')

    def __init__(self, session, method_name, timeout=10):
        """
        
        :param session: vk_requests.session.VKSession instance 
        :param method_name: str: method name
        """
        self._session = session
        self._method_name = method_name
        self._method_args = None  # will be set with __call__ execution
        self.timeout = timeout

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
                       timeout=self.timeout)

    def __call__(self, **method_args):
        self._method_args = method_args
        return self._session.make_request(request_obj=self)

    def __repr__(self):  # pragma: no cover
        return "%s(method='%s', args=%s)" % (
            self.__class__.__name__,
            self.method_name,
            self.method_args)
