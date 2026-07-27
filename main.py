import logging
import os
import time
from typing import Iterable, Optional, Dict, Any, List
try:
    import markdown
except ImportError:
    markdown = None
try:
    import gspread
    import pandas as pd
except ImportError:
    gspread = None
    pd = None
try:
    import resend
except ImportError:
    resend = None
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class BulkMailer:
    """
    Bulk Mailer engine using Resend API.
    Supports sending to direct lists/arrays of email addresses or fetching recipients from Google Sheets.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
        sheet_id: Optional[str] = None,
        worksheet_name: Optional[str] = None,
        credentials_file: str = "./data/credentials.json"
    ):
        self.api_key = api_key or os.getenv("RESEND_API_KEY")
        self.from_email = from_email or os.getenv("FROM_EMAIL", "onboarding@resend.dev")
        self.sheet_id = sheet_id or os.getenv("SHEET_ID")
        self.worksheet_name = worksheet_name or os.getenv("WORKSHEET_NAME", "Sheet1")
        self.credentials = credentials_file

        if self.api_key:
            if resend:
                resend.api_key = self.api_key
        else:
            logging.warning("RESEND_API_KEY is not set. Emails will fail to send until an API key is provided.")

        self.client = None
        self._connect_google_sheets()

    def _connect_google_sheets(self):
        """Attempts to initialize the gspread service account client."""
        if gspread is None:
            logging.info("gspread module not installed. Google Sheets integration disabled.")
            return

        if os.path.exists(self.credentials):
            try:
                self.client = gspread.service_account(filename=self.credentials)
                logging.info("Google Sheets client initialized successfully.")
            except Exception as e:
                logging.warning(f"Google Sheets authentication disabled: {e}")
        else:
            logging.info(f"Google Sheets credentials file not found at '{self.credentials}'. Sheets integration will require manual client or setup.")

    @staticmethod
    def load_content_from_file(file_path: str) -> str:
        """
        Loads message content from an HTML or Markdown file.
        Converts Markdown to HTML automatically if the file has a .md extension.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Content file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if file_path.endswith(".md"):
            if markdown:
                return markdown.markdown(content)
            else:
                logging.warning("Markdown module not installed. Returning raw markdown text.")
                return f"<pre>{content}</pre>"
        return content

    def send_email(self, email: str, subject: str, html: str) -> Dict[str, Any]:
        """
        Sends a single email using the Resend API.
        """
        if resend is None:
            raise RuntimeError("The 'resend' Python library is not installed. Please run: pip install resend")

        if not self.api_key:
            raise ValueError("Resend API key is missing. Set RESEND_API_KEY in environment or pass to BulkMailer.")

        params = {
            "from": self.from_email,
            "to": [email],
            "subject": subject,
            "html": html
        }
        return resend.Emails.send(params)

    def send(
        self,
        emails: Iterable[str],
        subject: str,
        html: Optional[str] = None,
        markdown_text: Optional[str] = None,
        delay_seconds: float = 0.2
    ) -> Dict[str, Any]:
        """
        Sends bulk emails to an iterable (list/array/tuple) of email addresses.
        Accepts raw HTML or Markdown content.
        """
        if html is None and markdown_text is not None:
            if markdown:
                html = markdown.markdown(markdown_text)
            else:
                html = f"<p>{markdown_text}</p>"

        if not html:
            raise ValueError("Must provide either 'html' or 'markdown_text' email content.")

        # Clean and deduplicate recipient emails while preserving order
        unique_emails: List[str] = []
        for e in emails:
            cleaned = str(e).strip()
            if cleaned and cleaned not in unique_emails:
                unique_emails.append(cleaned)

        total = len(unique_emails)
        logging.info(f"Starting bulk email send to {total} recipient(s)...")

        success_count = 0
        failed_count = 0
        successful_emails = []
        failed_emails = []

        for index, email in enumerate(unique_emails, start=1):
            try:
                response = self.send_email(email=email, subject=subject, html=html)
                email_id = response.get("id") if isinstance(response, dict) else str(response)
                logging.info(f"[{index}/{total}] ✓ Sent -> {email} (ID: {email_id})")
                success_count += 1
                successful_emails.append(email)
            except Exception as e:
                logging.error(f"[{index}/{total}] ✗ Failed -> {email}: {e}")
                failed_count += 1
                failed_emails.append({"email": email, "error": str(e)})

            if delay_seconds > 0 and index < total:
                time.sleep(delay_seconds)

        logging.info("-" * 50)
        logging.info(f"Bulk Send Completed. Total: {total} | Success: {success_count} | Failed: {failed_count}")
        logging.info("-" * 50)

        return {
            "total": total,
            "success": success_count,
            "failed": failed_count,
            "successful_emails": successful_emails,
            "failed_emails": failed_emails
        }

    def send_from_list(
        self,
        emails: Iterable[str],
        subject: str,
        html: Optional[str] = None,
        markdown_text: Optional[str] = None,
        delay_seconds: float = 0.2
    ) -> Dict[str, Any]:
        """
        Alias for sending to an array/list of email addresses.
        """
        return self.send(
            emails=emails,
            subject=subject,
            html=html,
            markdown_text=markdown_text,
            delay_seconds=delay_seconds
        )

    def get_sheet_emails(
        self,
        sheet_id: Optional[str] = None,
        worksheet_name: Optional[str] = None,
        column_name: str = "Email"
    ) -> List[str]:
        """
        Retrieves a list of recipient emails from Google Sheets.
        """
        target_sheet_id = sheet_id or self.sheet_id
        target_worksheet = worksheet_name or self.worksheet_name

        if not target_sheet_id:
            raise ValueError("Google Sheet ID is not provided. Set SHEET_ID in environment or pass sheet_id.")

        if self.client is None:
            # Try re-connecting in case credentials were added
            self._connect_google_sheets()
            if self.client is None:
                raise RuntimeError(
                    f"Google Sheets client unavailable. Ensure '{self.credentials}' exists and is valid."
                )

        spreadsheet = self.client.open_by_key(target_sheet_id)
        worksheet = spreadsheet.worksheet(target_worksheet)
        records = worksheet.get_all_records()

        df = pd.DataFrame(records)
        df.columns = df.columns.astype(str).str.strip()

        if column_name not in df.columns:
            available_cols = list(df.columns)
            raise ValueError(f"Column '{column_name}' not found in sheet. Available columns: {available_cols}")

        emails = (
            df[column_name]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        # Filter out invalid / blank entries
        valid_emails = [e for e in emails if "@" in e]

        logging.info(f"Retrieved {len(valid_emails)} email address(es) from Google Sheet (column: '{column_name}').")
        return valid_emails

    def send_from_sheet(
        self,
        subject: str,
        html: Optional[str] = None,
        markdown_text: Optional[str] = None,
        sheet_id: Optional[str] = None,
        worksheet_name: Optional[str] = None,
        column_name: str = "Email",
        delay_seconds: float = 0.2
    ) -> Dict[str, Any]:
        """
        Fetches recipient email array from Google Sheet and sends emails in bulk.
        """
        emails = self.get_sheet_emails(
            sheet_id=sheet_id,
            worksheet_name=worksheet_name,
            column_name=column_name
        )

        return self.send(
            emails=emails,
            subject=subject,
            html=html,
            markdown_text=markdown_text,
            delay_seconds=delay_seconds
        )


if __name__ == "__main__":
    print("BulkMailer engine module loaded.")
    print("Example usage with array:")
    print("  mailer = BulkMailer()")
    print("  mailer.send_from_list(['test@example.com'], subject='Hello', markdown_text='# Welcome!')")
