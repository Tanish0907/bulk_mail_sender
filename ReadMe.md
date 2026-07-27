# 📧 Resend Bulk Mail Sender

A powerful Python application and desktop GUI for bulk emailing using the **Resend API**. Supports sending to **direct arrays/lists of email addresses** as well as automatically fetching recipients from **Google Sheets**.

---

## 🔧 Key Features

- **Resend API Integration**: Lightning-fast, reliable bulk transactional email delivery.
- **Dual Input Modes**:
  1. **Python Array / List**: Pass any python list or text array of email addresses.
  2. **Google Sheets Integration**: Read recipient lists directly from Google Sheets using `gspread`.
- **Rich Content Support**: Load HTML templates (`.html`) or Markdown templates (`.md`) seamlessly.
- **Rate Limiting & Logging**: Automatic deduplication, clean console/UI logs, rate limit delays, and structured summary reporting.
- **Desktop GUI App**: Full-featured Tkinter desktop application with live logs and interactive recipient previews.

---

## 📁 Project Structure

```
.
├── main.py                # Core BulkMailer engine class
├── gui.py                 # Tkinter Desktop GUI application
├── example_array.py       # Example: Send to direct email array
├── example_sheets.py      # Example: Send from Google Sheets
├── compose.html           # HTML Email Template
├── compose.md             # Markdown Email Template
├── .env                   # Environment secrets (Resend API Key, Sender, Sheet ID)
├── data/
│   └── credentials.json   # Google service account credentials
└── ReadMe.md
```

---

## 🚀 Environment Setup

### 1. Configure `.env`
Create or update your `.env` file with your Resend API credentials and defaults:

```env
RESEND_API_KEY=re_your_resend_api_key_here
FROM_EMAIL=onboarding@resend.dev
SHEET_ID=your_google_sheet_id_here
WORKSHEET_NAME=Sheet1
```

> [!NOTE]
> If using `onboarding@resend.dev` as `FROM_EMAIL` (Resend's default test sender), emails can only be delivered to your registered Resend account email address until you verify a custom domain.

---

## 📨 Usage Examples

### Option 1: Send to an Array / List of Email Addresses

You can pass a Python list or array of emails directly to `send_from_list()`:

```python
from main import BulkMailer

mailer = BulkMailer()

# Array of email recipients
recipients = [
    "alice@example.com",
    "bob@example.com",
    "charlie@example.com"
]

# Load HTML or Markdown email template
html_content = mailer.load_content_from_file("compose.html")

# Send bulk emails
results = mailer.send_from_list(
    emails=recipients,
    subject="Welcome to Our Product!",
    html=html_content,
    delay_seconds=0.5
)

print(f"Sent {results['success']} out of {results['total']} emails.")
```

Run the example script:
```bash
python example_array.py
```

---

### Option 2: Send from Google Sheets

Ensure `./data/credentials.json` contains your Google Service Account credentials and the sheet is shared with your service account email.

```python
from main import BulkMailer

mailer = BulkMailer()

html_content = mailer.load_content_from_file("compose.html")

results = mailer.send_from_sheet(
    subject="Monthly Newsletter",
    html=html_content,
    column_name="Email",  # Header of email column in sheet
    delay_seconds=0.5
)

print(f"Sent {results['success']} emails from Google Sheets.")
```

Run the example script:
```bash
python example_sheets.py
```

---

## 🖥️ Desktop GUI App

Launch the graphical interface:

```bash
python gui.py
```

### Features in GUI:
- Switch between **Array / Manual List** tab and **Google Sheets** tab.
- Preview recipient counts before sending.
- Browse and load `.html` or `.md` files as email templates.
- View real-time output logs and progress status.

---

## 📋 Requirements

Install required dependencies via `pip`:

```bash
pip install resend gspread pandas python-dotenv markdown
```
