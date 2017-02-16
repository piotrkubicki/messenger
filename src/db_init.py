from subprocess import call
from app import init_db

call(['touch', 'var/database/messager.db'])
call(['touch', 'var/logs.log'])
call(['mkdir', '-p', 'var/messages'])
call(['mkdir', '-p', 'var/blacklists'])
call(['mkdir', '-p', 'var/tokens'])
init_db()
