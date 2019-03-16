import vk
from requests import post

class VKNetwork():
    def __init__(self,group_id,vk_access_token,vk_api_version):
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

    def delete(self,message_id):
        self.vk_api.messages.delete(message_ids=[message_id],group_id=self.group_id,delete_for_all=0)