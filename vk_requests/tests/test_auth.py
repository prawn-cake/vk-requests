# -*- coding: utf-8 -*-
import unittest
import mock
from vk_requests import API
from vk_requests.auth import AuthAPI, InteractiveVKSession
from vk_requests.tests.test_base import get_fixture


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

    @unittest.skip('Require console input')
    def test_interactive_session_init(self):
        session = InteractiveVKSession()
        api = API(session=session, timeout=10)
        self.assertIsInstance(api, API)
