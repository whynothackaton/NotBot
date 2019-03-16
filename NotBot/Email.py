import imaplib
import getpass


class Email:
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

        typ, data = self.imap.search(None, 'ALL')
        print(data)

        for number in data[0].split():
            typ, message_data = self.imap.fetch(number, '(RFC822)')
            print(data)
            print('Message %s\n%s\n' % (number, message_data[0][1]))  

        mail = email.message_from_bytes(message_data[0][1])     

    def close_connection(self):
        self.imap.close()


email = Email('mail.ru', 'naidenkoandrey1997', '**')
print(email.email_domen)
email.connection()