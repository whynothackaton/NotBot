import imaplib
import getpass
import email
import datetime


class MailBox:
    def __init__(self, email):
        self.email = email       
        self.imap = None
        self.id = '3ee652c711e9455c98afa34a2807e4f3'

    def connection(self, token):
        auth_string = 'user={0}\1auth=Bearer {1}\1\1' \
            .format(self.email, token)
        self.imap = imaplib.IMAP4_SSL('imap.yandex.com')
        self.imap.authenticate('XOAUTH2', lambda x: auth_string)
  
    def get_new_message(self): 
        status, message = self.imap.select('INBOX')
        assert status == 'OK'

        '''        
        date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
        result, data = self.imap.uid('search', None, '(SENTSINCE {date})'.format(date=date))        
        
        ids = data[0] # data is a list.
        id_list = ids.split() # ids is a space separated string
        latest_email_id = id_list[-1] # get the latest
        
        result, data = self.imap.uid('fetch', latest_email_id, "(RFC822)") # fetch the email body (RFC822) for the given ID
        '''

        result, data = self.imap.search(None, 'ALL')
        ids = data[0] # data is a list.
        id_list = ids.split() # ids is a space separated string
        latest_email_id = id_list[-1] # get the latest
        result, data = self.imap.uid('fetch', latest_email_id, "(RFC822)") # fetch the email body (RFC822) for the given ID

        raw_email = data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        date_tuple = email.utils.parsedate_tz(email_message['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            local_message_date = "%s" %(str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
        
        email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))
        email_to = str(email.header.make_header(email.header.decode_header(email_message['To'])))
        subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))

        #if local_date > date_time:
        return email_from + '\n ' + subject
        #else:
        #    None

    def close_connection(self):
        self.imap.close()
