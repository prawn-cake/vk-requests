# VK requests for humans™

[vk.com](https://vk.com) is the largest social network in Russia.


## Requirements

* python (2.7, 3.4, 3.5, 3.6)


## Install

    pip install vk-requests
    
## Usage and features

### Simple queries
    
    # Returns list of users
    api.users.get(users_ids=1)
    
    # Returns list of user's friends with extra fields 
    api.friends.get(user_id=1, fields=['nickname', 'city'])
    
    # Returns result list from your custom api method
    api.execute.YourMethod(**method_params)


### User token with login and password

Fits the usecase when you run queries from one on the backend from one of your accounts

    import vk_requests
    
    
    api = vk_requests.create_api(app_id=123, login='User', password='Password')
    api.users.get(user_ids=1)
    [{'first_name': 'Pavel', 'last_name': 'Durov', 'id': 1}]
    
### Using service token

Service token is preferable way, because it does not require user 
credentials and oauth requests, but **not all the methods can be called with service token** (e.g *execute* can't be)


    api = vk_requests.create_api(service_token="{YOUR_APP_SERVICE_TOKEN}")
    ...
    

[More info](https://vk.com/dev/service_token) about service token.


### Using client access token

For example when you got a token on the client side ([implicit flow](https://vk.com/dev/implicit_flow_user)) and want to query API on the backend.

Use `service_token` parameter as in the example above. 

   
### Using custom parameters

#### Scope or api version

Just pass `scope` and/or `api_version` parameters like

    api = vk_requests.create_api(..., scope=['offline', 'status'], api_version='5.00')
    api.status.set(text='Hello world!')

#### HTTP parameters

To override [requests http parameters (e.g ssl options)](http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification), 
just use `http_params` as follows:

    api = vk_requests.create_api(http_params={'timeout': 15, 'verify': False})


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


### Auto-resolving conflicts when you're getting access from unusual place

Just pass your phone number during API initialization. In case of security check 
it will be handled automatically, otherwise console input will be asked

    api = vk_requests.create_api(
        app_id=123, login='User', password='Password', phone_number='+79111234567')


## Interactive session

Interactive session gives you control over login parameters during the runtime. 

**Useful if**

* 2FA authentication required
* CAPTCHA required
* For testing purposes


### Usage

    api = vk_requests.create_api(..., interactive=True)

If you don't pass login, password and app_id you will be asked to prompt it, i.e having this

    api = vk_requests.create_api(app_id=XXX, login='***', password='***', interactive=True)

You will be asked only for *2FA authentication* or *captcha* code if required 


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


## Official API docs

* [https://vk.com/dev/methods](https://vk.com/dev/methods)
* [https://vk.com/dev/streaming_api_docs](https://vk.com/dev/streaming_api_docs)


## Tests

Tests are mostly checking integration part, so it requires some vk authentication data.

Before running tests locally define environment variables: 
    
    export VK_USER_LOGIN=<login> VK_USER_PASSWORD=<password> VK_APP_ID=<app_id> VK_PHONE_NUMBER=<phone_number> VK_SERVICE_TOKEN=<service_token>

To run tests:

    tox


## Bug tracker

Warm welcome for suggestions and concerns. Feel free to submit it to the [Issues section](https://github.com/prawn-cake/vk-requests/issues)


## License

MIT - [http://opensource.org/licenses/MIT](http://opensource.org/licenses/MIT)
