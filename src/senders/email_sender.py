import os
import re
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import (
    EMAIL_USER, EMAIL_PASSWORD, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT,
    RESUME_PDF, SUBJECT, SUBJECT_BY_SOURCE, BODY_BY_SOURCE, EMAIL_BODY_TEMPLATE,
)
from src.collectors.emails import Emails
from src.senders import register
from src.senders.base import BaseSender


def _resolve_template(template, job):
    try:
        return template.format_map({
            "name": job.get("name") or "there",
            "company": job.get("company") or "your company",
            "title": job.get("title") or "",
            "email": job.get("email") or "",
            "source": job.get("source") or "",
            "role": job.get("role") or "Full Stack Developer",
        })
    except (KeyError, ValueError):
        return template


def _to_plain(text: str) -> str:
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", t)
    return t


def _to_html(text: str) -> str:
    html = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", html)
    html = re.sub(r"(https?://[^\s<]+)", r'<a href="\1">\1</a>', html)
    html = html.replace("\n", "<br>\n")
    return (
        '<div style="font-family:Arial,Helvetica,sans-serif;'
        'font-size:14px;line-height:1.55;color:#222;">'
        f"{html}</div>"
    )


def _send_smtp(email: str, subject: str, body: str) -> None:
    msg = MIMEMultipart("mixed")
    msg["From"] = EMAIL_USER
    msg["To"] = email
    msg["Subject"] = subject

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(_to_plain(body), "plain", "utf-8"))
    alt.attach(MIMEText(_to_html(body), "html", "utf-8"))
    msg.attach(alt)

    if not os.path.exists(RESUME_PDF):
        raise FileNotFoundError(f"Resume PDF not found: {RESUME_PDF}")

    with open(RESUME_PDF, "rb") as pdf_file:
        pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf")
        pdf_attachment.add_header(
            "Content-Disposition",
            f'attachment; filename="{os.path.basename(RESUME_PDF)}"',
        )
        msg.attach(pdf_attachment)

    with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, timeout=30) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)


@register
class EmailSender(BaseSender):
    name = "email"
    data_type = Emails

    def send(self, job: dict) -> None:
        source = job.get("source", "")
        subject = _resolve_template(
            SUBJECT_BY_SOURCE.get(source, SUBJECT), job
        )
        body = _resolve_template(
            BODY_BY_SOURCE.get(source, EMAIL_BODY_TEMPLATE), job
        )
        _send_smtp(job["email"], subject, body)
