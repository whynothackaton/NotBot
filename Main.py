from flask import Flask, request, Response,render_template
from NotBot.SocialNetworks import SocialNetworks
from viberbot.api.bot_configuration import BotConfiguration
from NotBot.MailBox import MailBox
import json
import os
import threading
import time 
import datetime

app = Flask(__name__)

MBoxs=[]
sn= SocialNetworks()

@app.route('/', methods=['POST'])
def incoming():
    data = json.loads(request.data)
    print(data)

    if data['type'] == 'confirmation':
        return '18258778'
    if data['type'] == 'message_new':
        if 'авторизация' in data['object']['text'].lower():
            s=data['object']['text'].split(' ')
            sn.set_user( data['object']['from_id']  )
            ms=MailBox(s[1],s[2],s[3],sn.user_id)
            ms.connection()
            MBoxs.append(ms)
            sn.delete(data['object']['conversation_message_id'])
            sn.send("Успешно",sn.user_id,'vk')
    return Response(status=200)

@app.route('/login', methods=['POST'])
def login():
    email_domen=request.form['domen']
    login=request.form['username']
    password=request.form['password']
    #
    return "OK"

@app.route('/auth', methods=['POST','GET'])
def auth():
    return  render_template('login.html')

def Main():
    while True:       
        time.sleep(15)
        date_time = datetime.datetime.now()
        for mbx in MBoxs:
            msg=mbx.get_new_message(date_time)
            if msg is not None:
                sn.send(msg,mbx.id)
        

if __name__ == "__main__":
    thread1 = threading.Thread(target=Main)
    thread1.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

    