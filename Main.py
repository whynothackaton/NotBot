from flask import Flask, request, Response, render_template, redirect
import json
import os
import threading
import time
import datetime
from Bot import Bot
from MailBox import MailBox
import threading
import requests

app = Flask(__name__)
bot = Bot(name='NotBot', api_version='5.95')


@app.route('/paiflow', methods=['GET', 'POST'])
def paiflow():
    if request.method == 'POST':
        data = request.form
        bot.PAI.add('CATEGORY', data['category'])
    categories = bot.PAI.get_categories()
    print('****', categories)
    return render_template('paiflow.html',
                           categories=[c.decode() for c in categories])


@app.route('/paiflow/<category>', methods=['GET', 'POST'])
def paiflow_categories(category):
    questions = bot.PAI.get_questions(category=category)
    responses = bot.PAI.get_responses(category=category)
    if request.method == 'POST':
        data = request.form
        if 'T1' in data and 'T2' in data:
            bot.PAI.add(data['T1'], data['T2'])
        return redirect('/paiflow/' + category)
    return render_template('categories.html',
                           category=category,
                           questions=questions,
                           responses=responses)


@app.route('/paiflow/delete_val/category=<category>&key=<key>&value=<value>',
           methods=['GET', 'POST'])
def paiflow_delete(category, key, value):
    bot.PAI.delete(key, value)
    return redirect('/paiflow/' + category)


@app.route('/login', methods=['GET', 'POST'])
def logauth():
    if request.method == 'POST':
        data = request.form
        print(data)
        key = list(data.keys())[0]
        print(key)
        bot.bot_auth(provider=key.split('_')[0], token=data[key])
        return redirect("/")
    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/reset', methods=['GET', 'POST'])
def resetRedis():
    bot.Redis.flushall()
    return redirect('/')


@app.route('/yandex_auth', methods=['GET', 'POST'])
def incoming_yandex():
    print('TOKEN =', request.args, request.data, request.get_json(),
          request.form)
    return redirect('/')


@app.route('/supported_email', methods=['GET', 'POST'])
def supported_email():
    if request.method == 'POST':
        data = request.form
        bot.Redis.sadd('EMAILS', data['email'])
    emails = list(bot.Redis.smembers('EMAILS'))
    return render_template('emails.html', emails=[e.decode() for e in emails])


@app.route('/receiver', methods=['GET', 'POST'])
def receiver():
    return render_template('_receiver.html')


@app.route('/mail_auth', methods=['GET', 'POST'])
def incoming_mail():
    if 'code' in request.args:
        code = request.args['code']

        url = 'https://oauth.mail.ru/token'
        data = {
            'client_id': bot.id_mail_app,
            'client_secret': '55f04d3e6f1146f4b5b0ec8005c060a2',
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://notbotme.herokuapp.com/mail_auth'
        }

        response = requests.post(url=url, data=data)

        state = request.args['state'].split('|')
        email = state[0]
        id = state[1]
        token = response.json()['access_token']
        print("TETETETET=", email, id, token)
        bot.add_to_Redis(email, id, token)
        return "Спасибо!"

    return redirect('/')


@app.route('/bot', methods=['POST'])
def botserver():
    data = json.loads(request.data)
    if data['type'] == 'confirmation':
        return '18258778'

    elif data['type'] == 'message_new':
        id = data['object']['from_id']
        bot.dialog(data['object']['text'], data['object']['from_id'],
                   data['object']['peer_id'])
        return 'ok'
    return 'ok'


def Main():
    while True:
        emails = bot.get_emails_from_Redis()
        for email in emails:
            token_id = bot.get_id_from_Redis(email).split('|')
            email = token
            token = token_id[0]
            id = token_id[1]
            print("TOKEN=", email, token, id)
            #! message
            #*
            #* print("message")
            #* bot.send_message(id=id,message=message)
        time.sleep(30)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    thread1 = threading.Thread(target=Main)
    thread1.start()
    app.run(host="0.0.0.0", port=port)

    # достали токен из базы
    #token = ''
    # mb.connection(token)
    #new_message = mb.get_new_message()
    # if new_message is not None:
    #    pass  # отправляем new_message в вк
