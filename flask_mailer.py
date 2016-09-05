import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from flask import Flask, render_template, redirect, url_for, request, send_from_directory


import config

app = Flask(__name__)


def send_mail(sender_email, smtp_username, smtp_password, smtp_server, port, timeout, toaddrs, subject, body, content_type, fname=None):
    fromaddr = sender_email

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['Subject'] = subject

    msg.attach(MIMEText(body, content_type))

    if fname:
        with open(os.path.join(config.UPLOAD_FOLDER, fname), "rb") as f:
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


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(config.UPLOAD_FOLDER,
                               filename)


@app.route('/', methods=['GET'])
def main_get():
    return render_template("mailer.html")


@app.route('/', methods=['POST'])
def main_post():
    _file = request.files.get("file")
    if _file:
        _file.save(os.path.join(config.UPLOAD_FOLDER, _file.filename))

    r = send_mail(request.form.get("sender_email") or config.SMTP_USERNAME,
                  request.form.get("smtp_username") or config.SMTP_USERNAME,
                  request.form.get("smtp_password") or config.SMTP_PASSWORD,
                  request.form.get("smtp_server") or config.SMTP_SERVER,
                  int(request.form.get("smtp_port")) or config.PORT,
                  config.TIMEOUT, parse_email(request.form.get("list")),
                  request.form.get("subject"), request.form.get("message"),
                  request.form.get("content_type"),
                  _file.filename if _file else None)
    return redirect(url_for('main_get'))


if __name__ == '__main__':
    app.run(port=5001, debug=True)
