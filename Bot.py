from vkapi import VK
import requests
import redis
import re
from pai import PaiFlow


class Bot():
    def __init__(self, name="bot", group_id='', vk_access_token='', api_version=''):
        """[summary]

        Keyword Arguments:
            name {str} -- Bot name
            group_id {str} -- VK group identifier (default: {''})
            access_token {str} -- Access token (default: {''})
            api_version {str} -- Version api VK (default: {''})
        """
        self.VK = VK(token=vk_access_token, api_version=api_version)
        self.group_id = group_id
        self.Redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
        self.Name = name
        self.PAI = PaiFlow()
        self.PAI.build()

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

    def add_to_Redis(self, email, ids):
        """Adding to the DBMS

        Arguments:
            email {str} --  E-mail address (Key)
            ids {list} -- The list of identifiers of VK users associated with the e-mail address (Value)
        """
        self.Redis.sadd(email, ids)

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

        return self.Redis.keys()

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
            resp1 = self.PAI.get_response(8)
            self.VK.messages.send(
                peer_id=peer_id, random_id=0, message=resp1)

            self.add_to_Redis(str(email), peer_id)

            resp2 = self.PAI.get_response(9)
            self.VK.messages.send(
                peer_id=peer_id, random_id=0, message=resp2)

        elif code == 0:

            resp1 = self.PAI.get_response(4)
            resp2 = self.PAI.get_response(5)
            self.VK.messages.send(
                peer_id=peer_id, random_id=0, message=resp1+resp2)

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

    def testLP(self):
        self.r = self.VK.groups.getLongPollServer(group_id=self.group_id)
        self.ts = self.r['ts']

        while True:
            self.longPoll = requests.post(
                '%s' % self.r['server'],
                data={
                    'act': 'a_check',
                    'key': self.r['key'],
                    'ts': self.ts,
                    'wait': 25
                }).json()

            for update in self.longPoll['updates']:
                if update['type'] == 'message_new':
                    id = update['object']['from_id']
                    self.dialog(update['object']['text'], update['object']
                                ['from_id'], update['object']['peer_id'])

            self.ts = self.longPoll['ts']


bot = Bot("bot", "**",
          "**", "5.95")
bot.testLP()
