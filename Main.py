from flask import Flask, request, Response
from NotBot.MailBox import MailBox
import json
import os
import threading
import time 
import datetime

app = Flask(__name__)



@app.route('/', methods=['POST'])
def incoming():
    data = json.loads(request.data)
    print(data)

    if data['type'] == 'confirmation':
        return '**'
    if data['type'] == 'message_new':
        return 1

    return Response(status=200)


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

    