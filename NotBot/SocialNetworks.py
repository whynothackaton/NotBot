from .VKNetwork import VKNetwork
from .ViberNetwork import ViberNetwork
from viberbot.api.bot_configuration import BotConfiguration

class SocialNetworks():
    def __init__(self):
        self.VK_bot=VKNetwork(vk_access_token='66d88a983bd5b7f39de9db6f9235782db2b62a03160978a44c9ebc4e97558a335e7b1bf32317203799a5d',group_id=179748337,vk_api_version='5.92')
        bot_configuration = BotConfiguration(name='NotBot',avatar='https://pp.userapi.com/c850332/v850332246/105af0/pTe6rXEBU9E.jpg',auth_token='49615ef8ed67d5b9-50f2f0eb06ccc34a-8f1ed6e0cf602b98')
        self.Viber_bot=ViberNetwork(bot_configuration)

    def send(self,message,id,method):
        if method=='vk':
            self.VK_bot.send_message(id,message)
        if method=='viber':
            self.Viber_bot.send_message(id,message)
    def set_user(self,id):
        self.user_id=id