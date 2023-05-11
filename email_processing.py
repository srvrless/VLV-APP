from random import randint
import smtplib
from config import ADDR_FROM, EMAIL_PASSWORD



'''
Working with email
'''


class EmailProcessing:
    def __init__(self):
        self.verification_code = 0
        return
    
    async def email_text(self):
         code = randint(0, 10000)
         wrapper = '''Your registration code Code:{}'''.format(code)
         return wrapper, code

    async def send_email(self, email):
        try:
            email_text, code = await self.email_text()
            server = smtplib.SMTP('smtp.yandex.ru', 587)
            server.ehlo()  
            server.starttls()
            server.login(ADDR_FROM, EMAIL_PASSWORD)
            subject = 'Registration code'
            message = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (ADDR_FROM, email, subject, email_text)

            server.set_debuglevel(1) 
            server.sendmail(ADDR_FROM, email, message)
            server.quit()
            return code
        except: Exception('Smth Wrong with email sending')