![VKRequestsIcon](https://www.dropbox.com/s/dv9oy3i8nlmdo50/vk_icon.png?dl=1) requests for humans
========================================================================================================
[![Build Status](https://travis-ci.org/prawn-cake/vk-requests.svg?branch=master)](https://travis-ci.org/prawn-cake/vk-requests)
[![Coverage Status](https://coveralls.io/repos/prawn-cake/vk-requests/badge.svg?branch=master&service=github)](https://coveralls.io/github/prawn-cake/vk-requests?branch=master)
![PythonVersions](https://www.dropbox.com/s/ck0nc28ttga2pw9/python-2.7_3.4-blue.svg?dl=1)

[vk.com](https://vk.com) is the largest social network in Russia.
This library is significantly improved fork of [vk](https://github.com/dimka665/vk)


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
### "Queryset-like" requests
    
    # Returns list of users
    api.users.get(users_ids=1)
    
    # Returns list of user's friends with extra fields 
    api.friends.get(user_id=1, fields=['nickname', 'city'])
    
    # Returns result list from your custom api method
    api.execute.YourMethod(**method_params)
 
 
### Interactive session. 

Useful for dev purposes. You will be asked about login, password and app_id 
interactively in console. Useful if capture required.
        
        from vk_requests.api import API
        from vk_requests.auth import InteractiveVKSession
        
        
        api = vk_requests.create_api(..., session_cls=InteractiveVKSession)


### Auto-resolving conflicts when you getting access from unusual place

Just pass your phone number during API initialization. In case of security check 
it will be handled automatically, otherwise console input will be asked

    api = vk_requests.create_api(
        app_id=123, login='User', password='Password', phone_number='+79111234567')


## API docs
https://vk.com/dev/methods


## Tests
    
    tox


## Bug tracker

Warm welcome for suggestions and concerns

https://github.com/prawn-cake/vk-requests/issues


## License

MIT - http://opensource.org/licenses/MIT
