#!/usr/bin/python
import sys, dbus, gobject
import time
import argparse

# TODO: remove this
# ./notify.py -user="rassandra21@gmail.com" -message="te iubesc"

"""
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
"""


import smtplib
from email.mime.text import MIMEText
parser = argparse.ArgumentParser(description='Send notifications')
parser.add_argument('-sender',      dest='sender',   action='store', type=str, default=None,    help='TODO')
parser.add_argument('-password',    dest='password', action='store', type=str, default=None,    help='TODO')
parser.add_argument('-to',          dest='to',       action='store', type=str, default=None,    help='TODO')
parser.add_argument('-message',     dest='message',  action='store', type=str, default=None,    help='TODO')
args = parser.parse_args()

print "Sending email to %s" % ( args.to )

# @see http://docs.python.org/2/library/email-examples.html#email-examples for a html message example

messageBody = MIMEText(args.message)
messageBody['Subject'] = 'myHouse script results'
messageBody['From'] = args.sender
messageBody['To'] = args.to 

server = smtplib.SMTP('smtp.gmail.com:587')  
server.starttls()  
server.login(args.sender, args.password)  
server.sendmail(args.sender, args.to, messageBody.as_string())  
server.quit()  
print "Email sent"