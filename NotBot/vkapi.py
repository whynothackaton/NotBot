import requests


class VK(object):

    def __init__(self, token, api_version):
        '''[summary]
        
        Arguments:
            token {str} -- Access token.
            api_version {str} -- The version of the API.
        '''

        self.api_url = 'https://api.vk.com/method/'
        self.token = token
        self.api_version = api_version
        self.name = ''
        pass

    def __getattr__(self, name):
        if self.name == '':
            self.name = name
        else:
            self.name = self.name+'.'+name
        return self

    def method_request(self, method, params):
        '''[summary]
        Arguments:
            method {str} -- The name of the API method you want to access.
            kwargs {dict} -- Input parameters of the corresponding API method.
        Returns:
            r -- Response to a request
        '''
        params['access_token'] = self.token
        params['v'] = self.api_version
        r = requests.post(self.api_url + method, params=params)
        return r.json()['response']

    def __call__(self, *args, **kwargs):
        name = self.name
        self.name = ''
        return self.method_request(method=name, params=kwargs)