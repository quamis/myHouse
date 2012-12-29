#!/usr/bin/python
import sys, dbus, gobject
import time
import argparse

# TODO: remove this
# ./notify.py -user="rassandra21@gmail.com" -message="te iubesc"

parser = argparse.ArgumentParser(description='Send notifications')
parser.add_argument('-user',        dest='user',     action='store', type=str, default=None,    help='TODO')
parser.add_argument('-message',     dest='message',  action='store', type=str, default=None,    help='TODO')
args = parser.parse_args()


import subprocess
subprocess.Popen(["pidgin","--login"])
time.sleep(10)

bus = dbus.SessionBus()
obj = bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")

account_id = purple.PurpleAccountsGetAllActive()[0]

conversation = purple.PurpleConversationNew(1, account_id, args.user)
im = purple.PurpleConvIm(conversation)
purple.PurpleConvImSend(im, args.message)

time.sleep(10)
purple.PurpleCoreQuit()


