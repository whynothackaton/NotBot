#from SocialNetwork import SocialNetwork

from viberbot import Api
from viberbot import Api
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
import os



class ViberNetwork():
    def __init__(self,bot_configuration):
        self.bot_configuration=bot_configuration
        self.viber=Api(self.bot_configuration)
        
    def send_message(self,message,id):
        self.viber.send_messages(id,message)

