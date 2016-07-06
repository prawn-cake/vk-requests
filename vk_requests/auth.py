# coding=utf8

import abc
import logging

import six
from six.moves import input as raw_input

from vk_requests.exceptions import VkAuthError, VkAPIError, VkParseError
from vk_requests.utils import parse_url_query_params, VerboseHTTPSession, \
    parse_form_action_url, json_iter_parse, stringify_values, \
    parse_masked_phone_number, check_html_warnings

logger = logging.getLogger('vk-requests')


@six.add_metaclass(abc.ABCMeta)
class BaseAuthAPI(object):
    """"Base auth api interface"""

    LOGIN_URL = 'https://m.vk.com'
    # REDIRECT_URI = 'https://oauth.vk.com/blank.html'
    AUTHORIZE_URL = 'https://oauth.vk.com/authorize'
    CAPTCHA_URI = 'https://m.vk.com/captcha.php'
    DEFAULT_API_VERSION = '5.45'

    def __init__(self, app_id=None, user_login='', user_password='',
                 scope='offline', phone_number=None, api_version=None,
                 **kwargs):
        logger.debug('Init %s: %r', self.__class__.__name__, self)

        self.app_id = app_id
        self._login = user_login
        self._password = user_password
        self._kwargs = kwargs
        self.scope = scope
        self._access_token = None
        self._api_version = api_version

        # using for auto-authentication in case when it's required by login
        # form, for instance when you try to login from unusual place
        self._phone_number = phone_number

        # Some API methods get args (e.g. user id) from access token.
        # If we define user login, we need get access token now.
        if self._login:
            self.renew_access_token()

    def __repr__(self):  # pragma: no cover
        """This tricky method needs for tox tests. Otherwise it raises an
        AttributeError, haven't dug into this issue
        """
        params = {}
        attrs = ('app_id', 'login', '_kwargs')
        for attr in attrs:
            if hasattr(self, attr):
                params[attr] = getattr(self, attr)

        return '%s(%s)' % (
            self.__class__.__name__,
            ','.join(['%s=%s' % (k, v) for k, v in params.items()]))

    @property
    def api_version(self):
        return self._api_version or self.DEFAULT_API_VERSION

    def is_token_required(self):
        """Helper method for vk_requests.auth.VKSession initialization

        :return: bool
        """
        return any([self.app_id, self._login, self._password])

    @property
    def access_token(self):
        if self._access_token is None:
            self._access_token = self.get_access_token()
        return self._access_token

    def renew_access_token(self):
        """Force to get new access token

        """
        self._access_token = self.get_access_token()

    @abc.abstractmethod
    def get_access_token(self):
        """Implement this in subclasses

        """
        pass

    @abc.abstractmethod
    def get_sms_code(self):
        """Get sms code method when user enabled 2-factor auth

        """
        pass

    @staticmethod
    def get_captcha_key(captcha_image_url):
        """Default behavior on CAPTCHA is to raise exception if this method
        return None.
        Reload this in child if needed

        :param captcha_image_url: str
        """
        return None


class AuthAPI(BaseAuthAPI):
    """Default auth API"""

    def get_access_token(self):
        """
        Get access token using app id and user login and password.
        """

        if not all([self.app_id, self._login, self._password]):
            raise ValueError(
                'app_id=%s, login=%s password=%s (masked) must be given' % (
                    self.app_id, self._login, bool(self._password)))

        logger.info("Getting access token for user '%s'" % self._login)
        with VerboseHTTPSession() as s:
            self.do_login(session=s)
            url_query_params = self.do_oauth2_authorization(session=s)
            logger.debug('url_query_params: %s', url_query_params)

        if 'access_token' in url_query_params:
            logger.info('Done')
            return url_query_params['access_token']
        else:
            raise VkAuthError('OAuth2 authorization error')

    def do_login(self, session):
        """Do vk login

        :param session: vk_requests.utils.VerboseHTTPSession: http session
        """

        response = session.get(self.LOGIN_URL)
        action_url = parse_form_action_url(response.text)

        # Stop login it action url is not found
        if not action_url:
            logger.debug(response.text)
            raise VkParseError("Can't parse form action url")

        login_form_data = {'email': self._login, 'pass': self._password}
        response = session.post(action_url, login_form_data)
        logger.debug('Cookies: %s', session.cookies)

        response_url_query = parse_url_query_params(
            response.url, fragment=False)
        act = response_url_query.get('act')
        logger.debug('response_url_query: %s', response_url_query)

        # Check response url query params firstly
        if 'sid' in response_url_query:
            self.require_auth_captcha(
                query_params=response_url_query,
                form_text=response.text,
                login_form_data=login_form_data,
                session=session)

        elif act == 'authcheck':
            self.require_sms_code(html=response.text, session=session)

        elif act == 'security_check':
            self.require_phone_number(html=response.text, session=session)

        session_cookies = ('remixsid' in session.cookies,
                           'remixsid6' in session.cookies)
        if any(session_cookies):
            logger.info('Session is already established')
            return None
        else:
            message = 'Authorization error (incorrect password)'
            logger.error(message)
            raise VkAuthError(message)

    def do_oauth2_authorization(self, session):
        """ OAuth2. More info: https://vk.com/dev/auth_mobile
        """
        logger.info('Doing oauth2')
        auth_data = {
            'client_id': self.app_id,
            'display': 'mobile',
            'response_type': 'token',
            'scope': self.scope,
            'v': self.api_version
        }
        response = session.post(url=self.AUTHORIZE_URL,
                                data=stringify_values(auth_data))
        url_query_params = parse_url_query_params(response.url)
        if 'expires_in' in url_query_params:
            logger.info('Token will be expired in %s sec.' %
                        url_query_params['expires_in'])
        if 'access_token' in url_query_params:
            return url_query_params

        # Permissions are needed
        logger.info('Getting permissions')
        action_url = parse_form_action_url(response.text)
        logger.debug('Response form action: %s', action_url)

        if action_url:
            response = session.get(action_url)
            url_query_params = parse_url_query_params(response.url)
            return url_query_params
        try:
            response_json = response.json()
        except ValueError:  # not JSON in response
            error_message = 'OAuth2 grant access error'
            logger.error(response.text)
        else:
            error_message = 'VK error: [{}] {}'.format(
                response_json['error'], response_json['error_description'])
        logger.error('Permissions obtained')
        raise VkAuthError(error_message)

    def require_sms_code(self, html, session):
        logger.info('User enabled 2 factors authorization. '
                    'Auth check code is needed')
        action_url = parse_form_action_url(html)
        auth_check_code = self.get_sms_code()
        auth_check_data = {
            'code': auth_check_code,
            '_ajax': '1',
            'remember': '1'
        }
        response = session.post(action_url, data=auth_check_data)
        return response

    def require_auth_captcha(self, query_params, form_text, login_form_data,
                             session):
        """Resolve auth captcha case

        :param query_params: dict: response query params, for example:
        {'s': '0', 'email': 'my@email', 'dif': '1', 'role': 'fast', 'sid': '1'}

        :param form_text: str: raw form html data
        :param login_form_data: dict
        :param session: requests.Session
        :return: :raise VkAuthError:
        """
        logger.info('Captcha is needed')

        action_url = parse_form_action_url(form_text)
        logger.debug('form_url %s', action_url)
        if not action_url:
            raise VkAuthError('Cannot find form action url')

        captcha_url = '%s?s=%s&sid=%s' % (
            self.CAPTCHA_URI, query_params['s'], query_params['sid'])
        logger.info('Captcha url %s', captcha_url)

        login_form_data['captcha_sid'] = query_params['sid']
        login_form_data['captcha_key'] = self.get_captcha_key(captcha_url)

        response = session.post(action_url, login_form_data)
        return response

    def require_phone_number(self, html, session):
        logger.info(
            'Auth requires phone number. You do login from unusual place')

        # Raises VkPageWarningsError in case of warnings
        # NOTE: we check only 'security_check' case on warnings for now
        # in future it might be propagated to other cases as well
        check_html_warnings(html=html)

        # Determine form action url
        action_url = parse_form_action_url(html)

        # Get masked phone from html to make things more clear
        phone_prefix, phone_suffix = parse_masked_phone_number(html)

        if self._phone_number:
            code = self._phone_number[len(phone_prefix):-len(phone_suffix)]
        else:
            prompt = 'Enter missing digits of your phone number (%s****%s): '\
                        % (phone_prefix, phone_suffix)
            code = raw_input(prompt)

        params = parse_url_query_params(action_url, fragment=False)
        auth_data = {
            'code': code,
            'act': 'security_check',
            'hash': params['hash']}
        response = session.post(
            url=self.LOGIN_URL + action_url, data=auth_data)
        logger.debug('require_phone_number resp: %s', response.text)

    def get_sms_code(self):
        raise VkAuthError('Auth check code is needed')


class InteractiveAuthAPI(AuthAPI):
    """Interactive auth api with manual login, password, captcha management"""

    def __init__(self, **kwargs):
        super(InteractiveAuthAPI, self).__init__(**kwargs)
        self._login = InteractiveAuthAPI.get_user_login()
        self._password = InteractiveAuthAPI.get_user_password()
        self.app_id = kwargs.get('app_id')
        if not self.app_id:
            self.app_id = InteractiveAuthAPI.get_app_id()

        # Renew access token, cuz login is set
        self.renew_access_token()

    @staticmethod
    def get_user_login():
        user_login = raw_input('VK user login: ')
        return user_login.strip()

    @staticmethod
    def get_app_id():
        user_login = raw_input('VK app id: ')
        return int(user_login.strip())

    @staticmethod
    def get_user_password():
        import getpass

        user_password = getpass.getpass('VK user password: ')
        return user_password.strip()

    def get_access_token(self):
        logger.debug('InteractiveMixin.get_access_token()')
        access_token = super(InteractiveAuthAPI, self).get_access_token()
        if not access_token:
            access_token = raw_input('VK API access token: ')
        return access_token

    @staticmethod
    def get_captcha_key(captcha_image_url):
        """Read CAPTCHA key from user input
        """

        print('Open CAPTCHA image url: ', captcha_image_url)
        captcha_key = raw_input('Enter CAPTCHA key: ')
        return captcha_key

    def get_sms_code(self):
        """
        Read Auth code from shell
        """
        auth_check_code = raw_input('Auth check code: ')
        return auth_check_code.strip()


class VKSession(object):
    API_URL = 'https://api.vk.com/method/'
    DEFAULT_AUTH_API_CLS = AuthAPI

    def __init__(self, app_id=None, user_login=None, user_password=None,
                 phone_number=None, auth_api_cls=None, **api_kwargs):

        self.auth_api_cls = auth_api_cls or self.DEFAULT_AUTH_API_CLS
        self.auth_api = self.get_auth_api(app_id=app_id,
                                          login=user_login,
                                          password=user_password,
                                          phone_number=phone_number,
                                          **api_kwargs)
        self.censored_access_token = None

        # requests.Session subclass instance
        self.http_session = VerboseHTTPSession()
        self.http_session.headers['Accept'] = 'application/json'
        self.http_session.headers['Content-Type'] = \
            'application/x-www-form-urlencoded'

    def get_auth_api(self, app_id, login, password, phone_number,
                     **api_kwargs):
        """Get auth api instance"""

        if not issubclass(self.auth_api_cls, BaseAuthAPI):
            raise TypeError(
                'Wrong AUTH_API_CLS %s, must be subclass of %s' %
                (self.auth_api_cls, BaseAuthAPI.__name__, ))

        return self.auth_api_cls(app_id=app_id,
                                 user_login=login,
                                 user_password=password,
                                 phone_number=phone_number,
                                 **api_kwargs)

    @property
    def access_token(self):
        return self.auth_api.access_token

    @access_token.setter
    def access_token(self, value):
        self.auth_api._access_token = value
        if isinstance(value, six.string_types) and len(value) >= 12:
            self.censored_access_token = '{}***{}'.format(
                value[:4], value[-4:])
        else:
            self.censored_access_token = value
        logger.debug('access_token = %r', self.censored_access_token)

    def make_request(self, request_obj, captcha_response=None):
        logger.debug('Prepare API Method request %r', request_obj)
        response = self.send_api_request(request=request_obj,
                                         captcha_response=captcha_response)
        response.raise_for_status()

        # there are may be 2 dicts in one JSON
        # for example: "{'error': ...}{'response': ...}"
        for response_or_error in json_iter_parse(response.text):
            if 'error' in response_or_error:
                error_data = response_or_error['error']
                vk_error = VkAPIError(error_data)

                if vk_error.is_captcha_needed():
                    captcha_key = self.auth_api.get_captcha_key(
                        vk_error.captcha_img)

                    if not captcha_key:
                        raise vk_error

                    captcha_response = {
                        'sid': vk_error.captcha_sid,
                        'key': captcha_key,
                    }
                    return self.make_request(
                        request_obj, captcha_response=captcha_response)

                elif vk_error.is_access_token_incorrect():
                    logger.info(
                        'Authorization failed. Access token will be dropped')
                    self.access_token = None
                    return self.make_request(request_obj)

                else:
                    raise vk_error
            elif 'execute_errors' in response_or_error:
                # can take place while running .execute vk method
                # See more: https://vk.com/dev/execute
                raise VkAPIError(response_or_error['execute_errors'][0])
            elif 'response' in response_or_error:
                return response_or_error['response']

    def send_api_request(self, request, captcha_response=None):
        url = self.API_URL + request.get_method_name()
        vk_api = request.get_api()

        # Prepare request arguments
        method_kwargs = {'v': self.auth_api.api_version}
        for values in (vk_api.get_default_kwargs(), request.get_method_args()):
            method_kwargs.update(stringify_values(values))

        if self.auth_api.is_token_required():
            # Auth api call if access_token weren't be got earlier
            method_kwargs['access_token'] = self.access_token
        if captcha_response:
            method_kwargs['captcha_sid'] = captcha_response['sid']
            method_kwargs['captcha_key'] = captcha_response['key']

        response = self.http_session.post(
            url=url, data=method_kwargs, timeout=vk_api.get_timeout())
        return response

    def __repr__(self):  # pragma: no cover
        return "%s(api_url='%s', access_token='%s')" % (
            self.__class__.__name__, self.API_URL, self.auth_api._access_token)


class InteractiveVKSession(VKSession):
    DEFAULT_AUTH_API_CLS = InteractiveAuthAPI
