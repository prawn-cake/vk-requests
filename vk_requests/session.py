# -*- coding: utf-8 -*-

import logging

from six.moves import input as raw_input

from vk_requests.exceptions import VkAuthError, VkAPIError, VkParseError
from vk_requests.utils import parse_url_query_params, VerboseHTTPSession, \
    parse_form_action_url, stringify_values, parse_masked_phone_number, \
    check_html_warnings, parse_captcha_html

try:
    import ujson as json
except ImportError:
    import json


logger = logging.getLogger('vk-requests')


class VKSession(object):
    API_URL = 'https://api.vk.com/method/'
    DEFAULT_HTTP_HEADERS = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    LOGIN_URL = 'https://m.vk.com'
    AUTHORIZE_URL = 'https://oauth.vk.com/authorize'
    DIRECT_AUTHORIZE_URL = 'https://oauth.vk.com/token'
    CAPTCHA_URI = 'https://api.vk.com/captcha.php'

    def __init__(self, app_id=None, user_login=None, user_password=None,
                 phone_number=None, scope='offline', api_version=None,
                 interactive=False, service_token=None, client_secret=None,
                 two_fa_supported=False, two_fa_force_sms=False):
        """IMPORTANT: (app_id + user_login + user_password) and service_token
        are mutually exclusive

        """
        self.app_id = app_id
        self._login = user_login
        self._password = user_password
        self._phone_number = phone_number
        self._service_token = service_token
        self.scope = scope
        self.interactive = interactive
        self._access_token = None
        self._api_version = api_version
        self._client_secret = client_secret
        self._two_fa_supported = two_fa_supported
        self._two_fa_force_sms = two_fa_force_sms

        # requests.Session subclass instance
        self._http_session = None

        # Some API methods get args (e.g. user id) from access token.
        # If we define user login, we need get access token now.
        if self._login:
            self.renew_access_token()

    @property
    def http_session(self):
        """HTTP Session property

        :return: vk_requests.utils.VerboseHTTPSession instance
        """
        if self._http_session is None:
            session = VerboseHTTPSession()
            session.headers.update(self.DEFAULT_HTTP_HEADERS)
            self._http_session = session
        return self._http_session

    @property
    def api_version(self):
        return self._api_version

    def is_token_required(self):
        """Helper method for vk_requests.auth.VKSession initialization

        :return: bool
        """
        return any([self.app_id, self._login, self._password])

    def do_login(self, http_session):
        """Do vk login

        :param http_session: vk_requests.utils.VerboseHTTPSession: http session
        """

        response = http_session.get(self.LOGIN_URL)
        action_url = parse_form_action_url(response.text)

        # Stop login it action url is not found
        if not action_url:
            logger.debug(response.text)
            raise VkParseError("Can't parse form action url")

        login_form_data = {'email': self._login, 'pass': self._password}
        login_response = http_session.post(action_url, login_form_data)
        logger.debug('Cookies: %s', http_session.cookies)

        response_url_query = parse_url_query_params(
            login_response.url, fragment=False)

        logger.debug('response_url_query: %s', response_url_query)
        act = response_url_query.get('act')

        # Check response url query params firstly
        if 'sid' in response_url_query:
            self.require_auth_captcha(
                response=login_response,
                query_params=response_url_query,
                login_form_data=login_form_data,
                http_session=http_session)

        elif act == 'authcheck':
            self.require_2fa(html=login_response.text,
                             http_session=http_session)

        elif act == 'security_check':
            self.require_phone_number(html=login_response.text,
                                      session=http_session)

        session_cookies = ('remixsid' in http_session.cookies,
                           'remixsid6' in http_session.cookies)
        if any(session_cookies):
            logger.info('VK session is established')
            return True
        else:
            message = 'Authorization error: incorrect password or ' \
                      'authentication code'
            logger.error(message)
            raise VkAuthError(message)

    def do_implicit_flow_authorization(self, session):
        """ Standard OAuth2 authorization method. It's used for getting access token
        More info: https://vk.com/dev/implicit_flow_user
        """
        logger.info('Doing implicit flow authorization, app_id=%s', self.app_id)
        auth_data = {
            'client_id': self.app_id,
            'display': 'mobile',
            'response_type': 'token',
            'scope': self.scope,
            'redirect_uri': 'https://oauth.vk.com/blank.html',
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

    def do_direct_authorization(self, session):
        """ Direct Authorization, more info: https://vk.com/dev/auth_direct """
        logger.info('Doing direct authorization, app_id=%s', self.app_id)
        auth_data = {
            'client_id': self.app_id,
            'client_secret': self._client_secret,
            'username': self._login,
            'password': self._password,
            'grant_type': 'password',
            '2fa_supported': self._two_fa_supported,
            'scope': self.scope,
            'v': self.api_version
        }
        response = session.post(url=self.DIRECT_AUTHORIZE_URL,
                                data=stringify_values(auth_data))
        try:
            response_json = response.json()
        except ValueError:  # not JSON in response
            error_message = 'OAuth2 grant access error'
            logger.error(response.text)
            raise VkAuthError(error_message)
        else:
            if 'access_token' in response_json:
                return response_json

            if response_json['error'] == 'need_validation':
                return self.direct_auth_require_2fa(session, auth_data)
            elif response_json['error'] == 'need_captcha':
                return self.direct_auth_require_captcha(session, response_json, auth_data)
            else:
                error_message = 'VK error: [{}] {}'.format(
                    response_json['error'], response_json['error_description'])
                raise VkAuthError(error_message)

    def direct_auth_require_2fa(self, session, auth_data):
        if self._two_fa_force_sms:
            auth_data['force_sms'] = self._two_fa_force_sms
            session.post(url=self.DIRECT_AUTHORIZE_URL,
                         data=stringify_values(auth_data))
        logger.info(
            'User enabled 2 factors authentication. Auth check code is needed '
            '(SMS, Google Authenticator or one-time password generated by vk)')
        auth_data['code'] = self.get_2fa_code()
        response = session.post(url=self.DIRECT_AUTHORIZE_URL,
                                data=stringify_values(auth_data))
        try:
            response_json = response.json()
        except ValueError: # not JSON in response
            error_message = 'OAuth2 grant access error'
            logger.error(response.text)
            raise VkAuthError(error_message)
        return response_json

    def direct_auth_require_captcha(self, session, response, auth_data):
        logger.info('Captcha is needed. Response: %s', response)

        captcha_url = response['captcha_img']
        logger.info('Captcha url %s', captcha_url)

        auth_data['captcha_sid'] = response['captcha_sid']
        auth_data['captcha_key'] = self.get_captcha_key(captcha_url)

        response = session.post(url=self.DIRECT_AUTHORIZE_URL,
                                data=stringify_values(auth_data))
        try:
            response_json = response.json()
        except ValueError: # not JSON in response
            error_message = 'OAuth2 grant access error'
            logger.error(response.text)
            raise VkAuthError(error_message)
        return response_json

    def require_2fa(self, html, http_session):
        logger.info(
            'User enabled 2 factors authentication. Auth check code is needed '
            '(SMS, Google Authenticator or one-time password generated by vk)')
        action_url = parse_form_action_url(html)
        auth_check_code = self.get_2fa_code()
        auth_check_data = {
            'code': auth_check_code,
            '_ajax': '1',
            'remember': '1'
        }
        url = '/'.join([self.LOGIN_URL + action_url])
        response = http_session.post(url=url, data=auth_check_data)
        return response

    def require_auth_captcha(self, response, query_params,
                             login_form_data, http_session):
        """Resolve auth captcha case

        :param response: http response
        :param query_params: dict: response query params, for example:
        {'s': '0', 'email': 'my@email', 'dif': '1', 'role': 'fast', 'sid': '1'}

        :param login_form_data: dict
        :param http_session: requests.Session
        :return: :raise VkAuthError:
        """
        logger.info('Captcha is needed. Query params: %s', query_params)
        form_text = response.text

        action_url = parse_form_action_url(form_text)
        logger.debug('form action url: %s', action_url)
        if not action_url:
            raise VkAuthError('Cannot find form action url')

        captcha_sid, captcha_url = parse_captcha_html(
            html=response.text, response_url=response.url)
        logger.info('Captcha url %s', captcha_url)

        login_form_data['captcha_sid'] = captcha_sid
        login_form_data['captcha_key'] = self.get_captcha_key(captcha_url)

        response = http_session.post(action_url, login_form_data)
        return response

    def require_phone_number(self, html, session):
        logger.info(
            'Auth requires phone number. You do login from unusual place')

        # Raises VkPageWarningsError in case of warnings
        # NOTE: we check only 'security_check' case on warnings for now
        # in future it might be extended for other cases as well
        check_html_warnings(html=html)

        # Determine form action url
        action_url = parse_form_action_url(html)

        # Get masked phone from html to make things more clear
        phone_prefix, phone_suffix = parse_masked_phone_number(html)

        if self._phone_number:
            code = self._phone_number[len(phone_prefix):-len(phone_suffix)]
        else:
            if self.interactive:
                prompt = 'Enter missing digits of your phone number (%s****%s): '\
                            % (phone_prefix, phone_suffix)
                code = raw_input(prompt)
            else:
                raise VkAuthError(
                    'Phone number is required. Create an API instance using '
                    'phone_number parameter or use interactive mode')

        params = parse_url_query_params(action_url, fragment=False)
        auth_data = {
            'code': code,
            'act': 'security_check',
            'hash': params['hash']}
        response = session.post(
            url=self.LOGIN_URL + action_url, data=auth_data)
        logger.debug('require_phone_number resp: %s', response.text)

    def get_2fa_code(self):
        if self.interactive:
            auth_check_code = raw_input('Auth check code: ')
            return auth_check_code.strip()
        else:
            raise VkAuthError(
                'Auth check code is needed (SMS, Google Authenticator or '
                'one-time password). '
                'Use interactive mode to enter the code manually')

    @property
    def access_token(self):
        if self._access_token is None:
            self._access_token = self._get_access_token()
        return self._access_token

    def _get_access_token(self):
        """Get access token using app_id, login and password OR service token
        (service token docs: https://vk.com/dev/service_token
        """
        if self._service_token:
            logger.info('Use service token: %s',
                        5 * '*' + self._service_token[50:])
            return self._service_token

        if not all([self.app_id, self._login, self._password]):
            raise ValueError(
                'app_id=%s, login=%s password=%s (masked) must be given'
                % (self.app_id, self._login,
                   '*' * len(self._password) if self._password else 'None'))

        logger.info("Getting access token for user '%s'" % self._login)
        with self.http_session as s:
            if self._client_secret:
                url_query_params = self.do_direct_authorization(session=s)
            else:
                self.do_login(http_session=s)
                url_query_params = self.do_implicit_flow_authorization(session=s)
            logger.debug('url_query_params: %s', url_query_params)

        if 'access_token' in url_query_params:
            logger.info('Access token has been gotten')
            return url_query_params['access_token']
        else:
            raise VkAuthError('OAuth2 authorization error. Url params: %s'
                              % url_query_params)

    def get_captcha_key(self, captcha_image_url):
        """Read CAPTCHA key from user input"""

        if self.interactive:
            print('Open CAPTCHA image url in your browser and enter it below: ',
                  captcha_image_url)
            captcha_key = raw_input('Enter CAPTCHA key: ')
            return captcha_key
        else:
            raise VkAuthError(
                'Captcha is required. Use interactive mode to enter it '
                'manually')

    def renew_access_token(self):
        """Force to get new access token

        """
        self._access_token = self._get_access_token()

    def make_request(self, request, captcha_response=None):
        """Make api request helper function

        :param request: vk_requests.api.Request instance
        :param captcha_response: None or dict, e.g {'sid': <sid>, 'key': <key>}
        :return: dict: json decoded http response
        """
        logger.debug('Prepare API Method request %r', request)
        response = self._send_api_request(request=request,
                                          captcha_response=captcha_response)
        response.raise_for_status()
        response_or_error = json.loads(response.text)
        logger.debug('response: %s', response_or_error)

        if 'error' in response_or_error:
            error_data = response_or_error['error']
            vk_error = VkAPIError(error_data)

            if vk_error.is_captcha_needed():
                captcha_key = self.get_captcha_key(vk_error.captcha_img_url)
                if not captcha_key:
                    raise vk_error

                # Retry http request with captcha info attached
                captcha_response = {
                    'sid': vk_error.captcha_sid,
                    'key': captcha_key,
                }
                return self.make_request(
                    request, captcha_response=captcha_response)

            elif vk_error.is_access_token_incorrect():
                logger.info(
                    'Authorization failed. Access token will be dropped')
                self._access_token = None
                return self.make_request(request)

            else:
                raise vk_error
        elif 'execute_errors' in response_or_error:
            # can take place while running .execute vk method
            # See more: https://vk.com/dev/execute
            raise VkAPIError(response_or_error['execute_errors'][0])
        elif 'response' in response_or_error:
            return response_or_error['response']

    def _send_api_request(self, request, captcha_response=None):
        """Prepare and send HTTP API request

        :param request: vk_requests.api.Request instance
        :param captcha_response: None or dict 
        :return: HTTP response
        """
        url = self.API_URL + request.method_name

        # Prepare request arguments
        method_kwargs = {'v': self.api_version}

        # Shape up the request data
        for values in (request.method_args,):
            method_kwargs.update(stringify_values(values))

        if self.is_token_required() or self._service_token:
            # Auth api call if access_token hadn't been gotten earlier
            method_kwargs['access_token'] = self.access_token

        if captcha_response:
            method_kwargs['captcha_sid'] = captcha_response['sid']
            method_kwargs['captcha_key'] = captcha_response['key']

        http_params = dict(url=url,
                           data=method_kwargs,
                           **request.http_params)
        logger.debug('send_api_request:http_params: %s', http_params)
        response = self.http_session.post(**http_params)
        return response

    def __repr__(self):  # pragma: no cover
        return "%s(api_url='%s', access_token='%s')" % (
            self.__class__.__name__, self.API_URL, self._access_token)
