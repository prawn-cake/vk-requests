# -*- coding: utf-8 -*-
import time
import unittest

import mock
import six

import vk_requests
from vk_requests.api import API
from vk_requests.auth import BaseAuthAPI, AuthAPI, InteractiveVKSession, \
    InteractiveAuthAPI
from vk_requests.exceptions import VkAPIError, VkParseError, \
    VkPageWarningsError
from vk_requests.settings import APP_ID, USER_LOGIN, USER_PASSWORD, \
    PHONE_NUMBER
from vk_requests.tests.test_base import get_fixture
from vk_requests.utils import VerboseHTTPSession


class VkApiInstanceTest(unittest.TestCase):
    def test_create_api_without_token(self):
        api = vk_requests.create_api()
        self.assertIsInstance(api, API)
        self.assertIsNone(api._session.auth_api._access_token)

    def test_create_api_with_token(self):
        api = vk_requests.create_api(
            app_id=APP_ID, login=USER_LOGIN, password=USER_PASSWORD,
            phone_number=PHONE_NUMBER)
        self.assertIsInstance(api, API)

        # Check that we have got access token on init
        self.assertIsInstance(
            api._session.auth_api._access_token, six.string_types)

    def test_create_api_with_custom_api_version(self):
        api = vk_requests.create_api(api_version='5.00')
        self.assertEqual(api._session.auth_api.api_version, '5.00')

    @mock.patch('vk_requests.utils.VerboseHTTPSession.request')
    def test_send_request_with_custom_api_version(self, mock_request):
        """Steps:
            * Check default api version value per api request
            * Check custom default api version per api request
            * Check overridden api version within request

        """
        # Expect default version to being passed
        api = vk_requests.create_api()
        api.users.get(user_id=1)
        url_data, params = tuple(mock_request.call_args_list[0])
        self.assertEqual(params['data']['v'], BaseAuthAPI.DEFAULT_API_VERSION)
        mock_request.reset_mock()

        # Expect predefined version
        version = '3.00'
        api = vk_requests.create_api(api_version=version)
        api.users.get(user_id=1)
        url_data, params = tuple(mock_request.call_args_list[0])
        self.assertEqual(params['data']['v'], version)
        mock_request.reset_mock()

        # Override version in the requests
        version = '5.8'
        api.users.get(user_id=1, v=version)
        url_data, params = tuple(mock_request.call_args_list[0])
        self.assertEqual(params['data']['v'], version)


class VkTestCase(unittest.TestCase):
    def setUp(self):
        self.vk_api = vk_requests.create_api(lang='ru')

    @staticmethod
    def _create_api(**kwargs):
        return vk_requests.create_api(
            app_id=APP_ID,
            login=USER_LOGIN,
            password=USER_PASSWORD,
            **kwargs
        )

    def test_get_server_time(self):
        server_time = self.vk_api.getServerTime()
        self.assertTrue(int(server_time))

    def test_get_profiles_via_token(self):
        profiles = self.vk_api.users.get(user_id=1)
        self.assertEqual(profiles[0]['last_name'], u'Дуров')

    def test_users_search(self):
        request_opts = dict(
            city=2,
            age_from=18,
            age_to=50,
            offset=0,
            count=1000,
            fields=['screen_name'])

        # Expect api error because search method requires access token
        with self.assertRaises(VkAPIError) as err:
            resp = self.vk_api.users.search(**request_opts)
            self.assertIsNone(resp)
            self.assertIn('no access_token passed', str(err))

        # Create token-based API
        api = self._create_api()
        resp = api.users.search(**request_opts)
        self.assertIsInstance(resp, dict)
        total_num, items = resp['count'], resp['items']
        self.assertIsInstance(total_num, int)
        for item in items:
            self.assertIsInstance(item, dict)
            self.assertIn('screen_name', item)

    def test_get_friends(self):
        items = self.vk_api.friends.get(
            fields=['nickname', 'city', 'can_see_all_posts'],
            user_id=1)
        self.assertIsInstance(items, dict)
        friends = items['items']
        for item in friends:
            if 'deactivated' in item:
                # skip deactivated users, they don't have extra fields
                continue
            self.assertIsInstance(item, dict)

            # User can hide this field
            # self.assertIn('city', item)
            self.assertIn('nickname', item)
            self.assertIn('id', item)
            self.assertIn('can_see_all_posts', item)

    @unittest.skip('Custom method test')
    def test_execute(self):
        api = self._create_api()
        resp = api.execute.wallMultiGet(user1=1)
        items = resp[0]
        for item in items:
            print(item)

    def test_set_status(self):
        """Test requires scope='status' vk permissions
        """
        status_text = 'Welcome to noagent.168.estate'
        api = self._create_api(scope=['offline', 'status'])
        self.assertEqual(api._session.auth_api.scope, ['offline', 'status'])

        # Set the status
        resp = api.status.set(text=status_text)
        self.assertEqual(resp, 1)

        # Check the status
        resp = api.status.get()
        self.assertEqual(resp, {'text': status_text})

    def test_multi_scope_requests(self):
        api = self._create_api(scope=['messages', 'status'])
        resp = api.status.get()
        self.assertIn('text', resp)

        resp = api.messages.get()
        self.assertIsInstance(resp, dict)
        total_msg, msg_list = resp['count'], resp['items']
        self.assertIsInstance(total_msg, int)
        for msg in msg_list:
            self.assertIsInstance(msg, dict)

    def test_likes_get_list(self):
        api = self._create_api()
        resp = api.likes.getList(type='post', owner_id=1, item_id=815649)
        self.assertIn('count', resp)
        self.assertIn('items', resp)
        for user_id in resp['items']:
            self.assertIsInstance(user_id, int)


class AuthAPITest(unittest.TestCase):
    def setUp(self):
        self.patch_api = lambda api_method: \
            mock.patch('vk_requests.auth.AuthAPI.%s' % api_method)

    def test_init(self):
        auth_api = AuthAPI()
        self.assertIsInstance(auth_api, AuthAPI)

    def test_init_with_login_param(self):
        with self.patch_api('renew_access_token') as renew_access_token:
            auth_api = AuthAPI(user_login='test')
            self.assertEqual(auth_api._login, 'test')
            self.assertEqual(renew_access_token.call_count, 1)

    def test_check_interactive_api_renew_token_is_called_once(self):
        with self.patch_api('renew_access_token') as renew_access_token:
            # Fill user, password and app_id to init without prompt
            auth_api = InteractiveAuthAPI(user_login='test',
                                          user_password='test',
                                          app_id=1234)
            self.assertIsInstance(auth_api, InteractiveAuthAPI)
            self.assertEqual(renew_access_token.call_count, 1)

    @staticmethod
    def get_mocked_session(name='session', action=None):
        """Get mocked session with prepared cookies and text properties
        """
        if action is None:
            action = '/login.php?act=security_check&to=&hash=4b07a450e9f22038b'
        session = mock.MagicMock(name=name, spec=VerboseHTTPSession)

        # Set cookies mock
        cookies = {'remixsid': 'test'}
        type(session).cookies = mock.PropertyMock(return_value=cookies)

        # Mock 'text' property on get
        form = '<form method="post" action="%s"></form>' % action
        get_response = mock.MagicMock()
        type(get_response).text = mock.PropertyMock(return_value=form)
        session.get = mock.Mock(return_value=get_response)
        return session

    def test_do_login_require_captcha(self):
        # Prepare mocked parameters
        auth_api = AuthAPI()
        session = self.get_mocked_session()

        # Mock 'url' property on post to call require_captcha
        url = 'http://test/?sid=test123&test=1'
        post_response = mock.MagicMock()
        type(post_response).url = mock.PropertyMock(return_value=url)
        session.post = mock.Mock(return_value=post_response)

        # Do login, expect require captcha method being called
        with mock.patch('vk_requests.auth.AuthAPI.require_auth_captcha') as \
                require_captcha:
            auth_api.do_login(session=session)
            self.assertTrue(require_captcha.called)
            call_params = dict(tuple(require_captcha.call_args_list[0])[1])
            keys = ('query_params', 'form_text', 'login_form_data', 'session')
            for k in keys:
                self.assertIn(k, call_params)
            self.assertEqual(call_params['query_params'],
                             {'sid': 'test123', 'test': '1'})

    def test_do_login_require_2fa(self):
        auth_api = AuthAPI()
        session = self.get_mocked_session(name='2fa_session')

        # Mock 'url' property on post to call get_2fa_code
        url = 'http://test/?act=authcheck&test=1'
        login_response = mock.MagicMock(name='login_response')
        form = '<form method="post" action="/login?act=authcheck_code' \
               '&hash=1234567890_ff181e72e9db30cbc3"></form>'
        type(login_response).url = mock.PropertyMock(return_value=url)
        type(login_response).text = mock.PropertyMock(return_value=form)
        session.post = mock.Mock(return_value=login_response)

        with self.patch_api('get_2fa_code') as get_2fa_code:
            get_2fa_code.return_value = 1234
            auth_api.do_login(session=session)
            self.assertTrue(get_2fa_code.called)
            call_2fa = dict(tuple(session.post.call_args_list[-1])[1])

            # Check that 2fa http call was done with correct url and data
            self.assertEqual(call_2fa['url'],
                             'https://m.vk.com/login?act=authcheck_code&'
                             'hash=1234567890_ff181e72e9db30cbc3')
            self.assertEqual(call_2fa['data'],
                             {'_ajax': '1', 'code': 1234, 'remember': '1'})

    def test_do_login_require_phone_number(self):
        auth_api = AuthAPI()
        session = self.get_mocked_session()

        # Mock 'url' property on post to call require_phone_number
        url = 'http://test/?act=security_check&test=1'
        post_response = mock.MagicMock()
        type(post_response).url = mock.PropertyMock(return_value=url)
        session.post = mock.Mock(return_value=post_response)

        with self.patch_api('require_phone_number') as require_pn:
            auth_api.do_login(session=session)
            self.assertTrue(require_pn.called)
            call_params = dict(tuple(require_pn.call_args_list[0])[1])
            keys = ('html', 'session')
            for k in keys:
                self.assertIn(k, call_params)

    def test_require_phone_number_with_auto_resolving(self):
        """Test require_phone_number with auto resolving security check.
        Expect that the method will parse given phone number and send
        confirmation request

        """
        auth_api = AuthAPI(phone_number='+123456789')
        html = get_fixture('require_phone_num_resp.html')
        session_mock = mock.Mock()
        auth_api.require_phone_number(html=html, session=session_mock)
        self.assertEqual(session_mock.post.call_count, 1)
        call = tuple(session_mock.post.call_args_list[0])[1]
        self.assertEqual(call['data']['act'], 'security_check')
        self.assertEqual(call['data']['code'], '567')

    def test_require_phone_number_with_auto_resolving_warn(self):
        """Test require_phone_number with auto resolving security check when vk
        returns warning message like:
        'Incorrect numbers. You can repeat the attempt in 3 hours.'

        """
        auth_api = AuthAPI(phone_number='+123456789')
        html = get_fixture('require_phone_num_warn_resp.html')
        session_mock = mock.Mock()
        with self.assertRaises(VkPageWarningsError) as err:
            auth_api.require_phone_number(html=html, session=session_mock)
            self.assertIn(
                'Incorrect numbers. You can repeat the attempt in 3 hours',
                str(err))

    @unittest.skip('Require console input')
    def test_interactive_session_init(self):
        session = InteractiveVKSession()
        api = API(session=session, timeout=10)
        self.assertIsInstance(api, API)

    def test_do_login_no_action_url(self):
        auth_api = AuthAPI()
        session = self.get_mocked_session(action='')

        with self.assertRaises(VkParseError) as err:
            auth_api.do_login(session=session)
            self.assertIn("Can't parse form action url", str(err))