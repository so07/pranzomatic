#!/usr/bin/python
import mechanize
import requests
import datetime
import sys
import time

weekday = datetime.datetime.today().weekday()

if weekday == 5 or weekday == 6:
    sys.exit()

s = requests.Session()

auth = {'@password' : 'porchettoni!'}

r = s.post('http://pranzomatic.pythonanywhere.com/call', data=auth)

time.sleep(3600)

br = mechanize.Browser()
response = br.open('http://pranzomatic.pythonanywhere.com/roll');

br.select_form(name='roll_form')
br['@password'] = 'porchettoni!'

r = br.submit(name='@roll')
