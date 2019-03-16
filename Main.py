from flask import Flask, request, Response
from NotBot.SocialNetworks import SocialNetworks
from viberbot.api.bot_configuration import BotConfiguration
import json
import os
import threading
import time 
import MailBox

app = Flask(__name__)
#bot_configuration = BotConfiguration(name='NotBot',avatar='http://viber.com/avatar.jpg',auth_token='49615ef8ed67d5b9-50f2f0eb06ccc34a-8f1ed6e0cf602b98')
#vn=ViberNetwork(bot_configuration)

sn= SocialNetworks()

@app.route('/', methods=['POST'])
def incoming():
    data = json.loads(request.data)
    if data['type'] == 'confirmation':
        return '18258778'
    if data['type'] == 'message_new':
        sn.set_user( data['object']['from_id']  )
        sn.send(id=sn.user_id,message="Hello",method='vk')
    return Response(status=200)


def Main():
    while True:
        sn.send(id='207189016',message="12",method='vk')
        time.sleep(15)


if __name__ == "__main__":
    thread1 = threading.Thread(target=Main)
    thread1.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

    