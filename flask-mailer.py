import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from flask import Flask, render_template, redirect, url_for, request

import config

app = Flask(__name__)


def send_mail(sender_email, smtp_username, smtp_password, smtp_server, port, timeout, toaddrs, subject, body, fname=None):
    fromaddr = sender_email

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['Subject'] = subject

    msg.attach(MIMEText(body, "html"))

    if fname:
        with open(fname, "rb") as f:
            attach_file = MIMEApplication(f.read())
            attach_file.add_header('Content-Disposition', 'attachment', filename=os.path.basename(fname))
            msg.attach(attach_file)

    server = None
    try:
        server = smtplib.SMTP_SSL(smtp_server, port, timeout=timeout)
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddrs, text)
    finally:
        if server:
            server.close()

    return True


def parse_email(email_list):
    return email_list.split()


@app.route('/', methods=['GET'])
def main_get():
    # r = send_mail(["vitalij.banit@gmail.com", "oldtigersvoice@gmail.com"], "test spam", "Hello!")
    # if not r:
    #     raise Exception("Error send email")
    return render_template("mailer.html")


@app.route('/', methods=['POST'])
def main_post():
    r = send_mail(request.form.get("sender_email") or config.SMTP_USERNAME,
                  request.form.get("smtp_username") or config.SMTP_USERNAME,
                  request.form.get("smtp_password") or config.SMTP_PASSWORD,
                  request.form.get("smtp_server") or config.SMTP_SERVER,
                  request.form.get("smtp_port") or config.PORT,
                  config.TIMEOUT, parse_email(request.form.get("list")),
                  request.form.get("subject"), request.form.get("message"))
    # if not r:
    #     raise Exception("Error send email")
    return redirect(url_for('main_get'))


if __name__ == '__main__':
    app.run(port=5001)
