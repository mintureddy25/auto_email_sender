# plugins/

Self-contained email plugins. Each file has a top-level docstring describing
what it does, when to use it, args, returns, and a usage example — so an AI
agent (or human) can pick the right one without reading the implementation.

## Index

| Plugin | Function | One-liner |
|---|---|---|
| `send_email.py` | `send_email(to, subject, body, ...)` | Send a fresh standalone email |
| `reply_email.py` | `reply_to_latest_from(sender, body, ...)` | Send a THREADED reply (same Gmail conversation) |
| `read_email.py` | `read_latest_from(sender)` / `read_by_subject(substring)` | Fetch a SINGLE email |
| `read_all_emails.py` | `list_recent(limit, unread_only)` | List recent inbox messages |

## Shared internals

- `_smtp.py` — SMTP send (multipart/alternative: plain + HTML). Renders
  `**bold**`, `*italic*`, bare URLs. Used by send/reply plugins.
- `_imap.py` — IMAP connect + message parser. Used by read/reply plugins.

## Credentials

All plugins read from `auto_email_sender/.env` via `src.config`:

- `EMAIL_USER` — Gmail address (the sender + inbox owner)
- `EMAIL_PASSWORD` — Gmail app password (works for BOTH SMTP send and IMAP read)
- `EMAIL_SMTP_SERVER` / `EMAIL_SMTP_PORT`
- IMAP host is hardcoded to `imap.gmail.com:993`

Resume path comes from `src.config.RESUME_PDF` (defaults to
`auto_email_sender/assets/saitejareddyresume.pdf`).

## CLI usage

Every plugin can also be run directly from the command line:

```
python3 -m plugins.send_email       --to x@y.com --subject "Hi" --body "..."
python3 -m plugins.reply_email      --sender recruiter@co.com --body "..."
python3 -m plugins.read_email       --from recruiter@co.com
python3 -m plugins.read_email       --subject "Full Stack"
python3 -m plugins.read_all_emails  --limit 10 --unread
```

Always run from the `auto_email_sender/` directory so `src.config` imports resolve.

## Programmatic example

```python
from plugins.read_email import read_latest_from
from plugins.reply_email import reply_to_latest_from

# 1. See what the recruiter asked
msg = read_latest_from("recruiter@acme.com")
print(msg["subject"], "\n", msg["body"])

# 2. Send a threaded reply
reply_to_latest_from(
    sender="recruiter@acme.com",
    body=(
        "Hi,\n\n"
        "Thanks for reaching out. Details below:\n\n"
        "**Current CTC**: 11.5 LPA\n"
        "**Notice Period**: Immediate\n"
    ),
)
```
