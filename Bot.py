from networkapi import NetworkAPI
import requests
import redis
import re
from pai import PaiFlow
import os
import random
from functools import wraps
from message import Message
from linkbuilder import LinkBuilder

commands = {}
default_commands = []


class Bot():
    def __init__(self, name='bot', api_version='', debug=False):
        '''[summary]

        Keyword Arguments:
            name {str} -- Bot name
            group_id {str} -- VK group identifier (default: {''})
            api_version {str} -- Version api VK (default: {''})
        '''
        print('SELF=', self)
        self.Name = name
        self.api_version = api_version
        self.message_pool = {}
        self.used_id = {}
        if not debug:
            self.PAI = PaiFlow()
            self.Redis = redis.from_url(os.environ.get('REDIS_URL'), db=0)

            self.vk_token = self.Redis.get('VK_token')
            if self.vk_token != None:
                self.VK = NetworkAPI(api_url='https://api.vk.com/method/',
                                     provider='VK',
                                     token=self.vk_token.decode(),
                                     api_version=self.api_version)

            self.id_yandex_app = self.extract_id('YANDEX_token')
            self.id_mail_app = self.extract_id('MAIL_token')
            print("YANDEX_TOKEN=", self.id_yandex_app)

    def extract_id(self, name):
        id_email_app = self.Redis.get(name)
        if id_email_app != None:
            id_email_app = id_email_app.decode()

        return id_email_app

    def __add__(category: str):
        '''[summary]
        Arguments:
            category {str} -- [description]
        Returns:
            [type] -- [description]
        '''

        def add(command: callable):
            if category is None:
                default_commands.append(command)
            else:
                if category in commands:
                    commands[category].append(command)
                else:
                    commands[category] = [command]

        return add

    def __execute__(self, *args, **kwargs):
        peer_id = kwargs['peer_id']
        if peer_id in self.used_id:
            category = self.used_id[peer_id]
        else:
            category = kwargs['category']
        if category not in commands:
            for command in default_commands:
                command(args[0], kwargs)
        else:
            for command in commands[category]:
                command(args[0], kwargs)

    def bot_auth(self, provider: str, token: str):
        '''Bot registration

        Arguments:
            access_token {str} -- Access token 
        '''
        if provider.lower() == 'vk':
            self.VK = NetworkAPI(api_url='https://api.vk.com/method/',
                                 provider=provider,
                                 token=token,
                                 api_version=self.api_version)

        if provider.lower() == 'yandex':
            self.id_yandex_app = token
        if provider.lower() == 'mail':
            self.id_mail_app = token

        print('email_token=', self.id_yandex_app, provider)
        self.Redis.set(provider.upper() + '_token', token)

    def search_email(self, message: str):
        ''' 
        Search email address in the string.
        First, any e-mail address is searched.
        Next, the search for supported services: yandex,mail,gmail.

        1) In case of finding the right service, the pair is returned (1, found e-mail)
        2) In the case of finding e-mail addresses are not supported service returns pair (0, found e-mail)
        3) In the absence of string e-mail address returns a pair of (-1 , None)

        Arguments:
            message {str} -- A message from the user VK
        '''
        email_pattern = re.compile(r'[a-z0-9]+@[a-z0-9]+\.[a-z]+')
        service_regexes = r'yandex\.ru', r'mail\.ru', r'gmail\.com'
        service_pattern = re.compile('|'.join('(?:{0})'.format(x)
                                              for x in service_regexes))
        email = re.search(email_pattern, message)
        if email:
            if re.search(service_pattern, email.group()):
                return 1, email.group()
            return 0, email.group()
        return -1, None

    def add_to_Redis(self, email: str, id: str, token: str):
        '''Adding to the DBMS

        Arguments:
            email {str} --  E-mail address (Key)
            id {str} --  Identifiers (Value)
            token {str} --- e-mail auth token (Value)
        '''
        self.Redis.sadd(email, token + '|' + str(id))

    def get_id_from_Redis(self, email: str) -> list:
        '''Getting identifiers (value) by e-mail address (key) in the DBMS

        Arguments:
            email {str} --  E-mail address (Key)
        Returns:
            list -- The list of pairs(token|id) associated with the e-mail address (Value)
        '''

        return list(self.Redis.smembers(email))[0].decode()

    def get_emails_from_Redis(self) -> list:
        '''Getting  e-mail address (key) in the DBMS

        Arguments:


        Returns:
            [str] -- List of e-mail addresses
        '''
        return self.Redis.keys(pattern='[a-z0-9]*@[a-z0-9]*\.[a-z0-9]*')

    def get_link(self, email: str, id: str) -> str:
        '''

        Arguments:
            email {[type]} -- e-mail address
        '''

        if 'yandex' in email:
            lb = LinkBuilder(
                url="https://oauth.yandex.ru/authorize",
                client_id=self.id_yandex_app,
                redirect_uri="https://notbotme.herokuapp.com/yandex_auth",
                response_type="code",
                scope="mail:imap_full",
                state=email + '|' + id)
        if '@mail' in email:
            lb = LinkBuilder(
                url="https://oauth.mail.ru/login",
                client_id=self.id_mail_app,
                redirect_uri="https://notbotme.herokuapp.com/mail_auth",
                response_type="code",
                scope="mail.imap",
                state=email + '|' + id)

        return self.VK.utils.getShortLink(url=lb.get())['short_url']

    def send_message(self, id: str, message: str, network='VK'):
        '''[summary]

        Arguments:
            id {[type]} -- User id
            message {[type]} -- Message
        '''
        if network is 'VK':
            self.VK.messages.send(peer_id=id,
                                  random_id=random.randint(0, int(id)),
                                  message=message)

    @__add__(category='start')
    def __start(self, *args, **kwargs):

        params = args[0]
        peer_id = params['peer_id']
        category = params['category']
        UserName = self.VK.users.get(user_ids=peer_id)
        UserName = UserName[0]['first_name'] + ' ' + UserName[0]['last_name']

        greeting = self.PAI.get_response('greeting')
        acquaintance = self.PAI.get_response('acquaintance')
        affairs = self.PAI.get_response('affairs')
        authorization_help = self.PAI.get_response('authorization_help')

        self.send_message(id=peer_id,
                          message=greeting + ', ' + UserName + '! ' +
                          acquaintance + ' ' + self.Name + '. ' + affairs +
                          '.\n' + authorization_help)

    @__add__(category='greeting')
    def __greeting(self, *args, **kwargs):

        params = args[0]
        peer_id = params['peer_id']
        category = params['category']
        UserName = self.VK.users.get(user_ids=peer_id)
        UserName = UserName[0]['first_name']
        greeting = self.PAI.get_response(category)
        self.send_message(id=peer_id,
                          message=greeting + ', ' + UserName + '! ')

    @__add__(category='authorization')
    def __authorization(self, *args, **kwargs):
        params = args[0]
        message = params['message']
        peer_id = params['peer_id']
        code, email = self.search_email(message)

        if code == 1:  # correct email
            short_link = self.get_link(email, str(peer_id))
            link = self.PAI.get_response('link')
            self.send_message(id=peer_id, message=link)
            self.send_message(id=peer_id, message=short_link)

        elif code == 0:  # incorrect email

            unknown = self.PAI.get_response('unknown service')
            #affairs = self.PAI.get_response('affairs')
            self.send_message(id=peer_id, message=unknown)

        elif code == -1:  # without email
            self.send_message(id=peer_id, message='Вы не указали email')

    @__add__(category='sending')
    def send_email(self, *args, **kwargs):
        params = args[0]
        message = params['message']
        peer_id = params['peer_id']
        if peer_id in self.message_pool:
            self.message_pool[peer_id].set_this_item(message)
            if self.message_pool[peer_id].get_occupancy() == 100:
                print("MESSAGE=", self.message_pool[peer_id].toJSON())
                self.send_message(id=peer_id, message="Thanks")
                del self.used_id[peer_id]
        else:
            self.used_id[peer_id] = 'sending'
            self.message_pool[peer_id] = Message()
            self.message_pool[peer_id].set_this_item(peer_id)
        self.send_message(id=peer_id,
                          message=self.message_pool[peer_id].get_next_item())

    @__add__(category=None)
    def default_command(self, *args, **kwargs):
        params = args[0]
        category = params['category']
        peer_id = params['peer_id']
        response = self.PAI.get_response(category)
        self.send_message(id=peer_id, message=response)

    def dialog(self, message: str, peer_id: str, from_id: str):
        '''[summary]
        '''

        if peer_id != from_id:
            peer_id = from_id

        category = self.PAI.get_category(message)

        self.__execute__(self,
                         category=category,
                         message=message,
                         peer_id=peer_id)
