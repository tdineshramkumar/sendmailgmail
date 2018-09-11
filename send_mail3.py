"""
Author: T Dinesh Ram Kumar
This is used to send email
TO, CC, BCC, SUBJECT, ATTACHMENTS are specified as opt parameters
BODY is part of start input
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from getopt import getopt, GetoptError
from os.path import basename
import os
import sys


SERVER_ADDRESS = 'smtp.gmail.com'
SERVER_PORT = 465
email_username = from_address = os.getenv("EMAIL_USERNAME", "*****@gmail.com")      # ENTER USERNAME HERE
email_password = os.getenv("EMAIL_PASSWORD", "*********")                           # ENTER PASSWORD HERE

SHORT_OPTIONS = "hs:A:t:c:b:pB"  # Help, Subject, Attachments, To, CC, BCC, Print
LONG_OPTIONS = ["help", "subject=", "attach=", "to=", "cc=", "bcc=", "print", "body"]


def usage():
    """
    This prints the usage string
    """
    print("Usage: {} [OPTION...]".format(basename(sys.argv[0])))
    print("--subject, -s SUBJECT\n\t\tsend a mail with given subject")
    print("--to, -t TO_ADDRESS\n\t\tsend a mail to given recipients")
    print("--cc, -c CC_ADDRESS\n\t\tsend a mail with given cc recipients")
    print("--bcc, -b BCC_ADDRESS\n\t\tsend a mail with given bcc recipients")
    print("--attach, -A FILE\n\t\tAttach a FILE")
    print("--print, -p\n\t\tTo print the mail")
    print("--help, -h\n\t\tGive the usage")
    print("--body, -B\n\t\tbody is given in the command line")
    print("\n\t\telse body is taken from STDIN.")
    print("FROM_ADDRESS is configured in the code or taken from environment")


try:
    opts, argv = getopt(args=sys.argv[1:], shortopts=SHORT_OPTIONS, longopts=LONG_OPTIONS)
except GetoptError as error:
    print(error)
    usage()
    sys.exit(-1)

print_mail = False
subject, body = "E-Mail Command Line Client", ""
command_line_body = False
to_addresses, cc_addresses, bcc_addresses = [], [], [from_address]
attachments = []
for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit(0)
    if o in ("--print", "-p"):
        print_mail = True
    if o in ("-s", "--subject"):
        subject = a
    if o in ("-t", "--to"):
        to_addresses.append(a)
    if o in ("-c", "--cc"):
        cc_addresses.append(a)
    if o in ("-b", "--bcc"):
        bcc_addresses.append(a)
    if o in ("-A", "--attach"):
        attachments.append(a)
    if o in ("--body", "-B"):
        command_line_body = True

"""
This is for the Message
"""
msg = MIMEMultipart()
msg['From'] = from_address  # specify from address
msg['To'] = ", ".join(to_addresses)  # specify to addresses
msg['Cc'] = ", ".join(cc_addresses)  # specify cc addresses
msg['Bcc'] = ", ".join(bcc_addresses)  # specify bcc addresses
msg['Subject'] = subject  # specify subject
if command_line_body:
    body = " ".join(argv)
    msg.attach(MIMEText(body, 'plain'))  # Attach the body read from argv as plain text
else:
    print("Body (^D):")
    msg.attach(MIMEText(sys.stdin.read(), 'plain'))  # Attach the body read from stdin as plain text

"""
This is for file Attachments
"""
for filename in attachments:  # Specify attachment filename
    with open(filename, "rb") as attachment:
        attachment = open(filename, "rb")  # Read the file
        part = MIMEBase('application', 'octet-stream')  # ?
        part.set_payload(attachment.read())  # Set the payload
        encoders.encode_base64(part)  # Set the encoding ?
        part.add_header('Content-Disposition',  # Set the header ?
                        'attachment; filename= ' + basename(filename))
        msg.attach(part)  # Attach the attachments to the message

text = msg.as_string()  # convert message to string
if print_mail:
    print("Sent Mail: \n" + text)

server = smtplib.SMTP_SSL(SERVER_ADDRESS, SERVER_PORT)  # Connect to server
server.login(email_username, email_password)  # Authenticate
send_addresses = to_addresses + cc_addresses + bcc_addresses
server.sendmail(email_username, send_addresses, text)  # Send Mail
server.quit()  # Close connection
