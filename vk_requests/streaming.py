# -*- coding: utf-8 -*-


class ContentCode:
    EVENT = 100
    SUCCESSFUL_EXECUTION = 200
    SERVICE_MESSAGE = 300
    ERROR = 400


class Streaming(object):
    """VK Streamin API implementation
    Docs: https://vk.com/dev/streaming_api_docs
    """

    REQUEST_URL = 'https://{endpoint}/rules?key={key}'

    def __init__(self, service_token):
        import vk_requests

        self.api = vk_requests.create_api(service_token=service_token)
        self._params = None

    def _connect(self):
        """Get server url endpoint and key

        """
        self._params = self.api.streaming.getServerUrl()

    def __getattr__(self, item):
        if not self._params:
            self._connect()

    def add_rule(self, value, tag):
        pass

    def get_rules(self):
        pass

    def remove_rule(self, tag):
        """Remove rule by tag

        """
        pass

    def get_stream(self):
        # TODO: use https://github.com/aaugustin/websockets
        pass


