from .VKNetwork import VKNetwork
from .ViberNetwork import TGNetwork


class SocialNetworks():
    def __init__(self):
        self.VK_bot=VKNetwork(vk_access_token='66d88a983bd5b7f39de9db6f9235782db2b62a03160978a44c9ebc4e97558a335e7b1bf32317203799a5d',group_id=179748337,vk_api_version='5.92')
        self.TG_bot=TGNetwork('898225498:AAHUIh-SHjcQr1XdDPu4V1xWPghw6kx6__E')

    def send(self,message,id,method):
        if method=='vk':
            self.VK_bot.send_message(id,message)
        if method=='tg':
            self.TG_bot.send_message(id,message)
    def set_user(self,id):
        self.user_id=id