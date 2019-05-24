import requests


class NetworkAPI(object):
    def __init__(self, token, api_url, provider, api_version=None):
        '''[summary]

        Arguments:
            token {str} -- Access token.
            api_version {str} -- The version of the API.
        '''

        self.api_url = api_url
        self.token = token
        self.api_version = api_version
        self.provider = provider.lower()
        self.name = ''

        pass

    def __getattr__(self, name):
        if self.name == '':
            self.name = name
        else:
            self.name = self.name + '.' + name
        return self

    def method_request(self, method, params):
        '''[summary]
        Arguments:
            method {str} -- The name of the API method you want to access.
            kwargs {dict} -- Input parameters of the corresponding API method.
        Returns:
            r -- Response to a request
        '''
        headers = None
        if self.provider == 'vk':
            params['access_token'] = self.token
            params['v'] = self.api_version

        if self.provider == 'viber':
            headers['X-Viber-Auth-Token'] = self.token

        r = requests.post(self.api_url + method,
                          params=params,
                          headers=headers)
        print(r.json())
        return r.json()['response']

    def __call__(self, *args, **kwargs):
        name = self.name
        self.name = ''
        return self.method_request(method=name, params=kwargs)
