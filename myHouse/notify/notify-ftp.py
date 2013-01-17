#!/usr/bin/python
import sys, os
import argparse

from ftplib import FTP

parser = argparse.ArgumentParser(description='Send notifications')
parser.add_argument('-host',        dest='host',     action='store', type=str, default=None,    help='TODO')
parser.add_argument('-username',    dest='username', action='store', type=str, default=None,    help='TODO')
parser.add_argument('-password',    dest='password', action='store', type=str, default=None,    help='TODO')
parser.add_argument('-remotePath',  dest='remotePath',action='store',type=str, default="",    help='TODO')
parser.add_argument('-attach',      dest='attach',   action='append',type=str, default=None,    help='TODO')
args = parser.parse_args()

print "Logging in to %s" % (args.host)


ftp = FTP(args.host, args.username, args.password)

if args.attach:
    for file in args.attach:
        remotePath = "%s/%s" % (args.remotePath, os.path.basename(file))
        print " -> %s" % (remotePath)
        ftp.storbinary("STOR %s" % (remotePath), open(file, 'rb'))

ftp.close()
print "Done"
