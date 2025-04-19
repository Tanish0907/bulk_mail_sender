from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from smtplib import SMTP

import markdown


def mail(RECIPIENT):
    HOST = 'smtp.gmail.com'
    PORT = 587
    SENDER = 'sharmatanish097654@gmail.com'
    PASSWORD = 'aojj tmmw bplp nden '
    # RECIPIENT = 'sharmatanish0907@gmail.com'
    MESSAGE_FILE = 'compose.md'
    DISPLAY_NAME = 'Tanish'
    with open(MESSAGE_FILE) as file:
        message = file.read()
    server = SMTP(host=HOST, port=PORT)
    server.connect(host=HOST, port=PORT)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(user=SENDER, password=PASSWORD)

    multipart_msg = MIMEMultipart("alternative")

    multipart_msg["Subject"] = message.splitlines()[0]
    multipart_msg["From"] = DISPLAY_NAME + f' <{SENDER}>'
    multipart_msg["To"] = RECIPIENT

    text = message
    html = markdown.markdown(text)

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    multipart_msg.attach(part1)
    multipart_msg.attach(part2)


    server.sendmail(SENDER, RECIPIENT, multipart_msg.as_string())

    print('Sent email successfully!')

