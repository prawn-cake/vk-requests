# coding=utf8

import six
import re
import json
import requests
import logging
from collections import Iterable


logger = logging.getLogger('vk-requests')

try:
    # Python 2
    from urllib import urlencode
    from urlparse import urlparse, parse_qsl
except ImportError:
    # Python 3
    from urllib.parse import urlparse, parse_qsl, urlencode

try:
    # Python 2
    raw_input = raw_input
except NameError:
    # Python 3
    raw_input = input


def json_iter_parse(response_text):
    decoder = json.JSONDecoder(strict=False)
    idx = 0
    while idx < len(response_text):
        obj, idx = decoder.raw_decode(response_text, idx)
        yield obj


def stringify_values(dictionary):
    """Coerce iterable values to 'val1,val2,valN'

    Example:
        fields=['nickname', 'city', 'can_see_all_posts']
        --> fields='nickname,city,can_see_all_posts'

    :param dictionary:
    :return: converted values dict
    """
    values_dict = {}
    for key, value in dictionary.items():
        if isinstance(value, Iterable):
            items = []
            for v in value:
                try:
                    item = six.u(v)
                except TypeError:
                    item = v
                items.append(item)
            value = ','.join(items)
        values_dict[key] = value
    return values_dict


def parse_url_query_params(url, fragment=True):
    """Parse url query params

    :param fragment: bool: flag which is used for parsing oauth url
    :param url: str: url string
    :return: dict
    """
    parsed_url = urlparse(url)
    if fragment:
        url_query = parse_qsl(parsed_url.fragment)
    else:
        url_query = parse_qsl(parsed_url.query)
    # login_response_url_query can have multiple key
    url_query = dict(url_query)
    return url_query


def get_form_action(html):
    form_action = re.findall(r'<form(?= ).* action="(.+)"', html)
    if form_action:
        return form_action[0]


def get_masked_phone_number(html):
    """Get masked phone number from security check html
    """
    fields = re.findall(r'<span class="field_prefix">(.*)</span>', html)
    result = []
    for field in fields:
        result.append(field.replace('&nbsp;', ''))
    return tuple(result)


class VerboseHTTPSession(requests.Session):
    """HTTP session based on requests.Session with some extra logging
    """

    def request(self, method, url, **kwargs):
        logger.debug('Request: %s %s, params=%r, data=%r',
                     method, url, kwargs.get('params'), kwargs.get('data'))
        response = super(VerboseHTTPSession, self).request(
            method, url, **kwargs)
        logger.debug('Response: %s %s', response.status_code, response.url)
        return response
