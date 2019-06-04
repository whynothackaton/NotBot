import json
import os
import threading
import time
import datetime
import threading
import requests
import re

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
        return redirect('/admin/tables/' + tablename)
    fields = [field for field in EmailServices.__dict__ if field[0] != '_']
    values = ['' for i in range(len(fields))]
    object = dict(zip(fields, values))
    return render_template('admin_new_table.html', object=object)


@app.route('/admin/tables/<tablename>/delete/<name>', methods=['GET', 'POST'])
def admin_delete_table(tablename, name):
    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(EmailServices).filter(EmailServices.name == name).delete()
    session.commit()
    session.close()
    return redirect('/admin/tables/' + tablename)


@app.route('/admin/tables/<tablename>/update/<name>', methods=['GET', 'POST'])
def admin_update_table(tablename, name):
    Session = sessionmaker(bind=engine)
    session = Session()
    obj = session.query(EmailServices).filter(
        EmailServices.name == name).first()

    if request.method == 'POST':
        for key in request.form:
            obj.__dict__[key] = request.form[key]
        print(str(obj))
        
        #return redirect('/admin/tables/' + tablename)

    print(str(obj))
    fields = [field for field in obj.__dict__ if field[0] != '_']
    values = [obj.__dict__[field] for field in fields]
    object = dict(zip(fields, values))
    print(object)
    session.commit()
    session.close()
    return render_template('admin_new_table.html', object=object)


@app.route('/admin/tables/<tablename>', methods=['GET', 'POST'])
def admin_table(tablename):
    Session = sessionmaker(bind=engine)
    session = Session()
    objects = session.query(EmailServices).all()
    session.close()
    str_objects = [str(object) for object in objects]
    return render_template('admin_tables.html',
                           tablename=tablename,
                           objects=str_objects)


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


@app.route('/authorization', methods=['GET', 'POST'])
def authorization():
    if 'code' in request.args:
        code = request.args['code']        
        state = request.args['state'].split('|')
        email = state[0]
        id = state[1]

        email_pattern = re.compile(r'@(?P<host>(?:[a-z0-9-]+))')
        host = re.search(email_pattern, email).group('host')
        print(host)

        Session = sessionmaker(bind=engine)
        session = Session()
        objects = session.query(EmailServices) \
            .filter(EmailServices.name == host) \
            .first()
        print(objects)
        session.close()
                
        url = objects.url
        data = {
            'client_id': objects.client_id,
            'client_secret': objects.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://notbotme.herokuapp.com/authorization'
        }
        response = requests.post(url=url, data=data)
        
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