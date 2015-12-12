![VKRequestsIcon](https://www.dropbox.com/s/dv9oy3i8nlmdo50/vk_icon.png?dl=1) requests for humans
========================================================================================================

[vk.com](https://vk.com) is the largest social network in Russia.
This library is significantly improved fork of [vk](https://github.com/dimka665/vk)


## Usage
    import vk_requests
    
    
    api = vk_requests.create_api(app_id=123, login='User', password='Password')
    api.users.get(user_ids=1)
    [{'first_name': 'Pavel', 'last_name': 'Durov', 'id': 1}]


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
interactively in console
        
        from vk_requests.api import API
        from vk_requests.auth import InteractiveVKSession
        
        
        session = InteractiveVKSession()
        api = API(session=session, timeout=10)


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
