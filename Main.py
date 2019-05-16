from flask import Flask, request, Response
import json
import os
import threading
import time
import datetime

app = Flask(__name__)

@app.route('access_token/=<token>', methods=['GET', 'POST'])
def incoming(token):
    mb.connection(token)
    new_message = mb.get_new_message()
    if new_message is not None:
        pass # отправляем new_message в вк
    mb.close_connection()
        

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    mb = MailBox('rollabushka@yandex.ru')        

    
