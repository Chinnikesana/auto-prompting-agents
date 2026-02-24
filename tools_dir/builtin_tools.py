"""
Built-in Tools — All pre-packaged tools consolidated in a single file.
LLM-generated tools are still stored as individual files in tools_dir/.

Tools:
  - web_search: DuckDuckGo search
  - web_scraper: URL content extraction
  - datetime_tool: Current date/time
  - read_file: Read file contents
  - write_file: Write/append to file
  - http_request: HTTP GET/POST
  - read_email: Read emails via IMAP
  - send_email: Send emails via SMTP
"""
from datetime import datetime
from core.config import Config


# ---------------------------------------------------------------------------
# Web Search
# ---------------------------------------------------------------------------
def web_search(query: str) -> str:
    """Search the web using DuckDuckGo and return top 5 results."""
    if Config.TOOL_TEST_MODE:
        return "Mock search results for: " + query

    try:
        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddgs:
            for i, r in enumerate(ddgs.text(query, max_results=5)):
                results.append(
                    f"{i+1}. {r.get('title', 'No title')}\n"
                    f"   URL: {r.get('href', 'N/A')}\n"
                    f"   {r.get('body', 'No snippet')}"
                )

        if not results:
            return "No results found for: " + query

        return "\n\n".join(results)

    except Exception as e:
        return f"Error performing web search: {str(e)}"


# ---------------------------------------------------------------------------
# Web Scraper
# ---------------------------------------------------------------------------
def web_scraper(url: str) -> str:
    """Fetch a URL and return the first 2000 characters of clean text content."""
    if Config.TOOL_TEST_MODE:
        return "Mock scraped content from: " + url

    try:
        import requests
        from bs4 import BeautifulSoup

        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (compatible; DynamicAgentCreator/1.0)"
        })
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean = "\n".join(lines)

        return clean[:2000]

    except Exception as e:
        return f"Error scraping URL: {str(e)}"


# ---------------------------------------------------------------------------
# DateTime
# ---------------------------------------------------------------------------
def datetime_tool() -> str:
    """Return the current date and time as a formatted string."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S (%A)")


# ---------------------------------------------------------------------------
# Read File
# ---------------------------------------------------------------------------
def read_file(file_path: str) -> str:
    """Read a file and return its content as a string."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


# ---------------------------------------------------------------------------
# Write File
# ---------------------------------------------------------------------------
def write_file(file_path: str, content: str, mode: str = "write") -> str:
    """Write or append content to a file. mode: 'write' or 'append'."""
    try:
        parent = os.path.dirname(file_path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        file_mode = "a" if mode == "append" else "w"
        with open(file_path, file_mode, encoding="utf-8") as f:
            f.write(content)

        return f"Successfully {'appended to' if mode == 'append' else 'wrote'} file: {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


# ---------------------------------------------------------------------------
# HTTP Request
# ---------------------------------------------------------------------------
def http_request(url: str, method: str = "GET", headers: dict = None,
                 body: dict = None) -> str:
    """Make an HTTP request and return the response text."""
    if Config.TOOL_TEST_MODE:
        return f"Mock HTTP {method} response from: {url}"

    try:
        import requests

        method = method.upper()
        kwargs = {"timeout": 30}
        if headers:
            kwargs["headers"] = headers
        if method == "POST" and body:
            kwargs["json"] = body

        resp = requests.request(method, url, **kwargs)

        result = f"Status: {resp.status_code}\n"
        try:
            result += json.dumps(resp.json(), indent=2)
        except Exception:
            result += resp.text[:2000]

        return result

    except Exception as e:
        return f"Error making HTTP request: {str(e)}"


# ---------------------------------------------------------------------------
# Read Email (IMAP)
# ---------------------------------------------------------------------------
def read_email(count: int = 5, folder: str = "INBOX") -> str:
    """Read recent emails from an IMAP mailbox. Returns the latest `count` emails."""
    if Config.TOOL_TEST_MODE:
        return f"Mock email: 1 unread message in {folder} — Subject: Test Email"

    try:
        import imaplib
        import email as email_lib
        from email.header import decode_header

        smtp_host = Config.EMAIL_SMTP_HOST
        # Derive IMAP host from SMTP host
        imap_host = smtp_host.replace("smtp.", "imap.")
        user = Config.EMAIL_SENDER
        password = Config.EMAIL_APP_PASSWORD

        if not user or not password:
            return "Error: EMAIL_SENDER and EMAIL_APP_PASSWORD must be set in .env"

        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(user, password)
        mail.select(folder)

        status, messages = mail.search(None, "ALL")
        if status != "OK":
            return "Error: Could not search mailbox"

        msg_ids = messages[0].split()
        if not msg_ids:
            return "No emails found."

        # Get the latest `count` emails
        latest_ids = msg_ids[-count:]
        results = []

        for mid in reversed(latest_ids):
            status, msg_data = mail.fetch(mid, "(RFC822)")
            if status != "OK":
                continue

            msg = email_lib.message_from_bytes(msg_data[0][1])

            subject = ""
            raw_subject = msg.get("Subject", "")
            decoded = decode_header(raw_subject)
            for part, charset in decoded:
                if isinstance(part, bytes):
                    subject += part.decode(charset or "utf-8", errors="replace")
                else:
                    subject += part

            sender = msg.get("From", "Unknown")
            date = msg.get("Date", "Unknown")

            # Extract plain text body
            body_text = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body_text = part.get_payload(decode=True).decode(
                            part.get_content_charset() or "utf-8", errors="replace"
                        )
                        break
            else:
                body_text = msg.get_payload(decode=True).decode(
                    msg.get_content_charset() or "utf-8", errors="replace"
                )

            results.append(
                f"From: {sender}\n"
                f"Date: {date}\n"
                f"Subject: {subject}\n"
                f"Body: {body_text[:300]}\n"
                f"{'─' * 40}"
            )

        mail.logout()
        return "\n\n".join(results) if results else "No emails found."

    except Exception as e:
        return f"Error reading email: {str(e)}"


# ---------------------------------------------------------------------------
# Send Email (SMTP)
# ---------------------------------------------------------------------------
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via SMTP using credentials from environment variables."""
    if Config.TOOL_TEST_MODE:
        return f"Mock email sent to {to} with subject: {subject}"

    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        sender = Config.EMAIL_SENDER
        password = Config.EMAIL_APP_PASSWORD
        smtp_host = Config.EMAIL_SMTP_HOST
        smtp_port = Config.EMAIL_SMTP_PORT

        if not sender or not password:
            return "Error: EMAIL_SENDER and EMAIL_APP_PASSWORD must be set in .env"

        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)

        return f"Email sent successfully to {to}"

    except Exception as e:
        return f"Error sending email: {str(e)}"
