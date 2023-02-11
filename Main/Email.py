import datetime
import smtplib
import config
import logging

from colorama import Fore

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logging.basicConfig(filename=config.APP_LOG_PATH, encoding='utf-8', level=logging.INFO, format="%(asctime)s: [%(levelname)s] [LINE:%(lineno)s] [FILE:%(filename)s] %(message)s")


class Email:
    def __init__(self):

        self.sender_email = config.SENDER_EMAIL
        self.sender_email_password = config.SENDER_EMAIL_PASSWORD
        self.receiver_email = config.RECEIVER_EMAIL
        self.smtp_server = config.SMTP_SERVER

    def generate_message(self, subject, message) -> MIMEMultipart:
        try:
            message = MIMEMultipart("alternative", None, [MIMEText(message, 'html')])
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = self.receiver_email
            return message
        except Exception as exception:
            logging.error(exception)

    def send_message(self, subject, message):
        try:
            message = self.generate_message(subject, message)
            server = smtplib.SMTP(self.smtp_server)
            server.ehlo()
            server.starttls()
            server.login(self.sender_email, self.sender_email_password)
            server.sendmail(self.sender_email, self.receiver_email, message.as_string())
            server.quit()

            print(Fore.YELLOW + '[+]', Fore.GREEN + 'Email Sent Successfully', Fore.MAGENTA + '{}'.format(subject), Fore.BLUE + '{}'.format(datetime.datetime.now().strftime("%Y %m %d %H:%M:%S")))
        except Exception as exception:
            logging.error(exception)
