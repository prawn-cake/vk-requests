# -*- coding: utf-8 -*-
import unittest

import six

import vk_requests
from vk_requests.api import API
from vk_requests.exceptions import VkAPIError
from vk_requests import VKSession
from vk_requests.settings import APP_ID, USER_LOGIN, USER_PASSWORD, \
    PHONE_NUMBER, SERVICE_TOKEN

try:
    from unittest import mock
except ImportError:
    import mock


def fake_request(return_text_value='{}'):
    http_resp_mock = mock.Mock()
    http_resp_mock.configure_mock(text=return_text_value)
    return mock.patch('vk_requests.utils.VerboseHTTPSession.request',
                      return_value=http_resp_mock)


class VkApiTest(unittest.TestCase):
    def test_create_api_without_any_token(self):
        api = vk_requests.create_api()
        self.assertIsInstance(api, API)
        self.assertIsNone(api._session._access_token)

    def test_create_api_with_user_token(self):
        api = vk_requests.create_api(
            app_id=APP_ID, login=USER_LOGIN, password=USER_PASSWORD,
            phone_number=PHONE_NUMBER)
        self.assertIsInstance(api, API)

        # Check that we have got access token on init
        self.assertIsInstance(
            api._session._access_token, six.string_types)

    def test_create_api_with_custom_api_version(self):
        api = vk_requests.create_api(api_version='5.00')
        self.assertEqual(api._session.api_version, '5.00')

    @mock.patch('vk_requests.utils.VerboseHTTPSession.request')
    def test_send_request_with_custom_api_version(self, mock_request):
        """Steps:
            * Check default api version value per api request
            * Check custom default api version per api request
            * Check overridden api version within request

        """
        http_resp_mock = mock.Mock()
        http_resp_mock.configure_mock(text='{}')
        mock_request.return_value = http_resp_mock

        # Expect default version to being passed
        api = vk_requests.create_api()
        api.users.get(user_id=1)
        url_data, params = tuple(mock_request.call_args_list[0])
        self.assertEqual(params['data']['v'], VKSession.DEFAULT_API_VERSION)
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


class VkApiMethodsLiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vk_api = vk_requests.create_api()
        cls.api_st = vk_requests.create_api(service_token=SERVICE_TOKEN)
        cls.api_ut = cls._create_api()  # user-token api

    @staticmethod
    def _create_api(**kwargs):
        return vk_requests.create_api(
            app_id=APP_ID,
            login=USER_LOGIN,
            password=USER_PASSWORD,
            **kwargs
        )

    def test_get_server_time(self):
        server_time = self.api_st.getServerTime()
        self.assertTrue(int(server_time))

    def test_get_profiles_via_token(self):
        profiles = self.api_st.users.get(user_id=1)
        self.assertIn(profiles[0]['last_name'], ('Durov', 'Дуров'))

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

        resp = self.api_ut.users.search(**request_opts)
        self.assertIsInstance(resp, dict)
        total_num, items = resp['count'], resp['items']
        self.assertIsInstance(total_num, int)
        for item in items:
            self.assertIsInstance(item, dict)
            self.assertIn('screen_name', item)

    def test_get_friends(self):
        items = self.api_st.friends.get(
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
        posts = resp[0]
        for item in posts:
            self.assertIsInstance(item, dict)
            print(item)

    def test_set_status(self):
        """Test requires scope='status' vk permissions
        """
        status_text = 'Welcome to noagent.estate'
        api = self._create_api(scope=['offline', 'status'])
        self.assertEqual(api._session.scope, ['offline', 'status'])

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
        resp = self.api_st.likes.getList(
            type='post', owner_id=1, item_id=815649)
        self.assertIn('count', resp)
        self.assertIn('items', resp)
        for user_id in resp['items']:
            self.assertIsInstance(user_id, int)

    def test_wall_get(self):
        resp = self.api_st.wall.get(owner_id=1)
        self.assertIn('items', resp)
        self.assertIn('count', resp)


def test_customize_http_params():
    http_resp_mock = mock.Mock()
    http_resp_mock.configure_mock(text='{}')
    with fake_request() as req:
        api = vk_requests.create_api(
            http_params={'timeout': 15, 'verify': False})
        api.users.get(user_id=1)
        url_data, params = tuple(req.call_args_list[0])

        assert params['verify'] is False
        assert params['timeout'] == 15
