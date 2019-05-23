from vkapi import VK
import requests
import redis
import re
from pai import PaiFlow
import os
import random
from functools import wraps


commands = {}
default_commands = []


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

            self.vk_token = self.Redis.get('VK_token')
            if self.vk_token != None:
                self.VK = VK(token=self.vk_token.decode(),
                             api_version=self.api_version)

            self.yandex_id = self.Redis.get('YANDEX_token')
            if self.yandex_id != None:
                self.yandex_id = self.yandex_id.decode()

    def __add__(category):
        def add(command):
            if category is None:
                default_commands.append(command.__name__)
            else:
                if category in commands:
                    commands[category].append(command.__name__)
                else:
                    commands[category] = [command.__name__]
        return add

    def __execute__(self, *args, **kwargs):
        category = kwargs['category']
        if category not in commands:
            for command in default_commands:
                getattr(self,command)(args[0], kwargs)
        else:
            for command in commands[category]:
                getattr(self,command)(args[0], kwargs)

    def bot_auth(self, provider, token):
        '''Bot registration

        Arguments:
            access_token {str} -- Access token 
        '''
        if provider.lower() is 'vk':
            self.VK = VK(token=token, api_version=self.api_version)

        if provider.lower() is 'yandex':
            self.yandex_id = token
        print("YANDEX_token=",self.yandex_id,provider)
        self.Redis.set(provider.upper()+'_token', token)

    def search_email(self, message):
        '''Search email address in a message from the user VK

        Arguments:
            message {str} -- A message from the user VK
        '''
        email_pattern = re.compile('[a-z0-9]+@[a-z0-9]+\.[a-z]+')
        service_regexes = 'yandex\.ru', 'mail\.ru', 'gmail\.com'
        service_pattern = re.compile(
            '|'.join('(?:{0})'.format(x) for x in service_regexes))
        email = re.search(email_pattern, message)
        if email:

            if re.search(service_pattern, email.group()):
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
            link = f'https://oauth.yandex.ru/authorize?' + \
                f'response_type=token&' + \
                f'client_id={self.yandex_id}&' + \
                f'redirect_uri=https://notbotme.herokuapp.com/auth&' +\
                f'login_hint={email}&state={email}'

        return self.VK.utils.getShortLink(url=link)['short_url']

    def send_message(self, id, message, network='VK'):
        '''[summary]

        Arguments:
            id {[type]} -- vk user id
            message {[type]} -- message
        '''
        if network is 'VK':
            self.VK.messages.send(
                peer_id=id, random_id=random.randint(0, int(id)), message=message)

    @__add__(category='greeting')
    def __greeting(self, *args, **kwargs):

        params = args[0]
        peer_id = params['peer_id']
        category = params['category']
        UserName = self.VK.users.get(user_ids=peer_id)
        UserName = UserName[0]['first_name']+' '+UserName[0]['last_name']

        greeting = self.PAI.get_response(category)
        acquaintance = self.PAI.get_response('acquaintance')
        affairs = self.PAI.get_response('affairs')
        authorization_help = self.PAI.get_response('authorization help')

        self.send_message(id=peer_id, message=greeting+' ' +
                          UserName+'! '+acquaintance+self.Name+'.'+affairs+' '+authorization_help)

    @__add__(category='authorization')
    def __authorization(self, *args, **kwargs):
        params = args[0]
        message = params['message']
        peer_id = params['peer_id']
        code, email = self.search_email(message)

        if code == 1:  # correct email
            short_link = self.get_link(email)
            link = self.PAI.get_response('link')
            self.send_message(id=peer_id, message=link)
            self.send_message(id=peer_id, message=short_link)

        elif code == 0:  # incorrect email

            unknown = self.PAI.get_response('unknown service')
            affairs = self.PAI.get_response('affairs')
            self.send_message(id=peer_id, message=unknown+affairs)

        elif code == -1:  # without email
            self.send_message(id=peer_id, message="Вы не указали email")

    @__add__(category=None)
    def default_command(self, *args, **kwargs):
        params = args[0]
        category = params['category']
        peer_id = params['category']
        response = self.PAI.get_response(category)
        self.send_message(id=peer_id, message=response)

    def dialog(self, message, peer_id, from_id):
        '''[summary]
        '''

        if peer_id != from_id:
            peer_id = from_id

        category = self.PAI.get_category(message)

        self.__execute__(self, category=category,
                         message=message, peer_id=peer_id)
