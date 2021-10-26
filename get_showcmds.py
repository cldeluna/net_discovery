#!/usr/bin/python -tt
# Project: client_discovery
# Filename: get_showcmds.py
# claudia
# PyCharm

from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@eianow.com)"
__version__ = ": 1.0 $"
__date__ = "4/20/20"
__copyright__ = "Copyright (c) 2018 EIA"
__license__ = "Python"

import argparse
import netmiko
import datetime
import utils
import add_2env
import os
import re
import dotenv
import getpass


def get_creds(debug=True):
    """
    Function to interactively set credentials
    """

    user = input("Username [%s]: " % getpass.getuser())

    if not user:
        user = getpass.getuser()

    print("Password and Enable Password will not be echoed to the screen or saved.")
    if arguments.file_of_devs:
        print(
            f"*** These credentials will be use for all devices in the file {arguments.file_of_devs}***"
        )
    pwd = getpass.getpass("Password: ")

    enable = getpass.getpass("Enable: ")

    return user, pwd, enable


def main():
    """
    Basic Netmiko script showing how to connect to a device and save the output.

    """

    datestamp = datetime.date.today()
    print(f"===== Date is {datestamp} ====")

    # Load Credentials from environment variables
    dotenv.load_dotenv(verbose=False)

    fn = "show_cmds.yml"
    cmd_dict = utils.read_yaml(fn)

    # Set the environment variable for Netmiko to use TextFMS ntc-templates library
    # os.environ["NET_TEXTFSM"] = "./ntc-templates/templates"

    device_list = []
    if arguments.file_of_devs:
        fh = utils.open_file(arguments.file_of_devs)
        devlist = fh.readlines()
        for line in devlist:
            if re.search(r"\w+", line):
                device_list.append(line.strip())
    elif arguments.device:
        device_list.append(arguments.device)
    else:
        print(
            f"ERROR! Please provide the IP or FQDN of a single device using the -d option or a text file of devices using the -f option!"
        )
        exit("No devices provided. Aborting Execution.")

    # SAVING OUTPUT
    utils.sub_dir(arguments.output_subdir)

    if arguments.mfa:
        # User is using MFA
        usr = os.environ["INET_USR"]
        pwd = os.environ["INET_PWD"]
        sec = os.environ["INET_PWD"]
        mfa_code = input("Enter your 2-Factor Access Security Code: ")
        mfa = f"{pwd}{mfa_code.strip()}"
        sec = sec
    elif arguments.credentials:
        uname, passwd, enable = utils.get_creds()
        usr = uname
        mfa = passwd
        sec = enable
    else:
        # User has account without MFA
        usr = os.environ["NET_USR"]
        pwd = os.environ["NET_PWD"]
        sec = os.environ["NET_PWD"]
        mfa = pwd
        sec = pwd

    for dev in device_list:
        devdict = {
            "device_type": arguments.device_type,
            "ip": dev,
            "username": usr,
            "password": mfa,
            "secret": sec,
            "port": arguments.port,
        }

        # RAW Parsing with Python
        print(f"\n===============  Device {dev} ===============")

        # Set the Show Commands to execute by device type or command provided via CLI
        if devdict["device_type"] in ["cisco_ios", "cisco_nxos", "cisco_wlc"]:
            if arguments.show_cmd:
                cmds = []
                cmds.append(arguments.show_cmd)
            elif re.search("ios", devdict["device_type"]):
                cmds = cmd_dict["ios_show_commands"]
            elif re.search("nxos", devdict["device_type"]):
                cmds = cmd_dict["nxos_show_commands"]
            elif re.search("wlc", devdict["device_type"]):
                cmds = cmd_dict["wlc_show_commands"]
            else:
                cmds = cmd_dict["general_show_commands"]
            resp = utils.conn_and_get_output(devdict, cmds, debug=True)

            # Optional Note to distinguish or annotate the show commands
            if arguments.note:
                note_text = utils.replace_space(arguments.note)
                basefn = f"{dev}_{datestamp}_{note_text}.txt"
            else:
                basefn = f"{dev}_{datestamp}.txt"

            output_dir = os.path.join(os.getcwd(), arguments.output_subdir, basefn)
            utils.write_txt(output_dir, resp)

            print(f"\nSaving show command output to {output_dir}\n\n")

        else:
            print(f"\n\n\txxx Skip Device {dev} Type {devdict['device_type']}")


# Standard call to the main() function.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script Description",
        epilog="Usage: ' python get_showcmds.py -d my_switch_hostname.my.domain' ",
    )

    parser.add_argument(
        "-d",
        "--device",
        help="Get show commands from this device (ip or FQDN) and save to file",
        action="store",
        default="",
    )
    parser.add_argument(
        "-t",
        "--device_type",
        help="Device Types include cisco_nxos, cisco_asa, cisco_wlc Default: cisco_ios",
        action="store",
        default="cisco_ios",
    )
    parser.add_argument(
        "-p",
        "--port",
        help="Port for ssh connection. Default: 22",
        action="store",
        default="22",
    )
    parser.add_argument(
        "-o",
        "--output_subdir",
        help="Name of output subdirectory for show command files",
        action="store",
        default="local",
    )
    parser.add_argument(
        "-s", "--show_cmd", help="Execute a single show command", action="store"
    )
    parser.add_argument(
        "-n",
        "--note",
        action="store",
        help="Short note to distinguish show commands. Ex. -pre or -post",
    )
    parser.add_argument(
        "-m",
        "--mfa",
        action="store_true",
        help="Multi Factor Authentication will prompt for 2-Factor code",
        default=False
    )
    parser.add_argument(
        "-c",
        "--credentials",
        action="store_true",
        help="Set Credentials via Command Line interactively",
        default="",
    )
    parser.add_argument(
        "-f",
        "--file_of_devs",
        action="store",
        help="Provide the full path to a text file containing an IP or FQDN on each line (see example_device_file.txt) "
        "to execute show commands on multiple devices with the same credentials.",
        default="",
    )
    arguments = parser.parse_args()
    main()
