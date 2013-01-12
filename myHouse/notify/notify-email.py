#!/usr/bin/python
import sys
import argparse
import smtplib
import email
import os.path
from email.encoders import encode_base64
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

parser = argparse.ArgumentParser(description='Send notifications')
parser.add_argument('-subject',     dest='subject',  action='store', type=str, default="myHouse results",    help='TODO')
parser.add_argument('-sender',      dest='sender',   action='store', type=str, default=None,    help='TODO')
parser.add_argument('-password',    dest='password', action='store', type=str, default=None,    help='TODO')
parser.add_argument('-to',          dest='to',       action='append',type=str, default=None,    help='TODO')
parser.add_argument('-text',        dest='text',     action='store', type=str, default=None,    help='TODO')
parser.add_argument('-attach',      dest='attach',   action='append',type=str, default=None,    help='TODO')
args = parser.parse_args()

print "Sending email to %s" % (", ".join(args.to))

# @see http://docs.python.org/2/library/email-examples.html#email-examples for a html message example
messageBody = MIMEMultipart()
messageBody['Subject'] = args.subject
messageBody['From'] =   args.sender
messageBody['To'] =     ", ".join(args.to) 

# Record the MIME types of both parts - text/plain and text/html.
#messageBody.attach(email.mime.text.MIMEText(args.message,'html'))
body = MIMEText(args.text, 'plain')
messageBody.attach(body)

if args.attach:
    for file in args.attach:
        attachement = MIMEBase("application", 'octet-stream')
        attachement.set_payload(open(file, "rb").read())
        encode_base64(attachement)
        attachement.add_header('Content-Disposition','attachment', filename=os.path.basename(file))
        messageBody.attach(attachement)

# connect to the SMTP server & send
server = smtplib.SMTP('smtp.gmail.com:587')  
server.starttls()  
server.login(args.sender, args.password)  
result = server.sendmail(args.sender, args.to, messageBody.as_string())  
server.quit()
print "Email sent"
