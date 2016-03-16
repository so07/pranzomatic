
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import collections
from pranzomatic import pranzomatic
import datetime
import hashlib
from pranzomatic.myfortune import fortune
import os

app = Flask(__name__)

app.config["DEBUG"] = True

"""
def connect():
    connection = mysql.connector.connect(
                    user='Pranzomatic',
                    password='ilpranzoèservito',
                    host='Pranzomatic.mysql.pythonanywhere-services.com',
                    database='Pranzomatic$default'
                    )
    return connection;
"""
def get_today():
    return datetime.datetime.today().strftime("%Y-%m-%d")

def random_string(length=12):
    import random, string
    random_string = ''.join(random.choice(string.ascii_uppercase) for i in range(length))
    return random_string

def get_key(name):
    string=name+get_today()
    return hashlib.sha224(string.encode('utf-8')).hexdigest()

def connect():
    conn = sqlite3.connect('pranzomatic.db')
    return conn

def check_password(pwd):
    #Questo Paolo non lo dovrà scomprire mai... Sarà il nostro segreto!
    return pwd == "porchettoni!"

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/call', methods=['GET'])
@app.route('/call', methods=['POST'])
def call():

    if request.form:

        if not check_password(request.form["@password"]):
            return render_template('call.html')

        conn = connect()
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS tablemates (date text, name text, present int, key text)''')

        c.execute('''CREATE TABLE IF NOT EXISTS winners (date text, winner text)''')

        today = get_today()
        c.execute("DELETE FROM tablemates WHERE date='"+today+"'")
        tablemates = pranzomatic.pranzomatic_tablemates()

        mailing_list = pranzomatic.pranzomatic_mailing_dict(tablemates)
        #tablemates = ['sergio']
        for t in tablemates:
            key = get_key(t)
            c.execute("INSERT INTO tablemates VALUES ('"+today+"', '"+t+"', '0', '"+key+"')")
            user_mail = mailing_list[t]
            body = "http://pranzomatic.pythonanywhere.com/confirm?t="+t+"&k="+key
            pranzomatic.send_mail(body, [user_mail], "pranzomatic wants you ...")

        conn.commit()
        conn.close()

        return render_template('called.html', tablemates=tablemates)

    return render_template('call.html')


@app.route('/roll')
def roll():

    conn = connect()
    c = conn.cursor()

    today = get_today()

    result = c.execute("SELECT * FROM tablemates WHERE date='"+today+"'")
    rows = result.fetchall()
    tablemates = { i[1] : i[2] for i in rows }

    #tablemates = {'Mattia': 1, 'Sergio': 1, 'Paolo': 0, 'Michela': 0, 'Gino': 0}

    tablemates = collections.OrderedDict(sorted(tablemates.items()))
    conn.close()

    return render_template('roll.html', tablemates=tablemates)


@app.route('/rolled', methods=['POST'])
def rolled():

    tablemates = []

    if not check_password(request.form["@password"]):
        return redirect(url_for('roll'))

    for t in request.form:
        if t == "@roll":
            continue
        if t == "@password":
            continue

        tablemates.append(t.lower())

    winner = pranzomatic.pranzomatic_roll(tablemates)

    if not app.config['DEBUG']:
       conn = connect()
       c = conn.cursor()

       today = get_today()

       c.execute("DELETE FROM winners WHERE date='"+today+"'")
       c.execute("INSERT INTO winners VALUES ('"+today+"', '"+winner+"')")
       conn.commit()
       conn.close()

    quote = fortune.get_quote()
    if quote:
       winner += "\n\n%s" % quote

    pranzomatic.pranzomatic_distribution(tablemates, os.path.join('mysite', 'distributions', 'today.png'))
    pranzomatic.pranzomatic_distribution(tablemates, os.path.join('mysite', 'distributions', get_today()+'.png'))

    mailing_list = pranzomatic.pranzomatic_mailing_list(tablemates)
    pranzomatic.send_mail(winner, mailing_list)

    if not app.config['DEBUG']:
        pranzomatic.send_tweet(winner)

    return render_template('rolled.html', tablemates=tablemates, winner=winner)

@app.route('/confirm')
def confirm():

    t = request.args.get('t')
    k = request.args.get('k')

    if t and k:

        conn = connect()
        c = conn.cursor()

        updated = c.execute("UPDATE tablemates SET present=1 WHERE name='"+t+"' AND key='"+k+"'")

        conn.commit()
        conn.close()

        if updated.rowcount >= 1:
            return render_template('confirm.html', t=t)

    return "C'HAI PROVATO!!"
