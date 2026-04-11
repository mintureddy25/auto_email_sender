import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import (
    EMAIL_USER, EMAIL_PASSWORD, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT,
    RESUME_PDF, EMAIL_BODY_TEMPLATE, SUBJECT,
)
from src.collectors.emails import Emails
from src.senders import register
from src.senders.base import BaseSender


def _send_smtp(email: str, subject: str) -> None:
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(EMAIL_BODY_TEMPLATE.format(subject=subject), "plain"))

    if not os.path.exists(RESUME_PDF):
        raise FileNotFoundError(f"Resume PDF not found: {RESUME_PDF}")

    with open(RESUME_PDF, "rb") as pdf_file:
        pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf")
        pdf_attachment.add_header(
            "Content-Disposition",
            f'attachment; filename="{os.path.basename(RESUME_PDF)}"',
        )
        msg.attach(pdf_attachment)

    with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)


@register
class EmailSender(BaseSender):
    name = "email"
    data_type = Emails

    def send(self, job: dict) -> None:
        _send_smtp(job["email"], job.get("subject", SUBJECT))


# Back-compat shim for any caller that still does `email_sender.send(...)`
def send(email: str, subject: str) -> None:
    _send_smtp(email, subject)
