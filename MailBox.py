import imaplib
import getpass
import email
import datetime
import re
import time


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
        auth_string = 'user={0}\1auth=Bearer {1}\1\1' \
            .format(self.email, token)

        im = 'imap.' + self.email.split('@')[1]
        print("IMAP=", im)
        self.imap = imaplib.IMAP4_SSL(im)

        self.imap.authenticate('XOAUTH2', lambda x: auth_string)

    def get_new_message(self):
        '''[summary]
        
        Returns:
            [type] -- [description]
        '''
        messages = ''
        status, self.amount_message = self.imap.select('INBOX')

        assert status == 'OK'
        date = datetime.date.today().strftime('%d-%b-%Y')
        status, data = self.imap.uid('search', None, '(ON {0})'.format(date))

        if len(data[0]) != 0:
            assert status == 'OK'
            ids = data[0]  # data is a list.
            id_list = ids.split()  # ids is a space separated string
            for id in id_list:
                status, data = self.imap.uid(  # fetch the email body () for the given ID
                    'fetch', id, '(RFC822)')

                assert status == 'OK'
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
                    datetime.timedelta(seconds=30)
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
        subject = 'Тема: ' + str(
            email.header.make_header(
                email.header.decode_header(email_message['Subject'])))

        # this will loop through all the available multiparts in mail
        for part in email_message.walk():
            # ignore attachments/html
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True)
                text = body.decode().split()[0]

        return time, email_from + '\n' + subject + '\n\n' + text + '\n'

    def close_connection(self):
        '''[summary]
        '''
        self.imap.close()


'''
mb = MailBox('rollabushka@yandex.ru')
file = open('..\\..\\token.txt')
token = file.read()
mb.connection(token)
print(mb.get_new_message())
mb.close_connection()
'''
