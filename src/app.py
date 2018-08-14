import ConfigParser
import logging
import sqlite3
import base64
import bcrypt
import os
import eventlet

from datetime import datetime
from flask import Flask, g, url_for, render_template, session, request, jsonify, redirect, flash
from flask_socketio import SocketIO, join_room, leave_room, emit
from logging.handlers import RotatingFileHandler
from functools import wraps
from os import walk
from models.user import User
from models.room import Room
from models.message import Message
from models.friend_request import FriendRequest
from models.blacklist import Blacklist
from models.token import Token

app = Flask(__name__)
app.config['SECRET_KEY'] = '#~fer?L,97dwDw.:$332dsd45f'
socketio = SocketIO(app)

def init(app):
  config = ConfigParser.ConfigParser()

  try:
    location = os.path.dirname(os.path.abspath(__file__))
    config_location = os.path.join(location, 'etc/defaults.cfg')
    config.read(config_location)

    app.config['DEBUG'] = config.get('config', 'debug')
    app.config['ip_address'] = config.get('config', 'ip_address')
    app.config['port'] = config.get('config', 'port')
    app.config['url'] = config.get('config', 'url')

    app.config['database_location'] = config.get('database', 'database_location')
    app.config['schemas_location'] = config.get('database', 'schemas_location')
    app.config['seeders_location'] = config.get('database', 'seeders_location')
    app.config['messages_location'] = config.get('database', 'messages_location')
    app.config['blacklists_location'] = config.get('database', 'blacklists_location')
    app.config['tokens_location'] = config.get('database', 'tokens_location')

    app.config['log_file'] = config.get('logging', 'name')
    app.config['log_location'] = config.get('logging', 'location')
    app.config['log_level'] = config.get('logging', 'level')
  except:
    print 'Could not read configs from: %s' % config_location

def logs(app):
  location = os.path.dirname(os.path.abspath(__file__))
  log_pathname = os.path.join(*[location, app.config['log_location'], app.config['log_file']])
  file_handler = RotatingFileHandler(log_pathname, maxBytes = 1024 * 1024 * 10, backupCount = 1024)
  file_handler.setLevel(app.config['log_level'])
  formatter = logging.Formatter('%(levelname)s | %(asctime)s | %(module)s | %(funcName)s | %(message)s')
  file_handler.setFormatter(formatter)
  app.logger.setLevel(app.config['log_level'])
  app.logger.addHandler(file_handler)

def get_db():
  db = getattr(g, 'db', None)

  if db is None:
    location = os.path.dirname(os.path.abspath(__file__))
    db = sqlite3.connect(os.path.join(location, app.config['database_location']))
    g.db = db

  return db

@app.teardown_appcontext
def close_db_connection(exception):
  db = getattr(g, 'db', None)

  if db is not None:
    db.close()

def init_db():
  '''Read all files from schemas and seeders directory, create database tables and populate them. Remove messages files'''
  schemas = []
  seeders = []
  message_files = []
  init(app)

  for _, _, filenames in walk(app.config['schemas_location']):
    schemas.extend(filenames)

  for _, _, filenames in walk(app.config['seeders_location']):
    seeders.extend(filenames)

  for _, _, filenames in walk(app.config['messages_location']):
    for file in filenames:
      os.remove(app.config['messages_location'] + file)

  for _, _, filenames in walk(app.config['blacklists_location']):
    for file in filenames:
      os.remove(app.config['blacklists_location'] + file)

  for _, _, filenames in walk(app.config['tokens_location']):
    for file in filenames:
      os.remove(app.config['tokens_location'] + file)

  with app.app_context():
    db = get_db()

    for schema in schemas:
      with app.open_resource(app.config['schemas_location'] + schema, mode = 'r') as f:
        db.cursor().executescript(f.read())

      db.commit()

    for seeder in seeders:
      with app.open_resource(app.config['seeders_location'] + seeder, mode = 'r') as f:
        db.cursor().executescript(f.read())

      db.commit()

def authenticate(username, password):
  db = get_db()

  if username == '':
    return False

  user_pass = User(db).get_user_password(username)

  if user_pass is None:
    return False

  if user_pass == bcrypt.hashpw(password.encode('utf-8'), user_pass):
    session['username'] = username
    session['token'] = Token(app.config['tokens_location'], 'tokens').generate(username)

    return True

  flash(u'Credentials don\'t match any record!', 'error')

  return False

def require_auth(f):
  '''Redirect user if not authorised.'''
  @wraps(f)
  def decorated(*args, **kwargs):

    if 'token' in session and 'username' in session:
      token = session['token']
      username = session['username']
    else:
      return redirect(url_for('login'))

    if not Token(app.config['tokens_location'], 'tokens').validate(username, token, 10):
      response = {
        'response' : render_template('relog_form.html')
      }
      user = User(get_db()).get_user_by_username(username)

      if user is not None:
        socketio.emit('relog', response, room = user['room'])

      return redirect(url_for('login'))

    Token(app.config['tokens_location'], 'tokens').update(token)

    return f(*args, **kwargs)

  return decorated

def redirect_auth(f):
  '''Redirect user if authorised.'''
  @wraps(f)
  def decorated(*args, **kwargs):
    username = ''
    password = ''

    try:
      if session['username']:
        username = str(session['username'])

      if session['password']:
        password = str(session['password'])
    except KeyError:
      pass

    if authenticate(username, password):
      return redirect(url_for('dashboard'))

    return f(*args, **kwargs)

  return decorated

def validate_friend_request(sender_id, reciever_id):
  '''Return false if three request made, unresponded request exists, any request was already accepted or user is blocked.'''
  if sender_id == reciever_id:
    return False

  if Blacklist(app.config['blacklists_location'], reciever_id).find_user(sender_id):
    return False

  all_requests = FriendRequest(get_db()).get_requests_by_sender_and_reciever(sender_id, reciever_id)

  if len(all_requests) >= 3:
    return False

  #add requests send by reciever to sender
  all_requests.extend(FriendRequest(get_db()).get_requests_by_sender_and_reciever(reciever_id, sender_id))

  for request in all_requests:
    if request['status'] == 0:
      return False

  for request in all_requests:
    if request['status'] == 1:
      return False

  return True

def emit_friend_request(sender, friend_room, request_id):
  request_response = {
    'user_id' : sender['user_id'],
    'first_name' : sender['first_name'],
    'last_name' : sender['last_name'],
    'avatar' : sender['avatar'],
    'request_id' : request_id
  }

  socketio.emit('friend request', (render_template('friend_request_confirmation.html', request = request_response), request_id), room = friend_room)

@app.errorhandler(404)
def page_not_found(error):
  return render_template('404_error.html')

@app.route('/')
@require_auth
def dashboard():
  db = get_db()
  user = User(db).get_user_by_username(session['username'])
  friends = User(db).get_user_friends(user['user_id'])
  date_of_birth = user['date_of_birth'].split('/')
  user['date_of_birth'] = {}
  user['date_of_birth']['day'] = date_of_birth[0]
  user['date_of_birth']['month'] = date_of_birth[1]
  user['date_of_birth']['year'] = date_of_birth[2]

  rooms = Room(db).get_user_rooms(user['user_id'])
  unseen_messages = []

  for room in rooms:
    messages = Message(app.config['messages_location'], room['room_name'])
    if messages.check_unseen():
      unseen_messages.append(messages.get_last_message_user_id())

  for friend in friends:
    for um in unseen_messages:
      if um == friend['user_id']:
        friend['unseen_msg'] = True

  return render_template('dashboard.html', user = user, friends = friends)

@app.route('/login', methods=['GET', 'POST'])
@redirect_auth
def login():
  if request.method == 'GET':
    return render_template('login.html')

  if 'username' in request.form:
    username = request.form['username']
  elif 'username' in session:
    username = session['username']
  else:
    username = ''

  if 'password' in request.form:
    password = request.form['password']
  elif 'password' in request.json:
    password = request.json['password']
  else:
    password = ''

  if authenticate(username, password):
    #db = get_db()
    #user = User(db).get_user_by_username(username)
    return redirect(url_for('dashboard'))

  app.logger.info('Failed login attempt. Username: %s, Password: %s at %s' % (username, password, datetime.utcnow()))
  return render_template('login.html')

@app.route('/logout')
def logout():
  Token(app.config['tokens_location'], 'tokens').remove(session['token'])

  session['username'] = ''
  session['token'] = ''

  return redirect(url_for('login'))

@app.route('/users/<id>/profile/update', methods=['POST'])
@require_auth
def profile_update(id):
  db = get_db()
  user = User(db).get_user_by_username(session['username'])
  date_of_birth = '%s/%s/%s' % (request.json['day'], request.json['month'], request.json['year'])
  User(db).update(user['user_id'], request.json['first_name'], request.json['last_name'], request.json['avatar'], date_of_birth)

  response = {
    'message' : 'Profile updated successfully'
  }

  return jsonify(**response)

@app.route('/users/<id>/friends/search/', methods=['POST'])
@require_auth
def friends_search(id):
  db = get_db()
  date_of_birth = '%s/%s/%s' % (request.json['day'], request.json['month'], request.json['year'])
  friends = User(db).search(request.json['first_name'], request.json['last_name'], request.json['username'], date_of_birth)
  user = User(db).get_user_by_username(session['username'])
  user_friends = User(db).get_user_friends(user['user_id'])
  results = []

  for friend in friends:
    is_friend = False

    if friend['username'] == user['username']:
      is_friend = True

    for user_friend in user_friends:
      if friend['username'] == user_friend['username']:
        is_friend = True

    if not is_friend:
      results.append(friend);

  response = {
    'friends' : render_template('search_friends.html', friends = results)
  }

  return jsonify(**response)

@app.route('/signup', methods=['GET', 'POST'])
@redirect_auth
def signup():
  if request.method == 'GET':
    return render_template('signup.html')

  username = request.form['username']

  username_test = User(get_db()).get_user_by_username(username)

  if username_test is not None:
    flash(u'Username already exists!', 'error')
    return render_template('signup.html')

  password = request.form['password']
  password_confirmation = request.form['password-confirmation']
  first_name = request.form['first-name']
  last_name = request.form['last-name']
  date_of_birth = '%s/%s/%s' % (request.form['day'], request.form['month'], request.form['year'])
  avatar_file = request.files['user-photo']
  avatar = base64.b64encode(avatar_file.read())
  type = 'user'

  if username == '' or password == '' or password_confirmation == '' or first_name == '' or last_name == '' or date_of_birth == '' or avatar == '':
    flash(u'All fields are required!', 'error')
    return render_template('signup.html')

  if password == password_confirmation:
    hash_pass = bcrypt.hashpw(password, bcrypt.gensalt())
  else:
    flash(u'Password confirmation not the same as password!', 'error')
    return render_template('signup.html')

  db = get_db()
  User(db).create_user(first_name, last_name, username, hash_pass, avatar, date_of_birth, type)

  return redirect(url_for('login'))

@app.route('/users/<id>/friends/add/', methods=['POST'])
@require_auth
def send_friend_request(id):
  db = get_db()
  user = User(db).get_user_by_username(session['username'])
  friend = User(db).get_user_by_username(request.json['username'])
  friend_request = FriendRequest(db)

  if not validate_friend_request(user['user_id'], friend['user_id']):
    response = {
      'message' : 'Requests limit excedded or person is your friend already!'
    }

    return jsonify(**response)

  friend_request.create_friend_request(user['user_id'], friend['user_id'])
  all_friend_requests = friend_request.get_requests_by_sender_and_reciever(user['user_id'], friend['user_id'])
  current_friend_request = all_friend_requests[-1]

  emit_friend_request(user, friend['room'], current_friend_request['request_id'])

  response = {
    'message' : 'Friend request send'
  }

  return jsonify(**response)

@app.route('/users/<id>/friends/add/response/', methods=['POST'])
@require_auth
def send_friend_request_response(id):
  db = get_db()
  answer = request.json['answer']
  request_id = request.json['request_id']
  friend_request = FriendRequest(db).get_request_by_id(request_id)
  user = User(db)
  current_user = user.get_user_by_username(session['username'])
  friend_id = request.json['user_id']
  friend = user.get_user(friend_id)

  if friend_request is not None:
    if answer == 1:
      FriendRequest(db).update_status(request_id, 1)
      Room(db).create_room(current_user['user_id'], friend_id)
      new_room = Room(db).get_users_room(current_user['user_id'], friend_id)

      response = {
        'message' : 'Response accepted.',
        'answer' : True,
        'request_id' : request_id,
        'room' : new_room['room_name']
      }

      user_button = render_template('friend_button.html', friend = current_user)
      friend_button = render_template('friend_button.html', friend = friend)
      socketio.emit('friend request answer', (response, user_button, current_user['user_id']), room = friend['room'])
      socketio.emit('friend request answer', (response, friend_button, friend_id), room = current_user['room'])
    elif answer == 2:
      FriendRequest(db).update_status(request_id, 2)

      response = {
        'message' : 'Response rejected.',
        'answer' : False,
        'request_id' : request_id
      }

      socketio.emit('friend request answer', response, room = friend['room'])
    elif answer == 3:
      FriendRequest(db).update_status(request_id, 2)
      Blacklist(app.config['blacklists_location'], current_user['user_id']).add_user(friend_id)

      response = {
        'message' : 'User blocked.',
        'answer' : False,
        'request_id' : request_id
      }

      socketio.emit('friend request answer', response, room = friend['room'])
  else:
    response = {
      'error' : 'something goes wrong'
    }

  #check if user have more unresponded requests
  awaiting_friend_request = FriendRequest(db).get_waiting_request(current_user['user_id'])
  if awaiting_friend_request is not None:
    sender = User(db).get_user(awaiting_friend_request['sender_id'])
    emit_friend_request(sender, current_user['room'], awaiting_friend_request['request_id'])


  return jsonify(**response)

@app.route('/users/<user_id>/friends/<friend_id>/messages/', methods=['POST'])
@require_auth
def get_messages(user_id, friend_id):
  db = get_db()
  user = User(db).get_user_by_username(session['username'])
  friend = User(db).get_user(friend_id)
  users_room = Room(db).get_users_room(user['user_id'], friend['user_id'])
  messages = []

  if users_room is not None:
    messages = Message(app.config['messages_location'], users_room['room_name']).all()

  response = {
    'messages' : render_template('friend_messages.html', messages = messages, user_id = user['user_id'])
  }

  return jsonify(**response)

@socketio.on('connect')
@require_auth
def connect():
  db = get_db()
  user = User(db).get_user_by_username(session['username'])
  user_rooms = Room(db).get_user_rooms(user['user_id'])

  join_room(user['room'])

  for room in user_rooms:
    join_room(room['room_name'])
    response = {
      'user_id' : user['user_id'],
      'emit' : True
    }

    if room['first_user_id'] == user['user_id']:
      friend = User(db).get_user(room['second_user_id'])
    else:
      friend = User(db).get_user(room['first_user_id'])

    emit('friend connect', response, room = friend['room'])

  awaiting_friend_request = FriendRequest(db).get_waiting_request(user['user_id'])

  if awaiting_friend_request is not None:
    sender = User(db).get_user(awaiting_friend_request['sender_id'])
    emit_friend_request(sender, user['room'], awaiting_friend_request['request_id'])

@socketio.on('disconnect')
@require_auth
def disconnect():
  db = get_db()
  user = User(db).get_user_by_username(session['username'])
  user_rooms = Room(db).get_user_rooms(user['user_id'])

  for room in user_rooms:
    response = {
      'user_id' : user['user_id'],
    }

    if room['first_user_id'] == user['user_id']:
      friend = User(db).get_user(room['second_user_id'])
    else:
      friend = User(db).get_user(room['first_user_id'])

    leave_room(room['room_name'])
    emit('friend disconnect', response, room = friend['room'], include_self = False)

@socketio.on('join private room')
@require_auth
def join_private_room(data):
  db = get_db()

  friend_id = data
  user = User(db).get_user_by_username(session['username'])
  friend = User(db).get_user(friend_id)

  private_room = Room(db).get_users_room(friend_id, user['user_id'])
  join_room(private_room['room_name'])

  response = {
    'user_id' : user['user_id'],
    'emit' : False,
    'room_name' : private_room['room_name']
  }

  emit('friend connect', response, room = friend['room'])

@socketio.on('private message')
@require_auth
def private_message(data):
  db = get_db()
  sender = User(db).get_user_by_username(session['username'])

  if 'user_id' in data:
    reciever = User(db).get_user(data['user_id'])
    users_room = Room(db).get_users_room(reciever['user_id'], sender['user_id'])

    if users_room is not None:
      Message(app.config['messages_location'], users_room['room_name']).create_message(sender['user_id'], sender['username'], str(datetime.utcnow().strftime('%d/%b/%Y/ %H:%M:%S')), data['msg'])
      last_message = Message(app.config['messages_location'], users_room['room_name']).get_last()

      response = {
        'sender_id' : sender['user_id'],
        'reciever_id' : reciever['user_id'],
        'message' : render_template('friend_messages.html', messages = last_message, user_id = sender['user_id'])
      }

      emit('private message', response, room = users_room['room_name'])
    else:
      response = {
        'message' : 'Cannot send message to this user!'
      }

      emit('app error', response, room = sender['room'])
  else:
    response = {
      'message' : 'Friend not selected!'
    }
    emit('app error', response, room = sender['room'])

@socketio.on('message seen')
@require_auth
def message_seen(data):
  db = get_db()
  user = User(db).get_user_by_username(session['username'])
  room = Room(db).get_users_room(user['user_id'], data)
  Message(app.config['messages_location'], room['room_name']).mark_as_seen(data)

@socketio.on('connected friend response')
@require_auth
def connected_friend_response(data):
  db = get_db()
  user = User(db).get_user_by_username(session['username'])

  room = Room(db).get_users_room(user['user_id'], data)

  response = {
    'user_id' : user['user_id'],
    'emit' : False
  }

  if room is not None:
    emit('friend connect', response, room = room['room_name'])

if __name__ == '__main__':
  init(app)
  logs(app)
  DEBUG=True
  #socketio.run(app)
  eventlet.wsgi.server(eventlet.listen((app.config['ip_address'], int(app.config['port']))), app)
