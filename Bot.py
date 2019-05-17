from vkapi import VK
import requests
import redis
import re
from pai import PaiFlow
import os


class Bot():
    def __init__(self, name="bot", group_id='', api_version=''):
        """[summary]

        Keyword Arguments:
            name {str} -- Bot name
            group_id {str} -- VK group identifier (default: {''})
            api_version {str} -- Version api VK (default: {''})
        """
        self.group_id = group_id
        self.Redis = redis.from_url(os.environ.get("REDIS_URL"), db=0)
        self.Name = name
        self.PAI = PaiFlow()
        self.PAI.build()
        self.api_version = api_version
        self.token = self.Redis.get("VK_token")
        if self.token != None:
            self.VK = VK(token=self.token.decode(),
                         api_version=self.api_version)

    def auth(self, access_token):
        """Bot registration

        Arguments:
            access_token {str} -- Access token 
        """
        self.VK = VK(token=access_token, api_version=self.api_version)
        self.Redis.set('VK_token', access_token)

    def search_email(self, message):
        """Search email address in a message from the user VK

        Arguments:
            message {str} -- A message from the user VK
        """
        pattern1 = re.compile('[a-z0-9]+@[a-z0-9]+\.[a-z]+')
        regexes = 'yandex\.ru', 'mail\.ru', 'gmail\.com'
        pattern2 = re.compile('|'.join('(?:{0})'.format(x) for x in regexes))
        email = re.search(pattern1, message)
        if email:

            if re.search(pattern2, email.group()):
                return 1, email.group()
            return 0, "null"
        return -1, "null"

    def add_to_Redis(self, email, ids, token):
        """Adding to the DBMS

        Arguments:
            email {str} --  E-mail address (Key)
            ids {list} -- The list of identifiers of VK users associated with the e-mail address (Value)
        """
        self.Redis.sadd(email, str(ids)+"|"+token)

    def get_id_from_Redis(self, email):
        """Getting identifiers (value) by e-mail address (key) in the DBMS

        Arguments:
            email {str} --  E-mail address (Key)
        Returns:
            ids -- The list of identifiers of VK users associated with the e-mail address (Value)
        """

        return self.Redis.smembers(email)

    def get_emails_from_Redis(self):
        """Getting  e-mail address (key) in the DBMS

        Arguments:


        Returns:
            [str] -- List of e-mail addresses
        """
        return self.Redis.keys(pattern="[a-z0-9]*@[a-z0-9]*\.[a-z0-9]*")

    def dialog(self, message, peer_id, from_id):
        """[summary]
        """
        if peer_id != from_id:
            peer_id = from_id
        UserName = self.VK.users.get(user_ids=peer_id)
        UserName = UserName[0]['first_name']+" "+UserName[0]['last_name']
        code = None
        email = None
        category = None

        if 'авторизация' in message.lower():
            code, email = self.search_email(message)
        else:
            category = self.PAI.get_category(message.lower())

        if code == 1:
            ya_id = '3ee652c711e9455c98afa34a2807e4f3'
            ya_link = 'oauth.yandex.ru/authorize?' + \
                'response_type=token&' + \
                'client_id=3ee652c711e9455c98afa34a2807e4f3&' + \
                'login_hint={0}'.format(email) 

            resp1 = self.PAI.get_response(8)
            self.VK.messages.send(
                peer_id=peer_id, random_id=0, message=resp1)
            
            self.VK.messages.send(
                peer_id=peer_id, random_id=0, message=ya_link)

            self.add_to_Redis(str(email), peer_id, "erer4r4f44w54546")

            resp2 = self.PAI.get_response(9)
            self.VK.messages.send(
                peer_id=peer_id, random_id=0, message=resp2)

        elif code == 0:

            resp1 = self.PAI.get_response(4)
            resp2 = self.PAI.get_response(5)
            self.VK.messages.send(
                peer_id=peer_id, random_id=0, message=resp1+resp2)
        elif code == -1:
            category = self.PAI.get_category(message.lower())
            resp1 = self.PAI.get_response(category)
            self.VK.messages.send(
                peer_id=peer_id, random_id=0, message=resp1)

        elif category == "1":
            resp1 = self.PAI.get_response(category)
            resp2 = self.PAI.get_response(5)
            resp3 = self.PAI.get_response(3)
            resp4 = self.PAI.get_response(7)
            resp5 = self.PAI.get_response(11)
            self.VK.messages.send(
                peer_id=peer_id, random_id=0, message=resp1+" "+UserName+"!"+resp5+self.Name+"."+resp2+resp3+resp4)

        elif category == "2":
            resp1 = self.PAI.get_response(category)
            self.VK.messages.send(
                peer_id=peer_id, random_id=0, message=resp1)

        elif category == "3":
            resp1 = self.PAI.get_response(category)
            self.VK.messages.send(
                peer_id=peer_id, random_id=0, message=resp1)

        elif category == "6":
            self.VK.messages.send(
                peer_id=peer_id, random_id=0, message=self.PAI.help())
        elif category == "11":
            resp1 = self.PAI.get_response(category)
            self.VK.messages.send(
                peer_id=peer_id, random_id=0, message=resp1+" "+self.Name)
