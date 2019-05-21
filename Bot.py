from vkapi import VK
import requests
import redis
import re
from pai import PaiFlow
import os
import random
from functools import wraps


commands = {}


class Bot():
    def __init__(self, name='bot', group_id='', api_version='', debug=False):
        '''[summary]

        Keyword Arguments:
            name {str} -- Bot name
            group_id {str} -- VK group identifier (default: {''})
            api_version {str} -- Version api VK (default: {''})
        '''
        print("SELF=", self)
        self.group_id = group_id
        self.Name = name
        self.api_version = api_version

        if not debug:
            self.PAI = PaiFlow()
            self.Redis = redis.from_url(os.environ.get('REDIS_URL'), db=0)
            self.token = self.Redis.get('VK_token')
            if self.token != None:
                self.VK = VK(token=self.token.decode(),
                             api_version=self.api_version)

    def __add__(category):
        print("ARGS1=", category)
        def add(command):
            if category in commands:
                commands[category].append(command)
            else:
                commands[category] = [command]
        return add
        

    def __execute__(self, *args, **kwargs):
        print("ARGS2=", args, kwargs)
        category = kwargs['category']
        for command in commands[category]:
            command(args[0], kwargs)

    def auth(self, access_token):
        '''Bot registration

        Arguments:
            access_token {str} -- Access token 
        '''
        self.VK = VK(token=access_token, api_version=self.api_version)
        self.Redis.set('VK_token', access_token)

    def search_email(self, message):
        '''Search email address in a message from the user VK

        Arguments:
            message {str} -- A message from the user VK
        '''
        pattern1 = re.compile('[a-z0-9]+@[a-z0-9]+\.[a-z]+')
        regexes = 'yandex\.ru', 'mail\.ru', 'gmail\.com'
        pattern2 = re.compile('|'.join('(?:{0})'.format(x) for x in regexes))
        email = re.search(pattern1, message)
        if email:

            if re.search(pattern2, email.group()):
                return 1, email.group()
            return 0, 'null'
        return -1, 'null'

    def add_to_Redis(self, email, ids, token):
        '''Adding to the DBMS

        Arguments:
            email {str} --  E-mail address (Key)
            ids {list} -- The list of identifiers of VK users associated with the e-mail address (Value)
        '''
        self.Redis.sadd(email, token+'|'+str(ids))

    def get_id_from_Redis(self, email):
        '''Getting identifiers (value) by e-mail address (key) in the DBMS

        Arguments:
            email {str} --  E-mail address (Key)
        Returns:
            ids -- The list of identifiers of VK users associated with the e-mail address (Value)
        '''

        return self.Redis.smembers(email).decode()

    def get_emails_from_Redis(self):
        '''Getting  e-mail address (key) in the DBMS

        Arguments:


        Returns:
            [str] -- List of e-mail addresses
        '''
        return self.Redis.keys(pattern='[a-z0-9]*@[a-z0-9]*\.[a-z0-9]*')

    def get_link(self, email):
        '''

        Arguments:
            email {[type]} -- e-mail address
        '''
        link = ''
        if 'yandex' in email:
            ya_id = '5527ae60585949ba84b217997034aa06'
            link = 'https://oauth.yandex.ru/authorize?' + \
                'response_type=token&' + \
                'client_id=5527ae60585949ba84b217997034aa06&' + \
                'redirect_uri=https://notbotme.herokuapp.com/auth&' +\
                'login_hint={0}&state={0}'.format(email)

        return self.VK.utils.getShortLink(url=link)['short_url']

    def send_message(self, id, message):
        '''[summary]

        Arguments:
            id {[type]} -- vk user id
            message {[type]} -- message
        '''
        self.VK.messages.send(
            peer_id=id, random_id=random.randint(0, int(id)), message=message)

    @__add__(category='hello')
    def hello(self, *args, **kwargs):
        
        params = args[0]
        
        peer_id = params['peer_id']
        category = params['category']
        print("ARGS32=", self, peer_id, category)
        UserName = self.VK.users.get(user_ids=peer_id)
        UserName = UserName[0]['first_name']+' '+UserName[0]['last_name']
        resp1 = self.PAI.get_response(category)
        resp2 = self.PAI.get_response('name')
        resp3 = self.PAI.get_response('affairs')
        resp4 = self.PAI.get_response('can')
        resp5 = self.PAI.get_response('auth')
        self.send_message(id=peer_id, message=resp1+' ' +
                          UserName+'! '+resp2+self.Name+'.'+resp3+resp4+resp5)

    def dialog(self, message, peer_id, from_id):
        '''[summary]
        '''

        if peer_id != from_id:
            peer_id = from_id

        code = None
        email = None
        category = None
        
        if 'авторизация' in message.lower():
            code, email = self.search_email(message)
        else:
            category = self.PAI.get_category(message)
          
        self.__execute__(self,category=category, message=message, peer_id=peer_id)
        if code == 1:

            short_link = self.get_link(email)
            resp1 = self.PAI.get_response('link')
            resp2 = self.PAI.get_response('thanks')
            self.send_message(id=peer_id, message=resp1)
            self.send_message(id=peer_id, message=short_link)
            self.add_to_Redis(str(email), peer_id, 'erer4r4f44w54546')
            self.send_message(id=peer_id, message=resp2)

        elif code == 0:

            resp1 = self.PAI.get_response('unknown')
            resp2 = self.PAI.get_response('can')
            self.send_message(id=peer_id, message=resp1+resp2)

        elif code == -1:
            category = self.PAI.get_category(message.lower())
            resp = self.PAI.get_response(category)
            self.send_message(id=peer_id, message=resp)

        elif category == 'name':
            resp = self.PAI.get_response(category)
            self.send_message(id=peer_id, message=resp+' '+self.Name)

        else:
            resp = self.PAI.get_response(category)
            self.send_message(id=peer_id, message=resp)
