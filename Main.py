from flask import Flask, request, Response
import json
import os
import threading
import time
import datetime
from Bot import Bot
app = Flask(__name__)
bot = Bot(name="bot",group_id="179748337", api_version="5.95")

@app.route('/login=<token>',methods=['GET'])
def login(token):
    bot.auth(token)
    return "OK"

@app.route('/email=<token>',methods=['GET', 'POST'])
def incoming(token):
    return token
        
@app.route('/bot',methods=['POST'])
def bot():
    
    data = json.loads(request.data)
    if data['type'] == 'confirmation':
        return '18258778'
    elif data['type'] == 'message_new':
        id = data['object']['from_id']
        bot.dialog(data['object']['text'], data['object']
                                ['from_id'], data['object']['peer_id'])
        return 'ok'
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    
    app.run(host='0.0.0.0', port=port)

    
