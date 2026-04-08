import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.config import EMAIL_USER, EMAIL_PASSWORD, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, RESUME_PDF, EMAIL_BODY_TEMPLATE


def send(email, subject):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(EMAIL_BODY_TEMPLATE.format(subject=subject), "plain"))

    if os.path.exists(RESUME_PDF):
        with open(RESUME_PDF, "rb") as pdf_file:
            pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf")
            pdf_attachment.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(RESUME_PDF)}"',
            )
            msg.attach(pdf_attachment)
    else:
        print(f"[ERROR] Resume PDF not found: {RESUME_PDF}")
        return False

    with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)

    return True
