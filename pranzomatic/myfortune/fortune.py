#!/bin/usr/python 
import os
import re
import numpy as np

def random_num(_max):
    return np.random.random_integers(0, _max)

def get_quote():

  quote = ''
  try:
    files = ['fortunes', 'literature', 'riddles']

    files = [ os.path.join( os.path.abspath(os.path.dirname(__file__)), f ) for f in files ]

    quotes = []
    
    for f in files:
        with open(f, 'r') as f:
            dat = f.read()
            quotes.extend( re.findall('(.*?)(?:\n%\n)', dat, re.S) )
    quote = quotes[random_num(len(quotes))]

  except:
      pass

  return quote
  
if __name__ == '__main__':
    print( get_quote() )
