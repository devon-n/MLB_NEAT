import os
from email.policy import SMTP
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders


def send_email_func():
    # Path
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Creds
    creds = []
    with open('creds.txt') as f:
        for line in f:
            creds.append(line)

    # Sender, Receiver, subject, body
    sender = 'devnathan94@gmail.com'
    receivers = ['devnathan94@gmail.com']
    body = 'Hello Dev,\n\nHere is your daily betting report.'
    subject = 'Daily Betting Report'

    # Create message
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ','.join(receivers)
    msg['Body'] = body
    textPart = MIMEText(body, 'plain')
    msg.attach(textPart)

    # Add file
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(f'{dir_path}/tmp/report.pdf', 'rb').read())
    encoders.encode_base64(part)
    part.add_header(f'Content-Disposition', 'attachment; filename="{dir_path} + /tmp/report.pdf"')
    msg.attach(part)

    # Connect to Gmail SMTP server
    s = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465)
    s.login(user = creds[0], password = creds[1])
    s.sendmail(sender, receivers, msg.as_string())
    s.quit()
