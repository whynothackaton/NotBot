from flask import Flask, request, Response
from NotBot.SocialNetworks import SocialNetworks
from viberbot.api.bot_configuration import BotConfiguration
from NotBot.MailBox import MailBox
import json
import os
import threading
import time 

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
            sn.set_user( data['object']['from_id']  )
            sn.send(id=sn.user_id,message="https://notbotme.herokuapp.com/auth",method='vk')
    return Response(status=200)

@app.route('/login', methods=['POST'])
def login():
    email_domen=request.form['domen']
    login=request.form['username']
    password=request.form['password']
    MBoxs.append(MailBox(email_domen,login,password))
    return "OK"

@app.route('/auth', methods=['POST'])
def auth():
    return  render_template('login.html')

def Main():
    while True:
        #sn.send(id='207189016',message="12",method='vk')        
        time.sleep(15)
        date_time = datetime.datetime.now()
        ekzemplyar_mailbox.get_new_message(date_time)
        

if __name__ == "__main__":
    thread1 = threading.Thread(target=Main)
    thread1.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

    