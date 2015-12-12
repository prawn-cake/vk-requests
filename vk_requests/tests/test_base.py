# coding=utf8
import unittest
import os.path as op
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
        self.assertEqual(
            {1: u'str,стр2'}, utils.stringify_values({1: ['str', u'стр2']}))

    def test_stringify_3(self):
        self.assertEqual({1: u'стр,стр2'}, utils.stringify_values(
            {1: [u'стр', u'стр2']}))

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

    def test_get_form_action(self):
        html = get_fixture('require_phone_num_resp.html')
        form = utils.get_form_action(html)
        self.assertEqual(
            form, '/login.php?act=security_check&to=&hash=4b07a4650e9f22038b')

    def test_get_masked_phone_number(self):
        html = get_fixture('require_phone_num_resp.html')
        fields = utils.get_masked_phone_number(html)
        self.assertEqual(fields, ('+1234', '89'))
