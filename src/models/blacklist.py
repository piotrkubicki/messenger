import json
import os.path

class Blacklist():

  def __init__(self, location, filename):
    '''Initialise object with filename.

    Keyword arguments:
    location -- file location
    filename -- filename to work with
    '''
    extension = '.jison'
    self.file = location + filename + extension

    if not os.path.isfile(self.file):
      with open(self.file, 'w') as new_file:
        new_file.write('')

  def all(self):
    '''Returns all blacklisted users.'''
    users = None

    with open(self.file) as datafile:
      try:
        users = json.load(datafile)
      except ValueError:
        users = []

    return users

  def find_user(self, user_id):
    '''Check if user is blocked.

    Keyword arguments:
    user_id -- is of the user that search is made
    '''
    users = self.all()

    for user in users:
      if str(user['user_id']) == str(user_id):
        return True

    return False

  def add_user(self, user_id):
    '''Add user to the blacklist.

    Keyword arguments:
    blocked_user_id -- id of the user that will be blocked
    '''
    if not self.find_user(user_id):
      users = self.all()

      user = {
        'user_id' : user_id
      }

      users.append(user)

      with open(self.file, 'w') as datafile:
        json.dump(users, datafile)


