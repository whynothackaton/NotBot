from flask import Flask, request, Response
import json
import os
import threading
import time
import datetime
from Bot import Bot
from MailBox import MailBox
import threading

app = Flask(__name__)
bot = Bot(name="bot",group_id="179748337", api_version="5.95")
mb = MailBox('rollabushka@yandex.ru') 

@app.route('/log=<token>',methods=['GET','POST'])
def logauth(token):
    bot.auth(token)
    return "OK"


@app.route('/access_token/=<token>', methods=['GET', 'POST'])
def incoming(token):
    mb.connection(token)
    new_message = mb.get_new_message()
    if new_message is not None:
        pass # отправляем new_message в вк
    mb.close_connection()
        
@app.route('/bot',methods=['POST'])
def botserver():
    
    data = json.loads(request.data)
    if data['type'] == 'confirmation':
        return '18258778'
    elif data['type'] == 'message_new':
        id = data['object']['from_id']
        bot.dialog(data['object']['text'], data['object']
                                ['from_id'], data['object']['peer_id'])
        return 'ok'

def Main():
    while True:       
        time.sleep(15)
        emails = bot.get_emails_from_Redis()
        email="medvedev0denis@yandex.ru"
        st=bot.get_id_from_Redis(email)
        peer_id =st[0]
        token = st[1]
        bot.VK.messages.send(
                peer_id=peer_id, random_id=0, message="Вам новое письмо")

        

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    thread1 = threading.Thread(target=Main)
    thread1.start()
    app.run(host='0.0.0.0', port=port)   

    
