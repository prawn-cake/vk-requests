# -*- coding: utf-8 -*-
import unittest

import six

from vk_requests import settings
from vk_requests.auth import AuthAPI, VKSession


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
        self.assertTrue(session.auth_api.is_token_required)

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