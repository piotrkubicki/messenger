import json
import os.path

class Message():

  def __init__(self, location, filename):
    '''Initialise object with filename.

    Keyword arguments:
    location -- file location string
    filename -- file name string
    '''
    extension = '.json'
    self.file = location + filename + extension

    #create file if not exists
    if not os.path.isfile(self.file):
      with open(self.file, 'w') as new_file:
        new_file.write('')

  def all(self):
    '''Return all messages from file.'''
    messages = None

    with open(self.file) as datafile:
      try:
        messages = json.load(datafile)
      except ValueError:
        messages = []

    return messages

  def get_last(self):
    messages = self.all()
    last_message = []

    if len(messages) > 0:
      last_message.append(messages[-1])

    return last_message

  def check_unseen(self):
    '''Takes last message and check read status. Return true if message wasn't seen.'''
    last_message = self.get_last()

    if len(last_message) > 0:
      if last_message[0]['read'] == '1':
        return True

    return False

  def get_last_message_user_id(self):
    '''Return id of the user who send last message.'''
    last_message = self.get_last()

    if len(last_message) > 0:
      return last_message[0]['user_id']

    return None;

  def mark_as_seen(self, sender_id):
    messages = self.all()

    for message in messages:
      if message['user_id'] == sender_id:
        message['read'] = '0'

    with open(self.file, 'w') as datafile:
      json.dump(messages, datafile)

  def create_message(self, user_id, username, datetime, message):
    '''Add new message instance to messages storage.

    Keyword arguments:
    user_id -- id of user who send message
    username -- username of user who send message
    datetime -- current datetime
    message -- string with information
    '''
    messages = self.all()

    if len(messages) > 0:
      last_message = messages[-1]
      last_id = int(last_message['message_id'])
    else:
      last_id = 0

    message_id = last_id + 1

    message = {
      'message_id' : str(message_id),
      'user_id' : user_id,
      'username' : username,
      'datetime' : datetime,
      'message' : message,
      'read' : '1'
    }

    messages.append(message)

    with open(self.file, 'w') as datafile:
      json.dump(messages, datafile)

