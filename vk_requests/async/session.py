import aiohttp
import copy
from vk_requests import VKSession
from vk_requests.utils import stringify_values


class AsyncVKSession(VKSession):
    """Aiohttp powered VKSession"""

    @property
    def http_session(self):
        """Async HTTP Session getter

        :return: aiohttp.ClientSession instance
        """
        if self._http_session is None:
            session = aiohttp.ClientSession(headers=copy.deepcopy(self.DEFAULT_HTTP_HEADERS))
            self._http_session = session
        return self._http_session

    async def send_api_request(self, request_obj, captcha_response=None):
        """Prepare and send async HTTP API request

        :param request_obj: vk_requests.api.Request instance
        :param captcha_response: None or dict
        :return: HTTP response
        """
        url = self.API_URL + request_obj.method_name

        # Prepare request arguments
        method_kwargs = {'v': self.api_version}

        for values in (request_obj.method_args, ):
            method_kwargs.update(stringify_values(values))

        if self.is_token_required() or self._service_token:
            # Auth api call if access_token hadn't been gotten earlier
            method_kwargs['access_token'] = self.access_token

        if captcha_response:
            method_kwargs['captcha_sid'] = captcha_response['sid']
            method_kwargs['captcha_key'] = captcha_response['key']

        http_params = dict(url=url, data=method_kwargs, **request_obj.http_params)
        async with self.http_session.post(**http_params) as response:
            return await response.json()
