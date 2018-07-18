# -*- coding: utf-8 -*-
from vk_requests import utils
from vk_requests.tests.test_base import get_fixture


def test_parse_captcha_html():
    html = get_fixture('captcha_resp.html')
    captcha_sid, captcha_url = utils.parse_captcha_html(
        html=html, response_url='http://test'
    )
    assert captcha_sid == '600885884'
    assert captcha_url == 'http://test/captcha.php?s=0&sid=600885885'
