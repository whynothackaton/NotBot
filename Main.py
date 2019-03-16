from flask import Flask, request, Response
from NotBot.ViberNetwork import ViberNetwork
from NotBot.VKNetwork import VKNetwork
from viberbot.api.bot_configuration import BotConfiguration
import json
import os
import threading
import time 

app = Flask(__name__)
#bot_configuration = BotConfiguration(name='NotBot',avatar='http://viber.com/avatar.jpg',auth_token='49615ef8ed67d5b9-50f2f0eb06ccc34a-8f1ed6e0cf602b98')
#vn=ViberNetwork(bot_configuration)
vk_bot=VKNetwork(vk_access_token='66d88a983bd5b7f39de9db6f9235782db2b62a03160978a44c9ebc4e97558a335e7b1bf32317203799a5d',group_id=179748337,vk_api_version='5.92')


@app.route('/', methods=['POST'])
def incoming():
    data = json.loads(request.data)
    if data['type'] == 'confirmation':
        return '18258778'
    return Response(status=200)

def Main():
    while True:
        vk_bot.send_message(id='207189016',message="hello")
        time.sleep(15)


if __name__ == "__main__":
    thread1 = threading.Thread(target=Main)
    thread1.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

    