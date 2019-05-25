from flask import Flask, request, Response, render_template, redirect
import json
import os
import threading
import time
import datetime
from Bot import Bot
from MailBox import MailBox
import threading

app = Flask(__name__)
bot = Bot(name='bot', api_version='5.95')


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


@app.route('/mail_auth', methods=['GET', 'POST'])
def incoming_mail():
    if 'code' in request.args:

         print('TOKEN =', 'code' in request.args, request.data, request.get_json(),
          request.form)
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
            mb = MailBox(email)
            token_id = bot.get_id_from_Redis(email).split('|')
            token = token_id[0]
            id = token_id[1]
            mb.connection(token)
            print('peer_id=', id)
            print('token=', token)
        time.sleep(30)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    #thread1 = threading.Thread(target=Main)
    #thread1.start()
    app.run(host="0.0.0.0", port=port)

    # достали токен из базы
    #token = ''
    # mb.connection(token)
    #new_message = mb.get_new_message()
    # if new_message is not None:
    #    pass  # отправляем new_message в вк
