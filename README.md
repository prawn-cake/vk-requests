VK requests for humans™
========================================================================================================
[![Build Status](https://travis-ci.org/prawn-cake/vk-requests.svg?branch=master)](https://travis-ci.org/prawn-cake/vk-requests)
[![Coverage Status](https://coveralls.io/repos/prawn-cake/vk-requests/badge.svg?branch=master&service=github)](https://coveralls.io/github/prawn-cake/vk-requests?branch=master)
[![GitHub issues](https://img.shields.io/github/issues/prawn-cake/vk-requests.svg)](https://github.com/prawn-cake/vk-requests/issues)

[vk.com](https://vk.com) is the largest social network in Russia.
This library is significantly improved fork of [vk](https://github.com/dimka665/vk)

## Requirements

* python (2.7, 3.4, 3.5, 3.6)


## Install

    pip install vk-requests
    
## Usage

#### Using user token

    import vk_requests
    
    
    api = vk_requests.create_api(app_id=123, login='User', password='Password')
    api.users.get(user_ids=1)
    [{'first_name': 'Pavel', 'last_name': 'Durov', 'id': 1}]
    
#### Using service token

    api = vk_requests.create_api(service_token="{YOUR_APP_SERVICE_TOKEN}")
    ...
    
**NOTE:** service token is preferable way, because it does not require user 
credentials and oauth requests, but **not all the methods can be called with service token** (e.g *execute* can't be)

More info about service token: [Link](https://vk.com/dev/service_token) 
   
### Custom scope or api version requests

Just pass `scope` and/or `api_version` parameters like

    api = vk_requests.create_api(..., scope=['offline', 'status'], api_version='5.00')
    api.status.set(text='Hello world!')
    
### Enable logging

To enable library logging in your project you should do as follows:
    
    import logging
    
    # Setup basic config
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
    )
    
    # To change log level for the library logger
    logging.getLogger('vk-requests').setLevel(logging.DEBUG)


## Features

### Simple queries
    
    # Returns list of users
    api.users.get(users_ids=1)
    
    # Returns list of user's friends with extra fields 
    api.friends.get(user_id=1, fields=['nickname', 'city'])
    
    # Returns result list from your custom api method
    api.execute.YourMethod(**method_params)
 
 
### Interactive session

Interactive session gives you control over login parameters during the runtime. 

**Useful if**

* 2FA authentication required
* CAPTCHA required
* For testing purposes

#### Usage

    api = vk_requests.create_api(..., interactive=True)

If you don't pass login, password and app_id you will be asked to prompt it, i.e having this

    api = vk_requests.create_api(app_id=XXX, login='***', password='***', interactive=True)

You will be asked only for *2FA authentication* or *captcha* code if required 


### Auto-resolving conflicts when you're getting access from unusual place

Just pass your phone number during API initialization. In case of security check 
it will be handled automatically, otherwise console input will be asked

    api = vk_requests.create_api(
        app_id=123, login='User', password='Password', phone_number='+79111234567')

## Streaming API

[Streaming API](https://vk.com/dev/streaming_api_docs) allows to subscribe on the events from vk.

**NOTE:** Only for *python 3.4* and later

### Install 
    
    pip install vk-requests[streaming]
    

### Stream rules

    from vk_requests.streaming import StreamingAPI
    
    streaming_api = StreamingAPI(service_token="{YOUR_SERVICE_TOKEN}")
    
    # Add new rule
    streaming_api.add_rule(value='my_keyword', tag='tag1')
    
    # Get all rules
    rules = streaming_api.get_rules()
    
    # Remove the rule by tag
    streaming_api.remove_rule(tag='tag1')
    
    

### Consumer

Streaming API provides convenient coroutine-based handler interface (callback)

    import asyncio
    from vk_requests import StreamingAPI
    
    api = StreamingAPI(service_token="{YOUR_SERVICE_TOKEN}")
    stream = api.get_stream()
    
    @stream.consumer
    @asyncio.coroutine
    def handle_event(payload):
        print(payload)


    if __name__ == '__main__':
        stream.consume()


## API docs

* https://vk.com/dev/methods
* https://vk.com/dev/streaming_api_docs


## Tests

Tests are mostly checking integration part, so it requires some vk authentication data.

Before running tests locally define environment variables: 
    
    export VK_USER_LOGIN=<login> VK_USER_PASSWORD=<password> VK_APP_ID=<app_id> VK_PHONE_NUMBER=<phone_number> VK_SERVICE_TOKEN=<service_token>

To run tests:

    tox


## Bug tracker

Warm welcome for suggestions and concerns

https://github.com/prawn-cake/vk-requests/issues


## License

MIT - http://opensource.org/licenses/MIT
