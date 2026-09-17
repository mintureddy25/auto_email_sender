"""
Internal helper (not a user-facing plugin).
Shared IMAP connection + message parsing used by read_email.py,
read_all_emails.py, reply_email.py.

- Connects to imap.gmail.com:993 with the same Gmail app password used for SMTP
- parse_message() returns a dict with: from, to, subject, date,
  message_id, references, body (plain text; HTML stripped as fallback)
"""
import email
import imaplib
import re
from email.header import decode_header

from src.config import EMAIL_USER, EMAIL_PASSWORD


def imap_connect(mailbox: str = "INBOX"):
    m = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    m.login(EMAIL_USER, EMAIL_PASSWORD)
    m.select(mailbox)
    return m


def decode_mime(value) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    return "".join(
        p.decode(enc or "utf-8", errors="replace") if isinstance(p, bytes) else p
        for p, enc in parts
    )


def _extract_body(msg) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            disp = str(part.get("Content-Disposition", ""))
            if ct == "text/plain" and "attachment" not in disp:
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode(
                        part.get_content_charset() or "utf-8", errors="replace"
                    )
                    break
        if not body:
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload:
                        html = payload.decode(
                            part.get_content_charset() or "utf-8", errors="replace"
                        )
                        body = re.sub(r"<[^>]+>", "", html)
                        break
    else:
        payload = msg.get_payload(decode=True)
        body = payload.decode(errors="replace") if payload else ""
    return body.strip()


def parse_message(raw_bytes: bytes) -> dict:
    msg = email.message_from_bytes(raw_bytes)
    return {
        "from": decode_mime(msg.get("From")),
        "to": decode_mime(msg.get("To")),
        "subject": decode_mime(msg.get("Subject")),
        "date": msg.get("Date"),
        "message_id": msg.get("Message-ID"),
        "references": msg.get("References", ""),
        "body": _extract_body(msg),
    }


def extract_address(from_header: str) -> str:
    m = re.search(r"<([^>]+)>", from_header)
    if m:
        return m.group(1)
    m = re.search(r"[\w\.\-+]+@[\w\.\-]+", from_header)
    return m.group(0) if m else from_header
