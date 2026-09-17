"""
Plugin: read_email
==================
Purpose
-------
Read a SINGLE email from INBOX (the latest that matches). Two lookup modes:
  - read_latest_from(sender)       : latest email from a specific address
  - read_by_subject(substring)     : latest email whose subject contains substring

Use this when you need the body of a specific email before drafting a
reply, or when you need the Message-ID to thread manually.

Functions
---------
read_latest_from(sender: str) -> dict
read_by_subject(subject_contains: str) -> dict

Returns (both)
--------------
    {
        'from'        : str,    # "Name <addr@host>"
        'to'          : str,
        'subject'     : str,
        'date'        : str,    # RFC 2822 format
        'message_id'  : str,    # use for In-Reply-To when threading manually
        'references'  : str,    # existing thread chain (may be empty)
        'body'        : str,    # plain text; HTML stripped if only HTML present
    }
Raises LookupError if nothing matches.

Example
-------
    from plugins.read_email import read_latest_from
    msg = read_latest_from("opportunity@univar.in")
    print(msg['subject'])
    print(msg['body'])

CLI
---
    python3 -m plugins.read_email --from opportunity@univar.in
    python3 -m plugins.read_email --subject "Full Stack"
"""
from plugins._imap import imap_connect, parse_message


def read_latest_from(sender: str) -> dict:
    m = imap_connect()
    try:
        _, data = m.search(None, "FROM", f'"{sender}"')
        ids = data[0].split()
        if not ids:
            raise LookupError(f"No email found from {sender}")
        _, msg_data = m.fetch(ids[-1], "(RFC822)")
        return parse_message(msg_data[0][1])
    finally:
        m.logout()


def read_by_subject(subject_contains: str) -> dict:
    m = imap_connect()
    try:
        _, data = m.search(None, "SUBJECT", f'"{subject_contains}"')
        ids = data[0].split()
        if not ids:
            raise LookupError(
                f'No email found with subject containing "{subject_contains}"'
            )
        _, msg_data = m.fetch(ids[-1], "(RFC822)")
        return parse_message(msg_data[0][1])
    finally:
        m.logout()


if __name__ == "__main__":
    import argparse
    import json

    p = argparse.ArgumentParser(description="Read a single email from INBOX")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--from", dest="sender", help="Latest email from this sender")
    g.add_argument("--subject", dest="subject", help="Latest email with subject containing this")
    args = p.parse_args()

    msg = read_latest_from(args.sender) if args.sender else read_by_subject(args.subject)
    print(json.dumps(msg, indent=2, default=str))
