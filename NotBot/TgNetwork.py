#from SocialNetwork import SocialNetwork


import os



class TGNetwork():
    def __init__(self,token):
        self.token=token
        
    def send_message(self,message,id):
        self.viber.send_messages(id,message)

