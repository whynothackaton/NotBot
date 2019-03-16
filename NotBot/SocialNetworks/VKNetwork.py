#from SocialNetwork import SocialNetwork
import vk
from requests import post

class VKNetwork():
    def __init__(self,token,group_id):
        self.token=token
        self.group_id=group_id


    def send_message(self):
