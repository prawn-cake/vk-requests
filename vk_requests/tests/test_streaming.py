# -*- coding: utf-8 -*-
from vk_requests.streaming import Streaming


def test_one():
    """API sketch

    """
    streaming_api = Streaming(service_token='blablabla')
    streaming_api.add_rule(value='value', tag='x')
    rules = streaming_api.get_rules()
    streaming_api.remove_rule(tag='x')

    stream = streaming_api.get_stream()

    @stream.handler
    def handle_event(event):
        print(event)

    stream.add_handler(lambda event: print(event))
    stream.run()
