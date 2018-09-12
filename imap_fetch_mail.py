"""
@Author: drk
This code gets  mails from mail-server using IMAP4 Protocol
This code uses html2text to display html in command line

More Info from:
https://www.youtube.com/watch?v=bXRYJEKjqIM
https://tools.ietf.org/html/rfc3501#section-6.4.5
https://www.skytale.net/blog/archives/23-Manual-IMAP.html

Attachments use a base64 encoding scheme
"""
import imaplib
import email
from subprocess import Popen, PIPE
import os
import re

SHELL = "/bin/bash"     # os.getenv("SHELL", "/bin/bash")     # Get the terminal from Environment
SHOW_HTML_COMMAND = "html2text -ascii -style compact -width `tput cols`"   # Command to show html doc (input: stdin )
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "*******@gmail.com")    # get email username
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "*******")    # get password
ATTACHMENTS_DIR = os.getenv("ATTACHMENTS_DIR", "./Attachments/")    # get attachments directory
EMAIL_HEADERS = ["From", "To", "Cc", "Bcc", "Date", "Subject"]
IMAP_URL = os.getenv('IMAP_URL', 'imap.gmail.com')


# Connect and Authenticate to given imap server using IMAP4_SSL
def imap_auth(imap_url, username, password):
    mail = imaplib.IMAP4_SSL(imap_url)               # connect to imap server
    mail.login(user=username, password=password)     # authenticate
    return mail


# Get Mail UIDs meeting the SEARCH criteria from Selected Mail Box
# Returns the UIDs (Unique ID) of the mails
# In Latest to Oldest Order ?
# Search Criteria
# FROM "<mailaddress>" 	Mail from that sender 	FROM "user@example.org"
# TO "<mailaddress>" 	Mail to that recipient 	TO "user@example.org"
# SINCE <date> 	Mail received after this date 	SINCE 1-Nov-2009
# BEFORE <date> 	Mail received before this date 	BEFORE 1-Nov-2009
# DELETED 	Mails marked as deleted 	DELETED
# SUBJECT <string> 	Mails containing string in the subject 	SUBJECT "Proposal"
# BODY <string> 	Mails containing string in the body 	BODY "Hello Greg"
# NOT <key> 	Mails which do not match the key 	NOT FROM "user@example.org"
# OR <key1> <key2> 	Mails which match either of key1 or key2 	OR FROM "user@example.org" FROM "user2@example.org
# UNSEEN    Messages that do not have the \Seen flag set.
# TEXT <string> Messages that contain the specified string in the header or body of the message.
# UID <sequence set>     Messages with unique identifiers corresponding to the specified unique identifier set.
# NOT <search-key> Messages that do not match the specified search key.
def get_mails(mail, mail_box="INBOX", search="UNSEEN"):
    mail.select(mail_box)
    result, data = mail.uid("search", None, search)
    return data[0].split()[::-1]    # Latest to first


# Fetch a data items from mail identified by UID
# some sample data items
# BODY[TEXT] 	Just the mail body, without the headers
# BODY[HEADER] 	The mail headers
# BODY[HEADER.FIELDS (<list>)] 	Just the header fields indicated in list
# BODY[] 	The entire mail text, header and body
# BODY.PEEK 	Works as BODY does, but does not mark the mail as seen
# FLAGS 	Flags set for the message
# UID 	The UID of the message
def fetch_mail(mail, uid, data_items="(BODY.PEEK[])"):
    result, data = mail.uid("fetch", uid, data_items)
    message = email.message_from_bytes(data[0][1])
    return message


# input is the part of multipart whose Content-Type is 'text/html'
# returns string representation of html formatted for command line
def get_html_as_text(byte_payload):
    with Popen([SHELL, "-c", SHOW_HTML_COMMAND], stdin=PIPE, stdout=PIPE) as pipe:  # Both in, out via pipe
        stdout, stderr = pipe.communicate(byte_payload)    # decode the part and send it to html2text
        # print(stdout.decode(errors='ignore'))   # display to standard output ignore errors if any
        return stdout.decode(errors='ignore')   # return the decoded html data


nameless_files = {}     # this contains the number of nameless file attachments in given message UID


# write the byte payload to file at ATTACHMENTS_DIR/uid/filename
def write_to_file(uid, filename, byte_payload):
    if not filename:
        filename = "_nameless_" + str(nameless_files.get(uid, 1))
        nameless_files[uid] = nameless_files.get(uid, 1) + 1
    path_to_file = os.path.join(ATTACHMENTS_DIR, uid.decode('utf-8'), filename)     # construct the path
    os.makedirs(os.path.dirname(path_to_file), exist_ok=True)   # make the directory if already not existing
    with open(path_to_file, 'wb') as f:     # open in write bytes mode
        f.write(byte_payload)   # write to file
    return path_to_file     # Return the path to file


# walks the multi-part message and gets the contents from each of the part
# if attachment then stores it in filesystem and returns the path
# if html then formats it and returns the string
# otherwise returns as such
def message_contents(message, uid):
    contents = []
    for part in message.walk():
        if part.is_multipart():     # if a multipart continue the walk
            continue    # continue the walk
        elif part.get_content_disposition():    # if an attachment
            contents.append("\033[31;1mFile-Attachment: \033[033;1m{}\033[37m".
                            format(write_to_file(uid, part.get_filename(),
                                                 part.get_payload(decode=True))))
            continue
        elif part.get_content_type() == 'text/html':    # if HTML document convert to formatted string
            contents.append(get_html_as_text(part.get_payload(decode=True)))
        else:   # Otherwise simply show the decoded string
            contents.append(part.get_payload(decode=True).decode('utf-8'))
    return contents


# get the desired message headers as key value pairs from list of expected headers from message
def message_header(message, desired_headers):
    obtained_headers = {header: message.get(header) for header in desired_headers if header in message.keys()}
    return obtained_headers


# Show a message
# Note: This also saves attachments to files and shows the filename(s)
def display_message(headers, contents):
    def trim(string):
        output = re.sub("(\n){2,}", "\n\n", re.sub("\r", '', string))
        output = re.sub("(?<=[^\n])\n{2,}(?=[^\n]+\n\n)", "\n", output)
        return output.strip('\n')

    print("\033[044m\n", trim("\n".join(["\033[4D{}: {}".format(h, v) for h, v in headers.items()])), "\033[040m")
    print("\n", trim("\n".join(contents)), "\n\033[0m")


# Search for mails based on search string and then fetch desired data items
# from chosen mailbox
def search_for_mails(mail, search_string, data_items, mail_box="INBOX", limit=5):
    all_mails = get_mails(mail=mail, mail_box=mail_box, search=search_string)
    mails = []
    for uid in all_mails[:limit]:
        message = fetch_mail(mail=mail, uid=uid, data_items=data_items)
        headers = message_header(message=message, desired_headers=EMAIL_HEADERS)
        contents = message_contents(message=message, uid=uid)
        mails.append((headers, contents))
    return mails


# Connect to mail box with given authentication details
with imap_auth(IMAP_URL, EMAIL_USERNAME, EMAIL_PASSWORD) as MAIL:
    SEARCH_STRING = "(SINCE 12-Sep-2018)"
    DATA_ITEMS = "(BODY.PEEK[])"
    MAIL_BOX = "INBOX"
    mails = search_for_mails(MAIL, SEARCH_STRING, DATA_ITEMS, MAIL_BOX)
    for headers, contents in mails:
        display_message(headers=headers, contents=contents)
