# -*- coding: utf-8 -*-
import sys

if sys.version_info <= (3, 4):
    raise RuntimeError('Streaming API requires python version >= 3.4')

import requests
import websockets
import asyncio
import logging


logger = logging.getLogger(__name__)


class Stream(object):
    """Stream representation"""

    def __init__(self, conn_url):
        self._conn_url = conn_url
        self._consumer_fn = None

    def __repr__(self):
        return '%s(conn_url=%s)' % (self.__class__.__name__, self._conn_url)

    def consumer(self, fn):
        """Consumer decorator

        :param fn: coroutine consumer function

        Example:

        >>> api = StreamingAPI('my_service_key')
        >>> stream = api.get_stream()

        >>> @stream.consumer
        >>> @asyncio.coroutine
        >>> def handle_event(payload):
        >>>     print(payload)

        """
        if self._consumer_fn is not None:
            raise ValueError('Consumer function is already defined for this '
                             'Stream instance')
        if not any([asyncio.iscoroutine(fn), asyncio.iscoroutinefunction(fn)]):
            raise ValueError('Consumer function must be a coroutine')
        self._consumer_fn = fn

    def consume(self, timeout=None, loop=None):
        """Start consuming the stream

        :param timeout: int: if it's given then it stops consumer after given
        number of seconds
        """
        if self._consumer_fn is None:
            raise ValueError('Consumer function is not defined yet')

        logger.info('Start consuming the stream')

        @asyncio.coroutine
        def worker(conn_url):
            extra_headers = {
                'Connection': 'upgrade',
                'Upgrade': 'websocket',
                'Sec-Websocket-Version': 13,
            }

            ws = yield from websockets.connect(
                conn_url, extra_headers=extra_headers)

            if ws is None:
                raise RuntimeError("Couldn't connect to the '%s'" % conn_url)

            try:
                while True:
                    message = yield from ws.recv()
                    yield from self._consumer_fn(message)
            finally:
                yield from ws.close()

        if loop is None:
            loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)
        try:
            task = worker(conn_url=self._conn_url)
            if timeout:
                logger.info('Running task with timeout %s sec', timeout)
                loop.run_until_complete(
                    asyncio.wait_for(task, timeout=timeout))
            else:
                loop.run_until_complete(task)
        except asyncio.TimeoutError:
            logger.info('Timeout is reached. Closing the loop')
            loop.close()
        except KeyboardInterrupt:
            logger.info('Closing the loop')
            loop.close()


class StreamingAPI(object):
    """VK Streaming API implementation
    Docs: https://vk.com/dev/streaming_api_docs
    """

    REQUEST_URL = 'https://{endpoint}/rules?key={key}'
    STREAM_URL = 'wss://{endpoint}/stream?key={key}'

    def __init__(self, service_token):
        if not service_token:
            raise ValueError('service_token is required')
        import vk_requests

        self.api = vk_requests.create_api(service_token=service_token)
        self._params = self.api.streaming.getServerUrl()

    def add_rule(self, value, tag):
        """Add a new rule

        :param value: str
        :param tag: str
        :return: dict of a json response
        """
        resp = requests.post(url=self.REQUEST_URL.format(**self._params),
                             json={'rule': {'value': value, 'tag': tag}})
        return resp.json()

    def get_rules(self):
        resp = requests.get(url=self.REQUEST_URL.format(**self._params))
        return resp.json()

    def remove_rule(self, tag):
        """Remove a rule by tag

        """
        resp = requests.delete(url=self.REQUEST_URL.format(**self._params),
                               json={'tag': tag})
        return resp.json()

    def get_stream(self):
        """Factory method to get a stream object

        :return Stream instance
        """
        return Stream(conn_url=self.STREAM_URL.format(**self._params))

    def get_settings(self):
        """Get settings object with monthly limit info

        """
        return self.api.streaming.getSettings()

