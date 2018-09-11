"""
Tutorials from
1. https://www.youtube.com/watch?v=bXRYJEKjqIM
2. https://stackoverflow.com/questions/8856117/how-to-send-email-to-multiple-recipients-using-python-smtplib
3. https://stackoverflow.com/questions/38134714/starttls-extension-not-supported-by-server-getting-this-error-when-trying-to-s
4. https://stackoverflow.com/questions/26582811/gmail-python-multiple-attachments
"""

import smtplib
from getpass import getpass 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Utility function to get list of inputs
def get_input_list(message=''):
    input_list = []
    while True:
        value = input(message)
        if value == '':
            return input_list
        input_list.append(value)


SERVER_ADDRESS = 'smtp.gmail.com'
SERVER_PORT = 465
email_username = from_address = input("Username: ") 
email_password = getpass("Password: ")
to_addresses = get_input_list('To:')
if not to_addresses:    # if no to address specified 
    to_addresses = [from_address]   # use the default address
cc_addresses = get_input_list('Cc:')
bcc_addresses = get_input_list('Bcc:')
subject = input("Subject: ")
print("Body:")
body = '\n'.join(get_input_list())
attachments = get_input_list('Attachment:')

"""
This is for the Message
"""
msg = MIMEMultipart()
msg['From'] = from_address              # specify from address
msg['To'] = ", ".join(to_addresses)     # specify to addresses
msg['Cc'] = ", ".join(cc_addresses)     # specify cc addresses
msg['Bcc'] = ", ".join(bcc_addresses)   # specify bcc addresses
msg['Subject'] = subject                # specify subject
msg.attach(MIMEText(body, 'plain'))     # Attach the body as plain text


"""
This is for file Attachments
"""
for filename in attachments:    # Specify attachment filename
    with open(filename, "rb") as attachment:
        attachment = open(filename, "rb")       # Read the file
        part = MIMEBase('application', 'octet-stream')  # ?
        part.set_payload(attachment.read())     # Set the payload
        encoders.encode_base64(part)            # Set the encoding ?
        part.add_header('Content-Disposition',  # Set the header ?
                        'attachment; filename= ' + filename)
        msg.attach(part)                        # Attach the attachments to the message


text = msg.as_string()  # convert message to string

server = smtplib.SMTP_SSL(SERVER_ADDRESS, SERVER_PORT)  # Connect to server
server.login(email_username, email_password)    # Authenticate
send_addresses = to_addresses + cc_addresses + bcc_addresses
server.sendmail(email_username, send_addresses, text)   # Send Mail
server.quit()   # Close connection

