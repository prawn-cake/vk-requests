VK requests for humans™
========================================================================================================
[![Build Status](https://travis-ci.org/prawn-cake/vk-requests.svg?branch=master)](https://travis-ci.org/prawn-cake/vk-requests)
[![Coverage Status](https://coveralls.io/repos/prawn-cake/vk-requests/badge.svg?branch=master&service=github)](https://coveralls.io/github/prawn-cake/vk-requests?branch=master)
[![GitHub issues](https://img.shields.io/github/issues/prawn-cake/vk-requests.svg)](https://github.com/prawn-cake/vk-requests/issues)

[vk.com](https://vk.com) is the largest social network in Russia.

## Requirements

* python (2.7, 3.4, 3.5, 3.6)

**NOTE:** Python 2.7 will be no longer supported starting from the version 2.0.0

## Install

    pip install vk-requests
    

### Example

    import vk_requests
    
    
    api = vk_requests.create_api(app_id=123, login='User', password='Password')
    api.users.get(user_ids=1)
    [{'first_name': 'Pavel', 'last_name': 'Durov', 'id': 1}]
    
### Documentation

Check [full documentation](https://prawn-cake.github.io/vk-requests/)

Also check the [official VK api methods docs](https://vk.com/dev/methods)
    
