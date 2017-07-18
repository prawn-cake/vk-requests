# -*- coding: utf-8 -*-
import logging
from collections import Iterable

import bs4
import requests
import six

from vk_requests.exceptions import VkParseError, VkPageWarningsError

logger = logging.getLogger('vk-requests')

try:
    # Python 2
    from urllib import urlencode
    from urlparse import urlparse, parse_qsl
except ImportError:
    # Python 3
    from urllib.parse import urlparse, parse_qsl, urlencode


def stringify_values(data):
    """Coerce iterable values to 'val1,val2,valN'

    Example:
        fields=['nickname', 'city', 'can_see_all_posts']
        --> fields='nickname,city,can_see_all_posts'

    :param data: dict
    :return: converted values dict
    """
    if not isinstance(data, dict):
        raise ValueError('Data must be dict. %r is passed' % data)

    values_dict = {}
    for key, value in data.items():
        items = []
        if isinstance(value, six.string_types):
            items.append(value)
        elif isinstance(value, Iterable):
            for v in value:
                # Convert to str int values
                if isinstance(v, int):
                    v = str(v)
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

    :param fragment: bool: flag is used for parsing oauth url
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


def parse_form_action_url(html, parser=None):
    """Parse <form action="(.+)"> url

    :param html: str: raw html text
    :param parser: bs4.BeautifulSoup: html parser
    :return: url str: for example: /login.php?act=security_check&to=&hash=12346
    """
    if parser is None:
        parser = bs4.BeautifulSoup(html, 'html.parser')

    forms = parser.find_all('form')
    if not forms:
        raise VkParseError('No one form is found in \n%s' % html)
    if len(forms) > 1:
        raise VkParseError('Find more than 1 forms to handle:\n%s', forms)
    form = forms[0]
    return form.get('action')


def parse_masked_phone_number(html, parser=None):
    """Get masked phone number from security check html

    :param html: str: raw html text
    :param parser: bs4.BeautifulSoup: html parser
    :return: tuple of phone prefix and suffix, for example: ('+1234', '89')
    :rtype : tuple
    """
    if parser is None:
        parser = bs4.BeautifulSoup(html, 'html.parser')

    fields = parser.find_all('span', {'class': 'field_prefix'})
    if not fields:
        raise VkParseError(
            'No <span class="field_prefix">...</span> in the \n%s' % html)

    result = []
    for f in fields:
        value = f.get_text().replace(six.u('\xa0'), '')
        result.append(value)
    return tuple(result)


def check_html_warnings(html, parser=None):
    """Check html warnings

    :param html: str: raw html text
    :param parser: bs4.BeautifulSoup: html parser
    :raise VkPageWarningsError: in case of found warnings
    """
    if parser is None:
        parser = bs4.BeautifulSoup(html, 'html.parser')

    # Check warnings
    warnings = parser.find_all('div', {'class': 'service_msg_warning'})
    if warnings:
        raise VkPageWarningsError('; '.join([w.get_text() for w in warnings]))
    return True


class VerboseHTTPSession(requests.Session):
    """HTTP session based on requests.Session with some extra logging
    """
    def __init__(self):
        super(VerboseHTTPSession, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

    def request(self, method, url, **kwargs):
        self.logger.debug(
            'Request: %s %s, params=%r, data=%r',
            method, url, kwargs.get('params'), kwargs.get('data'))
        response = super(VerboseHTTPSession, self).request(
            method, url, **kwargs)
        self.logger.debug(
            'Response: %s %s', response.status_code, response.url)
        return response
