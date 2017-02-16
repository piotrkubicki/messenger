class FriendRequest():

  def __init__(self, db):
    self.db = db

  def all(self):
    '''Return all friend requests.'''
    requests = []

    for row in self.db.cursor().execute('SELECT request_id, sender_id, reciever_id, status FROM friend_requests'):
      request = {
        'request_id' : row[0],
        'sender_id' : row[1],
        'reciever_id' : row[2],
        'status' : row[3]
      }

      requests.append(request)

    return requests

  def get_requests_by_reciever(self, reciever_id):
    '''Return all requests send to user.

    Keyword arguments:
    reciever_id -- id for search query
    '''
    requests = []

    for row in self.db.cursor().execute('SELECT request_id, sender_id, reciever_id, status FROM friend_requests WHERE reciever_id = ' + str(reciever_id)):
      request = {
        'request_id' : row[0],
        'sender_id' : row[1],
        'reciever_id' : row[2],
        'status' : row[3]
      }

      requests.append(request)

    return requests

  def get_requests_by_sender(self, sender_id):
    '''Return all requests send by user.

    Keyword arguments:
    sender_id -- id for search query
    '''
    requests = []

    for row in self.db.cursor().execute('SELECT request_id, sender_id, reciever_id, status FROM friend_requests WHERE sender_id = ' + str(sender_id)):
      request = {
        'request_id' : row[0],
        'sender_id' : row[1],
        'reciever_id' : row[2],
        'status' : row[3]
      }

      requests.append(request)

    return requests

  def get_waiting_request(self, reciever_id):
    '''Return friend request that wait for response.

    Keyword arguments:
    reciever_id -- id for search query
    '''
    request = None

    for row in self.db.cursor().execute('SELECT request_id, sender_id, reciever_id, status FROM friend_requests WHERE reciever_id = ' + str(reciever_id) + ' AND status = 0 ORDER BY request_id LIMIT 1'):
      request = {
        'request_id' : row[0],
        'sender_id' : row[1],
        'reciever_id' : row[2],
        'status' : row[3]
      }
    return request

  def get_request_by_id(self, id):
    '''Return request.

    Keyword arguments:
    id -- id for search query
    '''

    for row in self.db.cursor().execute('SELECT request_id, sender_id, reciever_id, status FROM friend_requests WHERE request_id = ' + str(id)):
      request = {
        'request_id' : row[0],
        'sender_id' : row[1],
        'reciever_id' : row[2],
        'status' : row[3]
      }

    return request

  def get_requests_by_sender_and_reciever(self, sender_id, reciever_id):
    '''Return all requests send by user to user

    Keyword arguments:
    sender_id -- id for search query
    reciever_id -- id for search query
    '''
    requests = []

    for row in self.db.cursor().execute('SELECT request_id, sender_id, reciever_id, status FROM friend_requests WHERE sender_id = ' + str(sender_id) + ' AND reciever_id = ' + str(reciever_id)):
      request = {
        'request_id' : row[0],
        'sender_id' : row[1],
        'reciever_id' : row[2],
        'status' : row[3]
      }

      requests.append(request)

    return requests

  def create_friend_request(self, sender_id, reciever_id):
    '''Create new friend request database entry in friend requests table.

    Keyword arguments:
    sender_id -- id of user who send request
    reciever_id -- id of user target
    '''
    friend_requests = self.all()

    if len(friend_requests) > 0:
      last_request = friend_requests[-1]
      last_id = last_request['request_id']
    else:
      last_id = 0

    request_id = int(last_id) + 1

    data = (request_id, sender_id, reciever_id, 0)

    self.db.cursor().execute('INSERT INTO friend_requests VALUES (?, ?, ?, ?)', data)
    self.db.commit()

  def update_status(self, id, new_status):
    '''Update request status.

    Keyword arguments:
    id -- request id
    new_status -- updated status
    '''
    data = (new_status, id)
    self.db.cursor().execute('UPDATE friend_requests SET status = ? WHERE request_id = ?', data)
    self.db.commit()
