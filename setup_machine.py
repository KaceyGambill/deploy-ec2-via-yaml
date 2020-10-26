import os, sys, stat
import subprocess
from re import search

def create_user_ssh_command_array(users):
    ssh_commands = []
    for user in users:
        user_login_name = user.get('login')
        user_pub_key = user.get('ssh_key')
        ssh_commands.append('sudo adduser {}'.format(user_login_name))
        ssh_commands.append('sudo su - {}'.format(user_login_name))
        ssh_commands.append('mkdir .ssh')
        ssh_commands.append('chmod 700 .ssh')
        ssh_commands.append('touch .ssh/authorized_keys')
        ssh_commands.append('chmod 600 .ssh/authorized_keys')
        ssh_commands.append('echo {} >> .ssh/authorized_keys'.format(user_pub_key))
        ssh_commands.append('echo "TEJOITO" >> the_file')
        ssh_commands.append('exit')
    return ssh_commands