class User():

  def __init__(self, db):
    self.db = db

  def get_user(self, id):
    '''Return single user entry with given id from users table.

    Keyword arguments:
    id -- user id to search for
    '''
    user = None

    for row in self.db.cursor().execute('SELECT user_id, first_name, last_name, username, avatar, date_of_birth, type, room FROM users WHERE user_id = ' + str(id)):
      user = {
        'user_id' : row[0],
        'first_name' : row[1],
        'last_name' : row[2],
        'username' : row[3],
        'avatar' : row[4],
        'date_of_birth' : row[5],
        'type' : row[6],
        'room' : row[7]
      }

    return user

  def get_user_password(self, username):
    password = None

    for row in self.db.cursor().execute('SELECT password FROM users WHERE username = "' + username + '"'):
      password = row[0]

    return password

  def get_user_by_username(self, username):
    '''Return single user data with given username from users table.

    Keyword arguments:
    username -- username to search for
    '''
    user = None
    for row in self.db.cursor().execute('SELECT user_id, first_name, last_name, username, avatar, date_of_birth, type, room FROM users WHERE username = "' + username + '"'):
      user = {
        'user_id' : row[0],
        'first_name' : row[1],
        'last_name' : row[2],
        'username' : row[3],
        'avatar' : row[4],
        'date_of_birth' : row[5],
        'type' : row[6],
        'room' : row[7]
      }

    return user

  def all(self):
    '''Return all users entries from users table.'''
    users = []

    for row in self.db.cursor().execute('SELECT user_id, first_name, last_name, username, avatar, date_of_birth, type, room FROM users'):
      user = {
        'user_id' : row[0],
        'first_name' : row[1],
        'last_name' : row[2],
        'username' : row[3],
        'avatar' : row[4],
        'date_of_birth' : row[5],
        'type' : row[6],
        'room' : row[7]
      }

      users.append(user)

    return users

  def get_user_friends(self, id):
    rooms = Room(self.db).get_user_rooms(id)
    friends = []

    for room in rooms:
      if id == room['first_user_id']:
        friend_id = room['second_user_id']
      else:
        friend_id = room['first_user_id']

      for row in self.db.cursor().execute('SELECT user_id, first_name, last_name, username, avatar FROM users WHERE user_id = ' + friend_id):
        friend = {
          'user_id' : row[0],
          'first_name' : row[1],
          'last_name' : row[2],
          'username' : row[3],
          'avatar' : row[4]
        }

        friends.append(friend)

    return friends

  def create_user(self, first_name, last_name, username, password, avatar, date_of_birth, type):
    '''Add user entry to users table.'''
    users = self.all();

    if len(users) > 0:
      last_user = users[-1]
      last_id = last_user['user_id']
    else:
      last_id = 0

    user_id = int(last_id) + 1

    room = username

    data = (str(user_id), first_name, last_name, username, password, avatar, date_of_birth, type, room)

    self.db.cursor().execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
    self.db.commit()


  def update(self, user_id, first_name, last_name, avatar, date_of_birth):
    '''Update user data.

    Keyword arguments:
    user_id -- id of user who will be updated
    first_name -- string
    last_name -- string
    avatar -- base64 string
    date_of_birth -- string
    '''
    user = self.get_user(str(user_id))

    if user is not None:
      if first_name is not '':
        user['first_name'] = first_name
      if last_name is not '':
        user['last_name'] = last_name
      if avatar is not '':
        user['avatar'] = avatar
      if date_of_birth is not '':
        user['date_of_birth'] = date_of_birth

      data = (user['first_name'], user['last_name'], user['avatar'], user['date_of_birth'], str(user_id))

      self.db.cursor().execute('UPDATE users SET first_name = ?, last_name = ?, avatar = ?, date_of_birth = ? WHERE user_id = ?', data)
      self.db.commit()


  def search(self, first_name, last_name, username, date_of_birth):
    '''Return all users that match given criteria.

    Keyword arguments:
    first_name -- string
    last_name -- string
    username -- string
    date_of_birth -- string
    '''
    friends = []

    query = 'SELECT first_name, last_name, username, avatar FROM users WHERE'

    query_params = []

    if first_name != '':
      query_params.append(' first_name LIKE "%' + first_name + '%"')

    if last_name != '':
      query_params.append(' last_name LIKE "%' + last_name + '%"')

    if username != '':
      query_params.append(' username LIKE "%' + username + '%"')

    if date_of_birth != '//':
      query_params.append(' date_of_birth LIKE "%' + date_of_birth + '%"')

    for index, param in enumerate(query_params):
      if index > 0:
        query += ' AND'

      query += param

    for row in self.db.cursor().execute(query):
      friend = {
        'first_name' : row[0],
        'last_name' : row[1],
        'username' : row[2],
        'avatar' : row[3]
      }

      friends.append(friend)

    return friends

from room import Room
