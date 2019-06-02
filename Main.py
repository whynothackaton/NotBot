import json
import os
import threading
import time
import datetime
import threading
import requests

from flask import Flask, request, Response, render_template, redirect
from Bot import Bot
from MailBox import MailBox
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import EmailServices, Base
app = Flask(__name__)
bot = Bot(name='NotBot', api_version='5.95')
engine = create_engine(os.environ['DATABASE_URL'])
Base.metadata.create_all(engine)


@app.route('/paiflow', methods=['GET', 'POST'])
def paiflow():
    if request.method == 'POST':
        data = request.form
        bot.PAI.add('CATEGORY', data['category'])
    categories = bot.PAI.get_categories()
    return render_template('paiflow.html',
                           categories=[c.decode() for c in categories])


@app.route('/admin/tables/<tablename>/new', methods=['GET', 'POST'])
def admin_new_table(tablename):
    if request.method == 'POST':
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(EmailServices(request.form))
        session.commit()
        session.close()
        return 'OK'
    fields = [field for field in dir(EmailServices) if field[0] != '_']
    return render_template('admin_new_table.html', fields=fields)


@app.route('/admin/tables/<tablename>', methods=['GET', 'POST'])
def admin_table(tablename):
    Session = sessionmaker(bind=engine)
    session = Session()
    objects = session.query(EmailServices).all()
    session.close()
    str_objects = [str(object) for object in objects]
    return render_template('admin_tables.html', objects=str_objects)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return render_template('admin.html', tables=engine.table_names())


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
def login():
    if request.method == 'POST':
        data = request.form
        key = list(data.keys())[0]
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


@app.route('/authorization', methods=['GET', 'POST'])
def authorization():
    if 'code' in request.args:
        code = request.args['code']
        url = 'https://oauth.yandex.ru/token'  #! https://oauth.mail.ru/token
        data = {
            'client_id': bot.id_yandex_app,
            'client_secret': 'cb25abcfb77847afa762e04cdbc506fa',
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://notbotme.herokuapp.com/yandex_auth'
        }
        response = requests.post(url=url, data=data)
        state = request.args['state'].split('|')
        email = state[0]
        id = state[1]
        token = response.json()['access_token']
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
        message = None
        emails = bot.get_emails_from_Redis()
        for email in emails:
            token_id = bot.get_id_from_Redis(email)
            mb = MailBox(email.decode())
            token = token_id[0].decode().split('|')[0]
            print("Я НЕ СПЛЮ!!!", email, token)
            if mb.connection(token):
                message = mb.get_new_message()
                mb.close_connection()
                print("Я ЕЩЕ НЕ СПЛЮ!!!", email, token, message)
            if message is not None:
                for tid in token_id:
                    tid_decode = tid.decode()
                    tid_split = tid_decode.split('|')
                    token = tid_split[0]
                    id = tid_split[1]
                    print("TOKEN=", email, token, id)
                    bot.send_message(id=id, message=message)
        time.sleep(30)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    thread1 = threading.Thread(target=Main)
    thread1.start()
    app.run(host="0.0.0.0", port=port)