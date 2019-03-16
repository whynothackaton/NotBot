from SocialNetwork import SocialNetwork
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest

bot_configuration = BotConfiguration(
	name='NotBot',
	avatar='http://viber.com/avatar.jpg',
	auth_token='**')


class ViberNetwork(SocialNetwork):
    def __init__(self,bot_configuration)
        self.bot_configuration=bot_configuration
        self.viber=Api(self.bot_configuration)
    def send_message(self):
        