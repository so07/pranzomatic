#!/usr/bin/env python
import os
import sys
import configparser as ConfigParser
import smtplib
import tweepy
import numpy as np

from distutils.util import strtobool


__version__ = 'v0.6'


def random_num(_max):
    return np.random.random_integers(0, _max)


def random_restaurant(distribution):
    return distribution[random_num(len(distribution)-1)]


def read_distribution(config_file):
    cp = ConfigParser.ConfigParser(allow_no_value=True)
    cp.read(config_file)
    t = {}
    for name in cp.sections():
        t[name] = { 'mail'    : cp.get(name, 'mail'),
                    'choices' : cp.get(name, 'choices').split() }
    return t


def get_distribution (tablemates, config_file='config.ini'):

    config_path = os.path.dirname(os.path.abspath(__file__))

    # read distributions from config file
    choices = read_distribution(os.path.join(config_path, config_file))

    # define distribution
    distribution = []

    for i in tablemates:
        distribution.extend(choices[i]['choices'])

    return distribution


def pranzomatic_roll (tablemates, config_file='config.ini'):

    distribution = get_distribution(tablemates, config_file)

    winner = random_restaurant(distribution)

    return winner


def pranzomatic_distribution (tablemates, name_image, config_file='config.ini'):

    distribution = get_distribution(tablemates, config_file)

    import pandas
    import collections
    import matplotlib.pyplot as plt

    data = [random_restaurant(distribution) for i in range(5000)]
    coll = collections.Counter(data)
    # normalize data
    total = sum(coll.values(), 0.0)
    for key in coll:
        coll[key] /= total
    # plot barh
    df = pandas.DataFrame.from_dict(coll, orient='index')
    df.plot(kind='barh', legend=False)
    plt.savefig(name_image, transparent=True, bbox_inches='tight')


def pranzomatic_tablemates (config_file='config.ini'):
    config_path = os.path.dirname(os.path.abspath(__file__))
    cp = ConfigParser.ConfigParser()
    cp.read(os.path.join(config_path, config_file))
    return cp.sections()


def pranzomatic_mailing_list (tablemates, config_file='config.ini'):

   config_path = os.path.dirname(os.path.abspath(__file__))

   choices = read_distribution(os.path.join(config_path, config_file))

   mailing_list = []

   for i in tablemates:
       mailing_list.append(choices[i]['mail'])

   return mailing_list


def pranzomatic_mailing_dict (tablemates, config_file='config.ini'):

   config_path = os.path.dirname(os.path.abspath(__file__))

   choices = read_distribution(os.path.join(config_path, config_file))

   mailing_list = {}

   for i in tablemates:
       mailing_list[i] = choices[i]['mail']

   return mailing_list


def send_mail(body, to_list, subject="And the winner is ...", config_file='social.ini'):

    config_path = os.path.dirname(os.path.abspath(__file__))

    cp = ConfigParser.ConfigParser()
    cp.read(os.path.join(config_path, config_file))

    mail_address  = cp.get('mail', 'mail_address')
    mail_smtp     = cp.get('mail', 'smtp')
    mail_username = cp.get('mail', 'username')
    mail_password = cp.get('mail', 'password')

    # prepare message
    message = """\
From: %s
To: %s
Subject: %s

%s
""" % (mail_address, ", ".join(to_list), subject, body)

    # send mail
    server = smtplib.SMTP(mail_smtp)
    server.starttls()
    server.login(mail_username, mail_password)
    server.sendmail(mail_address, to_list, message)
    server.quit()


def send_tweet(body, config_file='social.ini'):

  try:
    config_path = os.path.dirname(os.path.abspath(__file__))

    cp = ConfigParser.ConfigParser()
    cp.read(os.path.join(config_path, config_file))

    consumer_key    = cp.get('twitter', 'consumer_key')
    consumer_secret = cp.get('twitter', 'consumer_secret')
    access_key      = cp.get('twitter', 'access_key')
    access_secret   = cp.get('twitter', 'access_secret')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    message = "And the winner is ...\n" + body

    # send tweet
    api.update_status(status=message[:140])
  except:
      pass


def ask(default_answer='yes'):
    for i in range(3):
        try:
            return strtobool(raw_input('continue [Y/n] ').lower() or default_answer)
        except ValueError:
            sys.stdout.write('Please respond with \'y\' or \'n\'.\n')
    raise SystemExit('too many wrong answer')


def quote():
    try:
        from myfortune import fortune
        _quote = fortune.get_quote()
        #_quote = subprocess.Popen('fortune', stdout=subprocess.PIPE).communicate()[0]
    except:
        _quote = ''
    return _quote.strip()


