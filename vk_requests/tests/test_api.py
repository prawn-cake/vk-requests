# -*- coding: utf-8 -*-
import time
import unittest
import six
import vk_requests
from vk_requests.api import API
from vk_requests.exceptions import VkAPIError
from vk_requests.settings import APP_ID, USER_LOGIN, USER_PASSWORD, \
    PHONE_NUMBER


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


class VkTestCase(unittest.TestCase):
    def setUp(self):
        self.vk_api = vk_requests.create_api(lang='ru')

    def test_get_server_time(self):
        time_1 = time.time() - 1
        time_2 = time_1 + 10
        server_time = self.vk_api.getServerTime()
        self.assertTrue(time_1 <= server_time <= time_2)

    def test_get_server_time_via_token_api(self):
        time_1 = time.time() - 1
        time_2 = time_1 + 20
        server_time = self.vk_api.getServerTime()
        self.assertTrue(time_1 <= server_time <= time_2)

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
        api = vk_requests.create_api(
            app_id=APP_ID, login=USER_LOGIN, password=USER_PASSWORD)
        resp = api.users.search(**request_opts)
        total_num, items = resp[0], resp[1:]
        self.assertIsInstance(total_num, int)
        for item in items:
            self.assertIsInstance(item, dict)
            self.assertIn('screen_name', item)

    def test_get_friends(self):
        items = self.vk_api.friends.get(
            fields=['nickname', 'city', 'can_see_all_posts'],
            user_id=1)
        self.assertIsInstance(items, list)
        for item in items:
            if 'deactivated' in item:
                # skip deactivated users, they don't have extra fields
                continue
            self.assertIsInstance(item, dict)
            self.assertIn('city', item)
            self.assertIn('nickname', item)
            self.assertIn('user_id', item)
            self.assertIn('uid', item)
            self.assertIn('can_see_all_posts', item)

    @unittest.skip('Custom test')
    def test_execute(self):
        api = vk_requests.create_api(
            app_id=APP_ID,
            login=USER_LOGIN,
            password=USER_PASSWORD
        )
        resp = api.execute.wallMultiGet(user1=1)
        print(resp)