from flask import Flask, request, Response
from SocialNetworks.ViberNetwork import ViberNetwork
from viberbot.api.bot_configuration import BotConfiguration

app = Flask(__name__)
bot_configuration = BotConfiguration(name='NotBot',avatar='http://viber.com/avatar.jpg',auth_token='49615ef8ed67d5b9-50f2f0eb06ccc34a-8f1ed6e0cf602b98')
vn=ViberNetwork(bot_configuration)

@app.route('/', methods=['POST'])
def incoming():
    viber_request = vn.viber.parse_request(request.get_data())
    return Response(status=200)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443, debug=True)
    