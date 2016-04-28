# coding=utf8
import unittest
import os.path as op
from vk_requests.exceptions import VkPageWarningsError
import vk_requests.utils as utils


FIXTURES_PATH = '/'.join([op.abspath(op.dirname(__file__)), 'fixtures'])


def get_fixture(filename):
    file_path = '/'.join([FIXTURES_PATH, filename])
    with open(file_path) as fd:
        return fd.read()


class UtilsTestCase(unittest.TestCase):
    def test_stringify(self):
        self.assertEqual(
            {1: 'str,str2'}, utils.stringify_values({1: ['str', 'str2']}))

    def test_stringify_2(self):
        self.assertEqual({1: u'str,стр2'},
                         utils.stringify_values({1: ['str', u'стр2']}))

    def test_stringify_3(self):
        self.assertEqual({1: u'стр,стр2'},
                         utils.stringify_values({1: [u'стр', u'стр2']}))

    def test_stringify_int_values(self):
        values = {'user_ids': [1, 2, 3]}
        self.assertEqual(utils.stringify_values(values),
                         {'user_ids': u'1,2,3'})

    def test_stringify_string_values(self):
        # Expect the string will be set as is
        data = {'fields': 'owner'}
        self.assertEqual(utils.stringify_values(data), {'fields': 'owner'})

        data_2 = {'fields': ['owner']}
        self.assertEqual(utils.stringify_values(data_2), {'fields': 'owner'})

    def test_stringify_wrong_input(self):
        with self.assertRaises(ValueError) as err:
            values = utils.stringify_values('wrong input')
            self.assertIsNone(values)
            self.assertIn('Data must be dict', str(err))

    def test_parse_url_query_params(self):
        resp_url = 'https://m.vk.com/login.php?act=security_check&to=&al_page='
        params = utils.parse_url_query_params(resp_url, fragment=False)
        self.assertEqual(params['act'], 'security_check')

        resp_url = '/login.php?act=security_check&to=&hash=4b07a4650e9f22038b'
        params = utils.parse_url_query_params(resp_url, fragment=False)
        self.assertEqual(params['act'], 'security_check')
        self.assertEqual(params['hash'], '4b07a4650e9f22038b')

    def test_parse_url_fragments_params(self):
        url = 'https://oauth.vk.com/blank.html#access_token=337d6dc7cd73ff0040' \
              '&expires_in=0&user_id=12345'
        params = utils.parse_url_query_params(url)
        self.assertEqual(params['access_token'], '337d6dc7cd73ff0040')
        self.assertEqual(params['expires_in'], '0')
        self.assertEqual(params['user_id'], '12345')

    def test_parse_form_action(self):
        html = get_fixture('require_phone_num_resp.html')
        action_url = utils.parse_form_action_url(html)
        self.assertEqual(
            action_url,
            '/login.php?act=security_check&to=&hash=4b07a4650e9f22038b')

    def test_parse_masked_phone_number(self):
        html = get_fixture('require_phone_num_resp.html')
        fields = utils.parse_masked_phone_number(html)
        self.assertEqual(fields, ('+1234', '89'))

    def test_check_html_warnings(self):
        html = get_fixture('require_phone_num_resp.html')
        html_with_warn = get_fixture('require_phone_num_warn_resp.html')

        # No warnings - expect True
        self.assertTrue(utils.check_html_warnings(html))
        with self.assertRaises(VkPageWarningsError) as err:
            result = utils.check_html_warnings(html_with_warn)
            self.assertIsNone(result)
            self.assertIn('Incorrect numbers.', str(err))
