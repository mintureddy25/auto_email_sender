"""
Internal helper (not a user-facing plugin).
Shared SMTP send used by send_email.py and reply_email.py.

- Loads Gmail creds from src.config (which reads auto_email_sender/.env)
- Always builds multipart/alternative: plain text + HTML
- **bold**, *italic*, bare URLs are auto-rendered in the HTML part
- Optional PDF attachment, optional In-Reply-To / References threading headers
"""
import mimetypes
import os
import re
import smtplib
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import EMAIL_USER, EMAIL_PASSWORD, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT


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


def _attach_file(msg, filepath):
    ctype, encoding = mimetypes.guess_type(filepath)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)
    with open(filepath, "rb") as f:
        if maintype == "application" and subtype == "pdf":
            part = MIMEApplication(f.read(), _subtype="pdf")
        else:
            part = MIMEBase(maintype, subtype)
            part.set_payload(f.read())
            encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f'attachment; filename="{os.path.basename(filepath)}"',
    )
    msg.attach(part)


def smtp_send(to, subject, body, *, cc=None, bcc=None,
              attach_pdf=None, attach_files=None,
              in_reply_to=None, references=None):
    cc_list = [a for a in (cc or []) if a]
    bcc_list = [a for a in (bcc or []) if a]

    msg = MIMEMultipart("mixed")
    msg["From"] = EMAIL_USER
    msg["To"] = to
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)
    msg["Subject"] = subject
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
    if references:
        msg["References"] = references

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(_to_plain(body), "plain", "utf-8"))
    alt.attach(MIMEText(_to_html(body), "html", "utf-8"))
    msg.attach(alt)

    if attach_pdf:
        _attach_file(msg, attach_pdf)
    if attach_files:
        for fp in attach_files:
            _attach_file(msg, fp)

    # Build the recipient list explicitly so Bcc gets delivered without
    # leaking via the headers.
    recipients = [to] + cc_list + bcc_list
    with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, timeout=180) as s:
        s.starttls()
        s.login(EMAIL_USER, EMAIL_PASSWORD)
        s.send_message(msg, to_addrs=recipients)
