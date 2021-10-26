#!/usr/bin/python -tt
# Project: cat_netmiko
# Filename: utils
# claudia
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@eianow.com)"
__version__ = ": 1.0 $"
__date__ = "9/27/20"
__copyright__ = "Copyright (c) 2018 Claudia"
__license__ = "Python"

import argparse
import yaml
import netmiko
import json
import os
import re
import dotenv
import getpass
import add_2env


def replace_space(text, debug=False):
    newtext = re.sub('\s+', '_', text)
    if debug:
        print(f"Original Text: {text}\nReturning Text: {newtext.strip()}")
    return newtext.strip()


def load_env_from_dotenv_file(path):
    # Load the key/value pairs in the .env file as environment variables
    if os.path.isfile(path):
        dotenv.load_dotenv(path)
    else:
        print(f"ERROR! File {path} NOT FOUND! Aborting program execution...")
        exit()


def read_yaml(filename):
    with open(filename) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data


def read_json(filename, debug=False):
    with open(filename) as f:
        data = json.load(f)
    if debug:
        print(f"\n...in the read_json function in utils.py")
        print(data)
        print(f"returning data of type {type(data)} with {len(data)} elements\n")
    return data


def save_json(filename, data, debug=False):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    if debug:
        print(f"\n...in the read_json function in utils.py")
        print(f"saved data to {filename}")


def write_txt(filename, data):
    with open(filename, "w") as f:
        f.write(data)
    return f


def sub_dir(output_subdir, debug=False):
    # Create target Directory if does not exist
    if not os.path.exists(output_subdir):
        os.mkdir(output_subdir)
        print("Directory ", output_subdir, " Created ")
    else:
        if debug:
            print("Directory ", output_subdir, " Already Exists")


def conn_and_get_output(dev_dict, cmd_list, debug=False):

    response = ""
    try:
        net_connect = netmiko.ConnectHandler(**dev_dict)
    except (netmiko.ssh_exception.NetmikoTimeoutException, netmiko.ssh_exception.NetMikoAuthenticationException):
        print(f"Cannot connect to device {dev_dict['ip']}.")

    for cmd in cmd_list:
        if debug:
            print(f"--- Show Command: {cmd}")
        try:
            output = net_connect.send_command(cmd.strip())
            response += f"\n!--- {cmd} \n{output}"
        except Exception as e:
            print(f"Cannot execute command {cmd} on device {dev_dict['ip']}.")
            # continue

    return response


def load_environment(debug=False):
    # Load Credentials from environment variables
    dotenv.load_dotenv(verbose=True)

    usr_env = add_2env.check_env("NET_USR")
    pwd_env = add_2env.check_env("NET_PWD")

    if debug:
        print(usr_env)
        print(pwd_env)

    if not usr_env['VALID'] and not pwd_env['VALID']:
        add_2env.set_env()
        # Call the set_env function with a description indicating we are setting a password and set the
        # sensitive option to true so that the password can be typed in securely without echo to the screen
        add_2env.set_env(desc="Password", sensitive=True)


def open_file(filename, mode="r", encoding="utf-8", debug=False):

    """

    General Utility to safely open a file.

    encoding="utf-8"

    :param filename:  file to open
    :param mode: mode in which to open file, defaults to read
    :return:  file handle

    """

    if debug: print(f"in open_file function in cat_config_utils module with filename {filename} and mode as {mode}")

    file_handle = ''
    # Mode = r | w | a | r+
    try:
        file_handle = open(filename, mode, encoding=encoding, errors='ignore')

    except IOError:
        print("IOError" + str(IOError))
        print(f"open_file() function could not open file with mode {mode} in given path {path}"
              f"\nPlease make sure all result files are closed!")

    return file_handle


def get_creds(debug=True):
    """
    Function to interactively set credentials
    """

    user = input("Username [%s]: " % getpass.getuser())

    if not user:
        user = getpass.getuser()

    print("Password and Enable Password will not be echoed to the screen or saved.")

    pwd = getpass.getpass("Password: ")

    enable = getpass.getpass("Enable: ")

    return user, pwd, enable


def create_devobj_from_json_list(dev):
    """
        dev = {
        'device_type': 'cisco_nxos',
        'ip' : 'sbx-nxos-mgmt.cisco.com',
        'username' : user,
        'password' : pwd,
        'secret' : sec,
        'port' : 8181
    }
    """
    dotenv.load_dotenv()
    dev_obj = {}
    # print(os.environ)
    usr = os.environ['NET_USR']
    pwd = os.environ['NET_PWD']

    core_dev = r'(ar|as|ds|cs){1}\d\d'
    dev_obj.update({'ip': dev.strip()})
    dev_obj.update({'username': usr})
    dev_obj.update({'password': pwd})
    dev_obj.update({'secret': pwd})
    dev_obj.update({'port': 22})
    if re.search(core_dev, dev, re.IGNORECASE):
        dev_obj.update({'device_type': 'cisco_ios'})
    elif re.search(r'-srv\d\d', dev, re.IGNORECASE):
        dev_obj.update({'device_type': 'cisco_nxos'})
    elif re.search(r'-sp\d\d', dev, re.IGNORECASE):
        dev_obj.update({'device_type': 'silverpeak'})
    elif re.search(r'-wlc\d\d', dev, re.IGNORECASE):
        dev_obj.update({'device_type': 'cisco_wlc'})
    elif re.search('10.1.10.109', dev, re.IGNORECASE):
        dev_obj.update({'device_type': 'cisco_wlc'})
        dev_obj.update({'username': 'adminro'})
        dev_obj.update({'password': 'Readonly1'})
        dev_obj.update({'secret': 'Readonly1'})
        # dev_obj.update({'username': 'admin'})
        # dev_obj.update({'password': 'A123m!'})
        # dev_obj.update({'secret': 'A123m!'})
    elif re.search('10.1.10.', dev, re.IGNORECASE) or re.search('1.1.1.', dev, re.IGNORECASE):
        dev_obj.update({'device_type': 'cisco_ios'})
    elif re.search('10.', dev, re.IGNORECASE):
        dev_obj.update({'device_type': 'cisco_ios'})
    else:
        dev_obj.update({'device_type': 'unknown'})

    return dev_obj


# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script Description",
                                     epilog="Usage: ' python utils' ")
    arguments = parser.parse_args()
    main()
