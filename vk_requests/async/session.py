# -*- coding: utf-8 -*-
import aiohttp
import copy

import logging

from vk_requests import VKSession
from vk_requests.auth import AuthAPI
from vk_requests.exceptions import VkAuthError, VkParseError
from vk_requests.utils import stringify_values, parse_form_action_url, \
    parse_url_query_params

logger = logging.getLogger('vk-requests-async')


class AsyncVKSession(VKSession):
    """Aiohttp empowered VKSession"""

    @property
    def http_session(self):
        """HTTP session getter

        :return: aiohttp.ClientSession instance
        """
        if self._http_session is None:
            session = aiohttp.ClientSession(
                headers=copy.copy(self.DEFAULT_HTTP_HEADERS))
            self._http_session = session
        return self._http_session

    async def _get_access_token(self):
        if not all([self.app_id, self._login, self._password]):
            raise ValueError(
                'app_id=%s, login=%s password=%s (masked) must be given'
                % (self.app_id, self._login,
                   '*' * len(self._password) if self._password else 'None'))

        logger.info("Getting access token for user '%s'" % self._login)
        async with self.http_session as s:
            await self.do_login(http_session=s)
            url_query_params = await self.do_oauth2_authorization(session=s)
            logger.debug('url_query_params: %s', url_query_params)

        if 'access_token' in url_query_params:
            logger.info('Access token has been gotten')
            return url_query_params['access_token']
        else:
            raise VkAuthError('OAuth2 authorization error. Url params: %s'
                              % url_query_params)

    async def do_oauth2_authorization(self, session):
        """ OAuth2 authorization method. It's used for getting access token
        More info: https://vk.com/dev/auth_mobile
        """

        logger.info('Doing oauth2, app_id=%s', self.app_id)
        auth_data = {
            'client_id': self.app_id,
            'display': 'mobile',
            'response_type': 'token',
            'scope': self.scope,
            'v': self.api_version
        }
        async with session.post(url=self.AUTHORIZE_URL,
                                data=stringify_values(auth_data)) as response:
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
            async with session.get(action_url) as response:
                url_query_params = parse_url_query_params(response.url)
            return url_query_params
        try:
            response_json = await response.json()
        except ValueError:  # not JSON in response
            error_message = 'OAuth2 grant access error'
            logger.error(await response.text)
        else:
            error_message = 'VK error: [{}] {}'.format(
                response_json['error'], response_json['error_description'])
        logger.error('Permissions obtained')
        raise VkAuthError(error_message)

    async def do_login(self, http_session):
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
        act = response_url_query.get('act')
        logger.debug('response_url_query: %s', response_url_query)

        # Check response url query params firstly
        if 'sid' in response_url_query:
            self.require_auth_captcha(
                query_params=response_url_query,
                form_text=login_response.text,
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
