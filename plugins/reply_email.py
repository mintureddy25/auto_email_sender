"""
Plugin: reply_email
===================
Purpose
-------
Send a THREADED reply — the response appears inside the SAME Gmail
conversation as the original email. Works by:
  1. Looking up the latest email from the given sender via IMAP
  2. Reading its Message-ID + References headers
  3. Sending the reply with In-Reply-To + References set correctly
  4. Subject auto-prefixed with "Re: " if it isn't already

Use this when replying to a recruiter's follow-up, a screening questionnaire,
or any email in an existing thread. For new outgoing mail use plugins.send_email.

Function
--------
reply_to_latest_from(sender, body, *, attach_resume=True,
                     attach_pdf=None, subject_override=None)

Args
----
sender (str)           : the exact sender email to reply to
                         e.g. "opportunity@univar.in"
body (str)             : plain text reply body — **bold**, *italic*, URLs OK
attach_resume (bool)   : attach default resume PDF (default True)
attach_pdf (str)       : path to a custom PDF (overrides resume)
subject_override (str) : override subject; default reuses original subject
                         with "Re: " prepended when missing

Returns
-------
dict { 'to', 'subject', 'in_reply_to', 'references' } on success.
Raises LookupError if no email from that sender exists in INBOX.

Example
-------
    from plugins.reply_email import reply_to_latest_from

    reply_to_latest_from(
        sender="opportunity@univar.in",
        body=(
            "Hi Rashmi,\\n\\n"
            "Thanks for the quick response. Details below:\\n\\n"
            "**Current CTC**: 11.5 LPA\\n"
            "**Notice Period**: Immediate\\n"
        ),
    )

CLI
---
    python3 -m plugins.reply_email \\
        --sender opportunity@univar.in \\
        --body "Hi Rashmi, ..."
"""
import os

from src.config import RESUME_PDF
from plugins._imap import imap_connect, parse_message, extract_address
from plugins._smtp import smtp_send


def reply_to_latest_from(sender: str, body: str, *,
                         attach_resume: bool = True,
                         attach_pdf: str = None,
                         attach_files: list = None,
                         subject_override: str = None,
                         cc: list = None,
                         bcc: list = None) -> dict:
    m = imap_connect()
    try:
        _, data = m.search(None, "FROM", f'"{sender}"')
        ids = data[0].split()
        if not ids:
            raise LookupError(f"No email found from {sender}")
        _, msg_data = m.fetch(ids[-1], "(RFC822)")
        info = parse_message(msg_data[0][1])
    finally:
        m.logout()

    subject = subject_override or info["subject"]
    if not subject.lower().lstrip().startswith("re:"):
        subject = "Re: " + subject

    in_reply_to = info["message_id"]
    if info["references"]:
        references = (info["references"] + " " + in_reply_to).strip()
    else:
        references = in_reply_to

    pdf = attach_pdf or (RESUME_PDF if attach_resume else None)
    if pdf and not os.path.exists(pdf):
        raise FileNotFoundError(f"Attachment not found: {pdf}")
    if attach_files:
        for fp in attach_files:
            if not os.path.exists(fp):
                raise FileNotFoundError(f"Attachment not found: {fp}")

    to_addr = extract_address(info["from"])

    smtp_send(
        to_addr, subject, body,
        cc=cc,
        bcc=bcc,
        attach_pdf=pdf,
        attach_files=attach_files,
        in_reply_to=in_reply_to,
        references=references,
    )
    cc_part = f" cc:{','.join(cc)}" if cc else ""
    print(f"SENT threaded reply to {to_addr}{cc_part}  (subject: {subject})")
    return {
        "to": to_addr,
        "cc": cc or [],
        "subject": subject,
        "in_reply_to": in_reply_to,
        "references": references,
    }


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Threaded reply to the latest email from a sender.")
    p.add_argument("--sender", required=True, help="Sender email to reply to")
    p.add_argument("--body", required=True, help="Reply body (plain text)")
    p.add_argument("--subject", help="Override subject (default reuses original)")
    p.add_argument("--no-resume", action="store_true")
    p.add_argument("--attach", help="Path to custom PDF attachment")
    p.add_argument("--cc", help="Comma-separated CC addresses")
    p.add_argument("--bcc", help="Comma-separated BCC addresses")
    args = p.parse_args()

    cc_list = [a.strip() for a in args.cc.split(",")] if args.cc else None
    bcc_list = [a.strip() for a in args.bcc.split(",")] if args.bcc else None

    reply_to_latest_from(
        args.sender, args.body,
        attach_resume=not args.no_resume,
        attach_pdf=args.attach,
        subject_override=args.subject,
        cc=cc_list,
        bcc=bcc_list,
    )
