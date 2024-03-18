import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email import encoders


class SendCheck:
    def __init__(self, receiver_email, sender_email="shurikm30@gmail.com", sender_password='jlkx fjay nrfj wmye'):
        self.receiver_email = receiver_email
        self.sender_email = sender_email
        self.sender_password = sender_password

    def sendCheck(self, body='OK!'):
        print(self.receiver_email)

        subject = 'Clover'
        recipient_name = self.receiver_email.split('@')[0]

        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = self.receiver_email
        message['Subject'] = subject

        message.attach(MIMEText(body, 'plain', 'utf-8'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, self.receiver_email, message.as_string())
            print('Письмо успешно отправлено')
        except Exception as e:
            print(f'Ошибка при отправке письма: {e}')
        finally:
            server.quit()

        return True

    def sendFile(self, file_path):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)

            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = self.receiver_email

            with open(file_path, 'rb') as file:
                attachment = MIMEApplication(file.read())
                attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
                message.attach(attachment)

            server.sendmail(self.sender_email, self.receiver_email, message.as_string())
            print('Файл успешно отправлен')
        except Exception as e:
            print(f'Ошибка при отправке файла: {e}')
        finally:
            server.quit()

        return True


