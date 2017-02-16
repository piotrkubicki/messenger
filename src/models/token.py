import json
import os.path
import uuid

from datetime import datetime

class Token():

  def __init__(self, location, filename):
    '''Initialise object with filename.

    Keyword arguments:
    location -- file location string
    filename -- filename string
    '''
    extension = '.json'
    self.file = location + filename + extension

    if not os.path.isfile(self.file):
      with open(self.file, 'w') as new_file:
        new_file.write('')

  def all(self):
    '''Return all messages from file.'''
    tokens = None

    with open(self.file) as datafile:
      try:
        tokens = json.load(datafile)
      except ValueError:
        tokens = []

    return tokens

  def generate(self, username):
    '''Generate new login token.'''
    tokens = self.all()

    token = {
      'username' : username,
      'time' : datetime.utcnow().strftime('%d-%b-%Y %H:%M:%S'),
      'token' : uuid.uuid4().hex
    }

    tokens.append(token)

    self.save(tokens)

    return token['token']

  def validate(self, username, user_token, time):
    '''Check if token provided exists in token file and removes expired tokens.'''
    tokens = self.all()
    time_now = datetime.strptime(datetime.utcnow().strftime('%d-%b-%Y %H:%M:%S'), '%d-%b-%Y %H:%M:%S')

    for token in tokens:
      date = datetime.strptime(token['time'], '%d-%b-%Y %H:%M:%S')
      time_diff = time_now - date
      time_result = divmod(time_diff.days * 86400 + time_diff.seconds, 60)

      if int(time_result[0]) > int(time):
        self.__remove__(token)
      else:
        if str(token['token']) == str(user_token) and str(token['username']) == str(username):
          return True

    return False

  def __remove__(self, token_to_remove):
    tokens = self.all()
    new_tokens = []

    for token in tokens:
      if str(token['token']) != str(token_to_remove['token']):
        new_tokens.append(token)

    self.save(new_tokens)

  def remove(self, token_to_remove):
    tokens = self.all()
    new_tokens = []

    for token in tokens:
      if str(token['token']) != str(token_to_remove):
        new_tokens.append(token)

    self.save(new_tokens)


  def update(self, token_to_update):
    tokens = self.all()

    for token in tokens:
     if token['token'] == token_to_update:
      token['time'] = datetime.utcnow().strftime('%d-%b-%Y %H:%M:%S')

    self.save(tokens)

  def save(self, tokens):
    with open(self.file, 'w') as datafile:
      json.dump(tokens, datafile)
