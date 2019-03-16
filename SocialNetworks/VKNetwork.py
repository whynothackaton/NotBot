from SocialNetwork import SocialNetwork
import vk
from requests import post

class VKNetwork(SocialNetwork):
    def __init__(self,token,group_id):
        self.token=token
        self.group_id=group_id


    def connect_to_long_poll(self):
        try:
            self.longPoll = self.vk_api.groups.getLongPollServer(group_id=self.group_id)
            self.server = self.longPoll['server']
            self.key = self.longPoll['key']
            self.ts = self.longPoll['ts']

        except Exception as e:
            error = "Error with connect to vk longPoll: " + str(e)
            print(error)

    def vk_run(self):
        try:
                self.longPoll = post(
                    '%s' % self.server,
                    data={
                        'act': 'a_check',
                        'key': self.key,
                        'ts': self.ts,
                        'wait': 25
                        }).json()

                    if self.longPoll['updates'] and len(self.longPoll['updates']) != 0:
                        for update in self.longPoll['updates']:
                        if update['type'] == 'message_new':
                            print("Q")
        except Exception as e:
            print(e)