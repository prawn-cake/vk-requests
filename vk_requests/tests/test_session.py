# -*- coding: utf-8 -*-
import unittest
import six
try:
    from unittest import mock
except ImportError:
    import mock

from vk_requests import settings
from vk_requests.exceptions import VkPageWarningsError, VkParseError
from vk_requests import VKSession
from vk_requests.tests.test_base import get_fixture
from vk_requests.utils import VerboseHTTPSession


class VKSessionTest(unittest.TestCase):
    def setUp(self):
        self.patch_api = lambda api_method: \
            mock.patch('vk_requests.VKSession.%s' % api_method)

    @staticmethod
    def get_real_vk_session(**kwargs):
        return VKSession(app_id=settings.APP_ID,
                         user_login=settings.USER_LOGIN,
                         user_password=settings.USER_PASSWORD,
                         phone_number=settings.PHONE_NUMBER, **kwargs)

    def test_session_init(self):
        session = self.get_real_vk_session()
        # Expect no errors
        self.assertIsInstance(session, VKSession)

        # Token is required, cuz auth params are being passed
        self.assertTrue(session.is_token_required)

    def test_access_token_property(self):
        # Check token getter
        session = self.get_real_vk_session()
        self.assertTrue(session.access_token)
        self.assertIsInstance(session.access_token, six.string_types)

    def test_init_with_login_param(self):
        with self.patch_api('renew_access_token') as renew_access_token:
            vk_session = VKSession(user_login='test')
            self.assertEqual(vk_session._login, 'test')
            self.assertEqual(renew_access_token.call_count, 1)

    def test_check_interactive_api_renew_token_is_called_once(self):
        with self.patch_api('renew_access_token') as renew_access_token:
            # Fill user, password and app_id to init without prompt
            vk_session = VKSession(user_login='test',
                                   user_password='test',
                                   app_id=1234)
            self.assertIsInstance(vk_session, VKSession)
            self.assertEqual(renew_access_token.call_count, 1)

    @staticmethod
    def get_mocked_http_session(name='session', action=None):
        """Get mocked session with prepared cookies and text properties
        """
        if action is None:
            action = '/login.php?act=security_check&to=&hash=4b07a450e9f22038b'
        session = mock.MagicMock(name=name, spec=VerboseHTTPSession)

        # Set cookies mock
        session.configure_mock(cookies={'remixsid': 'test'})

        # Mock 'text' property on get
        form = '<form method="post" action="%s"></form>' % action
        get_response = mock.MagicMock()
        get_response.configure_mock(text=form)
        session.get = mock.Mock(return_value=get_response)
        return session

    def test_do_login_require_captcha(self):
        # Prepare mocked parameters
        vk_session = VKSession()
        session = self.get_mocked_http_session()

        # Mock 'url' property on post to call require_captcha
        url = 'http://test/?sid=test123&test=1'
        post_response = mock.MagicMock()
        post_response.configure_mock(url=url)
        session.post = mock.Mock(return_value=post_response)

        # Do login, expect require captcha method being called
        with mock.patch('vk_requests.VKSession.require_auth_captcha') as \
                require_captcha:
            vk_session.do_login(http_session=session)
            self.assertTrue(require_captcha.called)
            call_params = dict(tuple(require_captcha.call_args_list[0])[1])
            keys = ('query_params', 'form_text', 'login_form_data',
                    'http_session')
            for k in keys:
                self.assertIn(k, call_params)
            self.assertEqual(call_params['query_params'],
                             {'sid': 'test123', 'test': '1'})

    def test_do_login_require_2fa(self):
        vk_session = VKSession()
        session = self.get_mocked_http_session(name='2fa_session')

        # Mock 'url' property on post to call get_2fa_code
        url = 'http://test/?act=authcheck&test=1'
        login_response = mock.MagicMock(name='login_response')
        form = '<form method="post" action="/login?act=authcheck_code' \
               '&hash=1234567890_ff181e72e9db30cbc3"></form>'
        login_response.configure_mock(url=url, text=form)
        session.post = mock.Mock(return_value=login_response)

        with self.patch_api('get_2fa_code') as get_2fa_code:
            get_2fa_code.return_value = 1234
            vk_session.do_login(http_session=session)
            self.assertTrue(get_2fa_code.called)
            call_2fa = dict(tuple(session.post.call_args_list[-1])[1])

            # Check that 2fa http call was done with correct url and data
            self.assertEqual(call_2fa['url'],
                             'https://m.vk.com/login?act=authcheck_code&'
                             'hash=1234567890_ff181e72e9db30cbc3')
            self.assertEqual(call_2fa['data'],
                             {'_ajax': '1', 'code': 1234, 'remember': '1'})

    def test_do_login_require_phone_number(self):
        vk_session = VKSession()
        session = self.get_mocked_http_session()

        # Mock 'url' property on post to call require_phone_number
        url = 'http://test/?act=security_check&test=1'
        post_response = mock.MagicMock()
        type(post_response).url = mock.PropertyMock(return_value=url)
        session.post = mock.Mock(return_value=post_response)

        with self.patch_api('require_phone_number') as require_pn:
            vk_session.do_login(http_session=session)
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
        vk_session = VKSession(phone_number='+123456789')
        html = get_fixture('require_phone_num_resp.html')
        session_mock = mock.Mock()
        vk_session.require_phone_number(html=html, session=session_mock)
        self.assertEqual(session_mock.post.call_count, 1)
        call = tuple(session_mock.post.call_args_list[0])[1]
        self.assertEqual(call['data']['act'], 'security_check')
        self.assertEqual(call['data']['code'], '567')

    def test_require_phone_number_with_auto_resolving_warn(self):
        """Test require_phone_number with auto resolving security check when vk
        returns warning message like:
        'Incorrect numbers. You can repeat the attempt in 3 hours.'

        """
        vk_session = VKSession(phone_number='+123456789')
        html = get_fixture('require_phone_num_warn_resp.html')
        session_mock = mock.Mock()
        with self.assertRaises(VkPageWarningsError) as err:
            vk_session.require_phone_number(html=html, session=session_mock)
            self.assertIn(
                'Incorrect numbers. You can repeat the attempt in 3 hours',
                str(err))

    def test_do_login_no_action_url(self):
        vk_session = VKSession()
        session = self.get_mocked_http_session(action='')

        with self.assertRaises(VkParseError) as err:
            vk_session.do_login(http_session=session)
            self.assertIn("Can't parse form action url", str(err))
