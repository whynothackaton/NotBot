#from SocialNetwork import SocialNetwork
import vk
from requests import post

class VKNetwork():
    def __init__(self,token,group_id,vk_access_token,vk_api_version,):
        self.token=token
        self.group_id=group_id
        self.vk_api_version = vk_api_version
        self.vk_access_token = vk_access_token
        self.vk_session = vk.Session(access_token=vk_access_token)
        self.vk_api = vk.API(self.vk_session, v=vk_api_version)

    def send_message(self,id,message):
        self.vk_api.messages.send(
                        peer_id=id,
                        random_id='0',
        message=message)