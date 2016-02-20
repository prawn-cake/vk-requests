# -*- coding: utf-8 -*-
import unittest

import mock
import six

from vk_requests import API
from vk_requests.auth import AuthAPI, InteractiveVKSession, VKSession
from vk_requests.exceptions import VkPageWarningsError
from vk_requests.tests.test_base import get_fixture
from vk_requests import settings


class AuthAPITest(unittest.TestCase):
    def test_require_phone_number(self):
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

    def test_require_phone_number_warn(self):
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


class VKSessionTest(unittest.TestCase):
    @staticmethod
    def get_default_vk_session(**kwargs):
        return VKSession(app_id=settings.APP_ID,
                         user_login=settings.USER_LOGIN,
                         user_password=settings.USER_PASSWORD,
                         phone_number=settings.PHONE_NUMBER, **kwargs)

    def test_session_init(self):
        session = self.get_default_vk_session()
        # Expect no errors
        self.assertIsInstance(session, VKSession)

        # Token is required, cuz auth params are being passed
        self.assertTrue(session.is_token_required)

    def test_custom_auth_api_cls(self):
        class MyAuthAPI(AuthAPI):
            @staticmethod
            def get_captcha_key(captcha_image_url):
                return 1

        # Create session with custom AuthAPI implementation
        session = self.get_default_vk_session(auth_api_cls=MyAuthAPI)
        self.assertIsInstance(session.auth_api, MyAuthAPI)

    def test_access_token_property(self):
        # Check token getter
        session = self.get_default_vk_session()
        self.assertTrue(session.access_token)
        self.assertIsInstance(session.access_token, six.string_types)

        # Check token setter
        new_token_value = 'my_fake_access_token'
        session.access_token = new_token_value
        self.assertEqual(session.access_token, new_token_value)
        self.assertEqual(session.censored_access_token, 'my_f***oken')