class Room():

  def __init__(self, db):
    '''Initialise object with database connection.

    Keyword arguments:
    db -- database connection
    '''
    self.db = db

  def all(self):
    '''Return all rooms.'''
    rooms = []

    for row in self.db.cursor().execute('SELECT room_id, first_user_id, second_user_id, room_name FROM rooms'):
      room = {
        'room_id' : row[0],
        'first_user_id' : row[1],
        'second_user_id' : row[2],
        'room_name' : row[3]
      }

      rooms.append(room)

    return rooms

  def get_user_rooms(self, id):
    '''Return all rooms for giver user.'''
    rooms = []

    for row in self.db.cursor().execute('SELECT room_id, first_user_id, second_user_id, room_name FROM rooms WHERE first_user_id = ' + str(id) + ' OR second_user_id = ' + str(id)):
      room = {
        'room_id' : row[0],
        'first_user_id' : row[1],
        'second_user_id' : row[2],
        'room_name' : row[3]
      }

      rooms.append(room)

    return rooms

  def get_users_room(self, first_user, second_user):
    '''Return room for given pair of users.

    Keyword arguments:
    first_user -- id of first room owner
    second_user -- id of second room owner
    '''
    room = None

    for row in self.db.cursor().execute('SELECT room_name FROM rooms WHERE first_user_id = ' + str(first_user) + ' AND second_user_id = ' + str(second_user)+ ' OR first_user_id = ' + str(second_user) + ' AND second_user_id = ' + str(first_user)):
      room = {
        'room_name' : row[0]
      }

    return room

  def create_room(self, first_user, second_user):
    '''Create new room for given pair of users.

    Keyword arguments:
    first_user -- id of first room owner
    second_user -- id of second room owner
    '''
    rooms = self.all()

    if len(rooms) > 0:
      last_room = rooms[-1]
      last_id = last_room['room_id']
      last_name = last_room['room_name']
    else:
      last_id = 0
      last_name = 0

    room_id = int(last_id) + 1
    room_name = int(last_name) + 1

    data = (str(room_id), str(first_user), str(second_user), str(room_name))

    self.db.cursor().execute('INSERT INTO rooms VALUES (?, ?, ?, ?)', data)
    self.db.commit()
