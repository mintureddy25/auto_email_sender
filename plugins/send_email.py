"""
Plugin: send_email
==================
Purpose
-------
Send a one-off, standalone email from the configured Gmail account
(EMAIL_USER in .env) to any recipient. Resume PDF attached by default.

Use this when the email is NEW — not a reply. For threaded replies to
an existing conversation, use plugins.reply_email instead.

Body formatting
---------------
- Plain text with **bold**, *italic*, and bare URLs supported
- ** / * markers are rendered as <strong>/<em> in the HTML part
- Bare URLs become clickable links in the HTML part
- Plain-text part has markers stripped so it reads cleanly

Function
--------
send_email(to, subject, body, *, attach_resume=True, attach_pdf=None)

Args
----
to (str)             : recipient email address
subject (str)        : subject line
body (str)           : plain text body (markdown-style markers OK)
attach_resume (bool) : True -> attach default resume PDF (default True)
attach_pdf (str)     : path to custom PDF (overrides resume)

Returns
-------
None. Raises FileNotFoundError if the attachment is missing,
smtplib.SMTPException on SMTP failure.

Example
-------
    from plugins.send_email import send_email

    send_email(
        to="jane@example.com",
        subject="Quick intro — 3+ yrs Full Stack",
        body=(
            "Hi Jane,\\n\\n"
            "I'm a **Full Stack Developer** with 3+ yrs of experience — "
            "happy to connect about the role.\\n\\n"
            "Portfolio: https://saitejareddy.online\\n"
        ),
    )

CLI
---
    python3 -m plugins.send_email \\
        --to jane@example.com \\
        --subject "Quick intro" \\
        --body "Hi Jane,..."
"""
import os

from src.config import RESUME_PDF
from plugins._smtp import smtp_send


def send_email(to: str, subject: str, body: str, *,
               cc=None, bcc=None,
               attach_resume: bool = True, attach_pdf: str = None) -> None:
    pdf = attach_pdf or (RESUME_PDF if attach_resume else None)
    if pdf and not os.path.exists(pdf):
        raise FileNotFoundError(f"Attachment not found: {pdf}")
    smtp_send(to, subject, body, cc=cc, bcc=bcc, attach_pdf=pdf)
    cc_part = f" cc:{','.join(cc)}" if cc else ""
    print(f"SENT to {to}{cc_part}  (subject: {subject})")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Send an email via Gmail SMTP.")
    p.add_argument("--to", required=True, help="Recipient email")
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True, help="Plain text body (supports **bold**)")
    p.add_argument("--no-resume", action="store_true", help="Don't attach resume PDF")
    p.add_argument("--attach", help="Path to custom PDF to attach instead of resume")
    args = p.parse_args()

    send_email(
        args.to, args.subject, args.body,
        attach_resume=not args.no_resume,
        attach_pdf=args.attach,
    )
