"""
Plugin: read_all_emails
=======================
Purpose
-------
List recent emails from INBOX (latest first). Optional filter for
unread-only. Body of each message is truncated for quick scanning;
use plugins.read_email for the full body of a specific message.

Use this when you want a bulk overview — "what came in today",
"show me unread recruiter replies", triaging the inbox, etc.

Function
--------
list_recent(limit=20, unread_only=False, body_chars=500) -> list[dict]

Args
----
limit (int)         : how many latest messages to return (default 20)
unread_only (bool)  : True -> only UNSEEN messages (default False)
body_chars (int)    : truncate each body to this many chars (default 500)

Returns
-------
List of message dicts (latest first). Each dict has the same fields as
plugins.read_email: from, to, subject, date, message_id, references, body.

Example
-------
    from plugins.read_all_emails import list_recent

    for m in list_recent(limit=10, unread_only=True):
        print(f"{m['date']}  {m['from']}")
        print(f"  {m['subject']}")

CLI
---
    python3 -m plugins.read_all_emails --limit 15
    python3 -m plugins.read_all_emails --unread
"""
from plugins._imap import imap_connect, parse_message


def list_recent(limit: int = 20, unread_only: bool = False,
                body_chars: int = 500) -> list:
    m = imap_connect()
    try:
        criterion = "UNSEEN" if unread_only else "ALL"
        _, data = m.search(None, criterion)
        ids = data[0].split()
        if not ids:
            return []

        out = []
        for mid in ids[-limit:][::-1]:  # latest first
            _, msg_data = m.fetch(mid, "(RFC822)")
            info = parse_message(msg_data[0][1])
            if len(info["body"]) > body_chars:
                info["body"] = info["body"][:body_chars] + "…"
            out.append(info)
        return out
    finally:
        m.logout()


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="List recent inbox messages")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--unread", action="store_true", help="Only unread (UNSEEN) messages")
    p.add_argument("--body-chars", type=int, default=300)
    args = p.parse_args()

    msgs = list_recent(limit=args.limit, unread_only=args.unread, body_chars=args.body_chars)
    if not msgs:
        print("(no messages)")
    for m in msgs:
        print(f"[{m['date']}]")
        print(f"  From    : {m['from']}")
        print(f"  Subject : {m['subject']}")
        if m["body"]:
            snippet = m["body"].splitlines()[0][:200]
            print(f"  Preview : {snippet}")
        print()
