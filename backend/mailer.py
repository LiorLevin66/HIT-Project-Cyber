"""Sends an email with SMTP. If SMTP is not configured, writes it to outbox.log."""
import smtplib
from email.message import EmailMessage

import config


def send_mail(to, subject, body):
    if not config.SMTP_HOST:
        with open(config.OUTBOX_PATH, "a", encoding="utf-8") as f:
            f.write(f"To: {to}\nSubject: {subject}\n\n{body}\n{'-' * 40}\n")
        print(f"[mail] SMTP not configured, mail to {to} written to outbox.log")
        return

    msg = EmailMessage()
    msg["From"] = config.SMTP_SENDER
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
        server.starttls()
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.send_message(msg)
