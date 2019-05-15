from vkapi import VK
import requests
import redis
import re

class Bot():
    def __init__(self, group_id='', access_token='', api_version=''):
        """[summary]

        Keyword Arguments:
            group_id {str} -- VK group identifier (default: {''})
            access_token {str} -- Access token (default: {''})
            api_version {str} -- Version api VK (default: {''})
        """
        self.VK = VK(token=access_token, api_version=api_version)
        self.group_id = group_id
        self.Redis = redis.StrictRedis(host='localhost', port=6379, db=1)

    def search_email(self,message):
        """Search email address in a message from the user VK
        
        Arguments:
            message {str} -- A message from the user VK
        """
        pattern=re.compile('[a-z0-9]+@[a-z0-9]+\.[a-z]+')
        email=re.search(pattern,message)
        return email

    def add_to_Redis(self, email, ids):
        """Adding to the DBMS

        Arguments:
            email {str} --  E-mail address (Key)
            ids {list} -- The list of identifiers of VK users associated with the e-mail address (Value)
        """
        self.Redis.set(email, ids)

    def add_to_Redis(self, email, ids):
        """Adding to the DBMS

        Arguments:
            email {str} --  E-mail address (Key)
            ids {list} -- The list of identifiers of VK users associated with the e-mail address (Value)
        """
        self.Redis.set(email, ids)
    def get_id_from_Redis(self,email):
        """Getting identifiers (value) by e-mail address (key) in the DBMS

        Arguments:
            email {str} --  E-mail address (Key)
        Returns:
            ids -- The list of identifiers of VK users associated with the e-mail address (Value)
        """
        return self.Redis.get(email)

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
                if update['type']=='message_new':
                    id=update['object']['from_id']
                    
                    email=self.search_email(update['object']['text'])
                    if email:
                        self.add_to_Redis(email.group,id)
                    print(self.get_id_from_Redis(email))
            self.ts = self.longPoll['ts']


bot = Bot("179748337", "66d88a983bd5b7f39de9db6f9235782db2b62a03160978a44c9ebc4e97558a335e7b1bf32317203799a5d", "5.95")
bot.testLP()
