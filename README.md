# Messenger
#### This application require internet connection to run
#### Vagrant installation on Linux
> Require to have vagrant installed https://www.vagrantup.com/
1. run virtual machine by entering `vagrant up` command from inside messenger directory
2. connect with the virtual machine by using `vagrant ssh` command from messenger directory
3. enter `cd /vagrant` command to change directory
4. enter `sudo apt-get update && sudo apt-get install -y python-pip python-dev` command
5. enter `sudo pip install -r requirements.txt` to install other required python packages
6. enter `cd src/` command to go into  /messenger/src/ directory
7. run initialisation script `sh init.sh` to create required files and directories, create and populate database
8. run application `python app.py`
9. application should be available here [messenger](http://localhost:5000)
10. you can create new users or try the testing ones logins range from 'tester' up to 'tester4' passwords: 'password'
