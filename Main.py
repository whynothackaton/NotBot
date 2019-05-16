from flask import Flask, request, Response
import json
import os
import threading
import time
import datetime

app = Flask(__name__)



@app.route('/email=<token>',methods=['GET', 'POST'])
def incoming(token):
    return token
        

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

    
