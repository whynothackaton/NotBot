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
            email {[type]} -- [description]
        '''
        self.email = email
        self.imap = None
        self.id = '3ee652c711e9455c98afa34a2807e4f3'

    def connection(self, token):
        '''[summary]

        Arguments:
            token {[type]} -- [description]
        '''
        auth_string = 'user={0}\1auth=Bearer {1}\1\1' \
            .format(self.email, token)
        self.imap = imaplib.IMAP4_SSL('imap.yandex.com')
        self.imap.authenticate('XOAUTH2', lambda x: auth_string)

    def get_new_message(self):
        '''[summary]

        Returns:
            [type] -- [description]
        '''
        status, self.amount_message = self.imap.select('INBOX')

        assert status == 'OK'
        date = datetime.date.today().strftime('%d-%b-%Y')
        status, data = self.imap.uid(
            'search', None, '(ON {0})'.format(date))

        if len(data[0]) != 0:
            assert status == 'OK'
            ids = data[0]  # data is a list.
            id_list = ids.split()  # ids is a space separated string

            for id in id_list:
                messages = ''
                status, data = self.imap.uid(  # fetch the email body () for the given ID
                    'fetch', id, '(RFC822)')

                assert status == 'OK'
                time_message, message = self.parse_message(data)

                now_delta_datetime = datetime.datetime.now() - \
                    datetime.timedelta(seconds=30) - \
                    datetime.timedelta(hours=1)
                message_datetime = datetime.datetime.strptime(
                    date + ' ' + time_message, '%d-%b-%Y %H:%M:%S')

                print(message_datetime)
                print(now_delta_datetime)
                print(message_datetime >= now_delta_datetime)
                print()

                if message_datetime >= now_delta_datetime:
                    messages += message
                    print('messages:\n', messages)

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

        '''
        body = None
        for part in email_message.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True)
            else:
                continue
        
        status, data = self.imap.fetch(self.amount_letters[0], '(UID BODY[TEXT])')
        import base64
        #print(base64.b64encode(data[0][0]))
        '''
        time = str(email.header.make_header(
            email.header.decode_header(
                email_message['Date']))).split()[4]
        email_from = 'Автор: ' + str(email.header.make_header(
            email.header.decode_header(email_message['From'])))
        subject = 'Тема: ' + str(email.header.make_header(
            email.header.decode_header(email_message['Subject'])))

        return time, email_from + '\n ' + subject + '\n'

    def close_connection(self):
        '''[summary]
        '''
        self.imap.close()
