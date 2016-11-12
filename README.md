![VKRequestsIcon](https://www.dropbox.com/s/dv9oy3i8nlmdo50/vk_icon.png?dl=1) requests for humans
========================================================================================================
[![Build Status](https://travis-ci.org/prawn-cake/vk-requests.svg?branch=master)](https://travis-ci.org/prawn-cake/vk-requests)
[![Coverage Status](https://coveralls.io/repos/prawn-cake/vk-requests/badge.svg?branch=master&service=github)](https://coveralls.io/github/prawn-cake/vk-requests?branch=master)
![PythonVersions](https://www.dropbox.com/s/ck0nc28ttga2pw9/python-2.7_3.4-blue.svg?dl=1)

[vk.com](https://vk.com) is the largest social network in Russia.
This library is significantly improved fork of [vk](https://github.com/dimka665/vk)

## Install

    pip install vk-requests
    
## Usage
    import vk_requests
    
    
    api = vk_requests.create_api(app_id=123, login='User', password='Password')
    api.users.get(user_ids=1)
    [{'first_name': 'Pavel', 'last_name': 'Durov', 'id': 1}]
    
### Custom scope or api version requests

Just pass `scope` and/or `api_version` parameters like

    api = vk_requests.create_api(..., scope=['offline', 'status'], api_version='5.00')
    api.status.set(text='Hello world!')
    
### Enable debug logger
From your code:
    
    import logging
    
    logging.getLogger('vk-requests').setLevel(logging.DEBUG)


## Features
### Straightforward queries
    
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


## API docs
https://vk.com/dev/methods


## Tests

Tests are mostly checking integration part, so it requires some vk authentication data.

Before running tests locally define environment variables: 
    
    export VK_USER_LOGIN=<login> VK_USER_PASSWORD=<password> VK_APP_ID=<app_id> VK_PHONE_NUMBER=<phone_number>

To run tests:

    tox


## Bug tracker

Warm welcome for suggestions and concerns

https://github.com/prawn-cake/vk-requests/issues


## License

MIT - http://opensource.org/licenses/MIT
