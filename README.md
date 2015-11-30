# VK Requests for humans

[vk.com](https://vk.com) is the largest social network in Russia.
This library is significantly improved fork of [vk](https://github.com/dimka665/vk)


## Usage
    from vk_requests import API
    
    
    api = API.create_api(app_id=1234, login='myUser', password='myPassword')
    api.users.get(user_ids=1)
    [{'first_name': 'Pavel', 'last_name': 'Durov', 'id': 1}]


## Features
* Interactive session
* Auto security-check passing with phone number