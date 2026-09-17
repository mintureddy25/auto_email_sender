"""
plugins/download_attachments.py

Download file attachments from the latest email matching a sender (and
optionally a subject substring) into a target directory.

When to use
-----------
A recruiter sent a form (xlsx/doc/pdf) you need to fill and return.
Use this to pull that attachment to disk so it can be edited and re-sent
via reply_email.

Args
----
sender (str)        : sender email to match (IMAP FROM search)
out_dir (str)       : directory to save attachments into (created if missing)
subject_sub (str)   : optional subject substring filter (case-insensitive)

Returns
-------
list[str] : absolute paths of the files written

CLI
---
    python3 -m plugins.download_attachments --sender x@y.com --out /tmp/forms
"""
import os

from plugins._imap import imap_connect, decode_mime
import email as _email


def download_attachments(sender: str, out_dir: str,
                         subject_sub: str = None) -> list:
    os.makedirs(out_dir, exist_ok=True)
    m = imap_connect()
    try:
        _, data = m.search(None, "FROM", f'"{sender}"')
        ids = data[0].split()
        if not ids:
            raise LookupError(f"No email found from {sender}")
        target_id = None
        if subject_sub:
            for i in reversed(ids):
                _, md = m.fetch(i, "(RFC822)")
                msg = _email.message_from_bytes(md[0][1])
                if subject_sub.lower() in decode_mime(msg.get("Subject")).lower():
                    target_id = i
                    break
            if target_id is None:
                raise LookupError(f"No email from {sender} with subject ~ {subject_sub!r}")
        else:
            target_id = ids[-1]
        _, md = m.fetch(target_id, "(RFC822)")
        msg = _email.message_from_bytes(md[0][1])
    finally:
        m.logout()

    saved = []
    for part in msg.walk():
        disp = str(part.get("Content-Disposition", ""))
        fname = part.get_filename()
        if "attachment" not in disp.lower() and not fname:
            continue
        if not fname:
            continue
        fname = decode_mime(fname)
        payload = part.get_payload(decode=True)
        if payload is None:
            continue
        path = os.path.join(out_dir, fname)
        with open(path, "wb") as f:
            f.write(payload)
        saved.append(os.path.abspath(path))
    return saved


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Download attachments from the latest email by sender.")
    p.add_argument("--sender", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--subject", default=None)
    a = p.parse_args()
    for fp in download_attachments(a.sender, a.out, a.subject):
        print(fp)
