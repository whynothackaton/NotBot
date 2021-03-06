import imaplib
import getpass
import email
import datetime
import re
import time
import base64


class MailBox:
    def __init__(self, email):
        '''[summary]
        
        Arguments:
            email {str} -- user's email
        '''
        self.email = email
        self.imap = None

    def connection(self, token):
        '''[summary]
        
        Arguments:
            token {[type]} -- [description]
        '''
        auth_string = 'user={0}\001auth=Bearer {1}\001\001' \
            .format(self.email, token)

        try:
            if '@mail.ru' in self.email:        
                print('auth_mail:', auth_string)
                #auth_string = base64.b64encode(bytes(auth_string,"utf-8"))
                #auth_string = auth_string.replace(b'\n',b'')
                print('auth_mail after b64encode:', auth_string)
                self.imap = imaplib.IMAP4_SSL('imap.mail.ru')
            if 'yandex' in self.email:
                self.imap = imaplib.IMAP4_SSL('imap.yandex.com')
            if 'gmail' in self.email:
                self.imap = imaplib.IMAP4_SSL('imap.gmail.com')
        except Exception as exp:
            print('Exception in self.connection:', exp)
            return False

        try:
            self.imap.authenticate('XOAUTH2', lambda x: auth_string)
        except Exception as exception:
            print("Exception with AUTH:", exception)
            return False
        return True

    def get_new_message(self):
        '''[summary]
        
        Returns:
            [type] -- [description]
        '''
        messages = ''
        try:
            status, self.amount_message = self.imap.select('INBOX')
        except Exception as exp:
            print('Exception with IMAP SELECT:', exp)            

        date = datetime.date.today().strftime('%d-%b-%Y')
        
        data = ['']
        try:
            status, data = self.imap.uid('search', None, '(ON {0})'.format(date))
        except Exception as exp:
            print('Exception with IMAP SEARCH', exp)

        if len(data[0]) != 0:
            ids = data[0]  # data is a list.
            id_list = ids.split()  # ids is a space separated string
            for id in id_list:
                status, data = self.imap.uid(  # fetch the email body () for the given ID
                    'fetch', id, '(RFC822)')

                message_date, message = self.parse_message(data)

                message_time = message_date.split()[4]
                message_timezone = int(message_date.split()[5][0:3])
                system_timezone = int(time.timezone / -3600)
                variance_timezone = abs(message_timezone - system_timezone)

                if message_timezone < system_timezone:
                    hour = int(message_time[0:2])
                    message_time = str(hour +
                                       variance_timezone) + message_time[2:8]
                else:
                    hour = int(message_time[0:2])
                    message_time = str(hour -
                                       variance_timezone) + message_time[2:8]

                now_delta_datetime = datetime.datetime.now() - \
                    datetime.timedelta(seconds=100)
                message_datetime = datetime.datetime.strptime(
                    date + ' ' + message_time, '%d-%b-%Y %H:%M:%S')

                if message_datetime >= now_delta_datetime:
                    messages += message

        if len(messages) != 0:
            return messages
        else:
            return None

    def parse_message(self, data):
        '''[summary]
        
        Arguments:
            data {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        '''
        raw_email = data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        time = str(
            email.header.make_header(
                email.header.decode_header(email_message['Date'])))
        email_from = 'Автор: ' + str(
            email.header.make_header(
                email.header.decode_header(email_message['From'])))

        subject = 'Тема: '
        try:
            subject += str(
                email.header.make_header(
                    email.header.decode_header(email_message['Subject']))) + \
                '\n\n'
        except:
            subject = ''

        # this will loop through all the available multiparts in mail
        text = ''
        for part in email_message.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True)
                try:
                    text = body.decode()
                except Exception as exp:
                    print('Exception in parse_letter:', exp)
                    print('body', body)

        return time, email_from + '\n' + subject + text

    def close_connection(self):
        '''[summary]
        '''
        self.imap.close()