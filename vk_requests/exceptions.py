# -*- coding: utf-8 -*-

# API Error Codes
AUTHORIZATION_FAILED = 5        # Invalid access token
PERMISSION_IS_DENIED = 7
CAPTCHA_IS_NEEDED = 14
ACCESS_DENIED = 15              # No access to call this method
USER_IS_DELETED_OR_BANNED = 18  # User deactivated
INVALID_USER_ID = 113


class VkException(Exception):
    pass


class VkAuthError(VkException):
    pass


class VkParseError(VkAuthError):
    """Raised when html has unexpected format"""
    pass


class VkPageWarningsError(VkParseError):
    """Raised when html has some warnings on the page"""
    pass


class VkAPIError(VkException):
    __slots__ = ['error', 'code', 'message', 'request_params', 'redirect_uri']

    def __init__(self, vk_error_data):
        super(VkAPIError, self).__init__()
        self.error_data = vk_error_data
        self.code = vk_error_data.get('error_code')
        self.message = vk_error_data.get('error_msg')
        self.request_params = self.get_pretty_request_params(vk_error_data)
        self.redirect_uri = vk_error_data.get('redirect_uri')

    @staticmethod
    def get_pretty_request_params(error_data):
        request_params = error_data.get('request_params', ())
        request_params = {param['key']: param['value']
                          for param in request_params}
        return request_params

    def is_access_token_incorrect(self):
        return all([self.code == ACCESS_DENIED,
                    'access_token' in self.message])

    def is_captcha_needed(self):
        return self.code == CAPTCHA_IS_NEEDED

    def is_user_deleted_or_banned(self):
        return self.code == USER_IS_DELETED_OR_BANNED

    @property
    def captcha_sid(self):
        return self.error_data.get('captcha_sid')

    @property
    def captcha_img_url(self):
        return self.error_data.get('captcha_img')

    def __str__(self):
        tokens = ['error_code=%s' % self.code,
                  'message=\'%s\'' % self.message,
                  'request_params=%s' % self.request_params]
        if self.redirect_uri:
            tokens.append('redirect_uri=\'%s\'' % self.redirect_uri)
        return ','.join(tokens)
