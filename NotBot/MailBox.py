import imaplib
import getpass
import email
import quopri
from email.parser import Parser
from email.message import EmailMessage


class MailBox:
    def __init__(self):
        self.email_domen = None
        self.login = None
        self.password = None
        self.imap = None

    def __init__(self, email_domen, login, password):
        self.email_domen = email_domen
        self.login = login
        self.password = password
        self.imap = None

    def connection(self):
        self.imap = imaplib.IMAP4_SSL('imap.' + self.email_domen)
        self.imap.login(self.login + '@' + self.email_domen, self.password)        
    
    def get_new_message(self): 
        status, message = self.imap.select('INBOX')
        assert status == 'OK'
        result, data = self.imap.search(None, 'ALL')
        ids = data[0] # data is a list.
        id_list = ids.split() # ids is a space separated string
        latest_email_id = id_list[-1] # get the latest
        result, data = self.imap.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822) for the given ID

        raw_email = data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))
        email_to = str(email.header.make_header(email.header.decode_header(email_message['To'])))
        subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))

        print(subject)

    def close_connection(self):
        self.imap.close()
        
mail = MailBox()
mail.connection()
mail.get_new_message()