import logging
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from main import BulkMailer

# ----------------------------------------------------------
# Custom GUI Logging Handler
# ----------------------------------------------------------
class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')
        self.text_widget.after(0, append)


# ----------------------------------------------------------
# Main GUI Application
# ----------------------------------------------------------
class ResendBulkMailerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Resend Bulk Email Sender")
        self.root.geometry("850x700")
        self.root.minsize(750, 600)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Main Layout Frame
        main_frame = ttk.Frame(root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Resend & Sender API Configuration
        config_frame = ttk.LabelFrame(main_frame, text="API & Sender Settings", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(config_frame, text="Resend API Key:").grid(row=0, column=0, sticky=tk.W, pady=3, padx=5)
        self.api_key_entry = ttk.Entry(config_frame, width=55, show="*")
        self.api_key_entry.grid(row=0, column=1, sticky=tk.W, pady=3, padx=5)
        self.api_key_entry.insert(0, os.getenv("RESEND_API_KEY", ""))

        ttk.Label(config_frame, text="From Email:").grid(row=1, column=0, sticky=tk.W, pady=3, padx=5)
        self.from_email_entry = ttk.Entry(config_frame, width=55)
        self.from_email_entry.grid(row=1, column=1, sticky=tk.W, pady=3, padx=5)
        self.from_email_entry.insert(0, os.getenv("FROM_EMAIL", "onboarding@resend.dev"))

        # 2. Recipient Input Source (Notebook / Tabs)
        recipients_frame = ttk.LabelFrame(main_frame, text="Recipient Source Selection", padding="10")
        recipients_frame.pack(fill=tk.X, pady=(0, 10))

        self.notebook = ttk.Notebook(recipients_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Array / Direct Email List
        self.tab_array = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_array, text="📧 Array / Manual List")

        ttk.Label(self.tab_array, text="Enter Email Addresses (comma, space, or line separated):").pack(anchor=tk.W, pady=(0, 5))
        self.array_text = scrolledtext.ScrolledText(self.tab_array, height=6)
        self.array_text.pack(fill=tk.BOTH, expand=True)
        self.array_text.insert(tk.END, "test1@example.com, test2@example.com\nuser@example.com")

        # Tab 2: Google Sheets
        self.tab_sheets = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_sheets, text="📊 Google Sheets")

        ttk.Label(self.tab_sheets, text="Google Sheet ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sheet_id_entry = ttk.Entry(self.tab_sheets, width=50)
        self.sheet_id_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        self.sheet_id_entry.insert(0, os.getenv("SHEET_ID", ""))

        ttk.Label(self.tab_sheets, text="Worksheet Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.worksheet_name_entry = ttk.Entry(self.tab_sheets, width=50)
        self.worksheet_name_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        self.worksheet_name_entry.insert(0, os.getenv("WORKSHEET_NAME", "Sheet1"))

        ttk.Label(self.tab_sheets, text="Email Column Header:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.column_name_entry = ttk.Entry(self.tab_sheets, width=50)
        self.column_name_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        self.column_name_entry.insert(0, "Email")

        # 3. Email Content Section
        content_frame = ttk.LabelFrame(main_frame, text="Email Composition", padding="10")
        content_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(content_frame, text="Subject Line:").grid(row=0, column=0, sticky=tk.W, pady=3, padx=5)
        self.subject_entry = ttk.Entry(content_frame, width=60)
        self.subject_entry.grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=3, padx=5)
        self.subject_entry.insert(0, "Important Update")

        ttk.Label(content_frame, text="Template File:").grid(row=1, column=0, sticky=tk.W, pady=3, padx=5)
        self.template_path_entry = ttk.Entry(content_frame, width=45)
        self.template_path_entry.grid(row=1, column=1, sticky=tk.W, pady=3, padx=5)
        if os.path.exists("compose.html"):
            self.template_path_entry.insert(0, "compose.html")

        self.browse_button = ttk.Button(content_frame, text="Browse...", command=self.browse_template)
        self.browse_button.grid(row=1, column=2, sticky=tk.W, pady=3, padx=5)

        # 4. Action Controls
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=5)

        self.preview_button = ttk.Button(action_frame, text="Preview Recipients", command=self.preview_recipients)
        self.preview_button.pack(side=tk.LEFT, padx=5)

        self.send_button = ttk.Button(action_frame, text="🚀 Send Bulk Emails", command=self.start_send_thread)
        self.send_button.pack(side=tk.RIGHT, padx=5)

        # 5. Progress Indicator
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)

        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.pack(side=tk.RIGHT, padx=5)

        # 6. Real-time Console Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Execution Logs", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.log_display = scrolledtext.ScrolledText(log_frame, state='disabled', height=10)
        self.log_display.pack(fill=tk.BOTH, expand=True)

        self.setup_logging()

    def setup_logging(self):
        handler = TextHandler(self.log_display)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
        handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

    def browse_template(self):
        file_path = filedialog.askopenfilename(
            title="Select Email Template File",
            filetypes=[("HTML/Markdown files", "*.html *.md *.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.template_path_entry.delete(0, tk.END)
            self.template_path_entry.insert(0, file_path)

    def get_parsed_array_emails(self):
        raw_text = self.array_text.get("1.0", tk.END)
        # Replace commas/newlines with space and split
        tokens = raw_text.replace(',', ' ').replace('\n', ' ').split()
        emails = [t.strip() for t in tokens if '@' in t]
        return emails

    def preview_recipients(self):
        current_tab_index = self.notebook.index(self.notebook.select())
        if current_tab_index == 0:
            # Array mode
            emails = self.get_parsed_array_emails()
            messagebox.showinfo("Recipient Preview", f"Parsed {len(emails)} valid recipient email address(es) from text list:\n\n" + "\n".join(emails[:10]) + ("\n..." if len(emails) > 10 else ""))
        else:
            # Google Sheets mode
            sheet_id = self.sheet_id_entry.get().strip()
            worksheet_name = self.worksheet_name_entry.get().strip()
            column_name = self.column_name_entry.get().strip()

            if not sheet_id:
                messagebox.showwarning("Missing Info", "Please enter a Google Sheet ID.")
                return

            self.status_label.config(text="Fetching Google Sheet...")
            self.progress_bar.start()

            def fetch():
                try:
                    mailer = BulkMailer(
                        api_key=self.api_key_entry.get().strip(),
                        from_email=self.from_email_entry.get().strip(),
                        sheet_id=sheet_id,
                        worksheet_name=worksheet_name
                    )
                    emails = mailer.get_sheet_emails(column_name=column_name)
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Google Sheets Preview",
                        f"Found {len(emails)} recipient email address(es) in column '{column_name}':\n\n" +
                        "\n".join(emails[:10]) + ("\n..." if len(emails) > 10 else "")
                    ))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch from Google Sheet: {e}"))
                finally:
                    self.root.after(0, lambda: self.progress_bar.stop())
                    self.root.after(0, lambda: self.status_label.config(text="Ready"))

            threading.Thread(target=fetch, daemon=True).start()

    def start_send_thread(self):
        api_key = self.api_key_entry.get().strip()
        from_email = self.from_email_entry.get().strip()
        subject = self.subject_entry.get().strip()
        template_file = self.template_path_entry.get().strip()

        if not api_key:
            messagebox.showerror("Missing API Key", "Please provide a valid Resend API Key.")
            return

        if not subject:
            messagebox.showerror("Missing Subject", "Please enter an email subject line.")
            return

        if not template_file or not os.path.exists(template_file):
            messagebox.showerror("Missing Template", f"Template file '{template_file}' not found.")
            return

        if not messagebox.askyesno("Confirm Send", f"Are you sure you want to send bulk emails with subject '{subject}'?"):
            return

        self.send_button.config(state=tk.DISABLED)
        self.progress_bar.start()
        self.status_label.config(text="Sending emails...")

        def run_send():
            try:
                mailer = BulkMailer(api_key=api_key, from_email=from_email)
                html_content = mailer.load_content_from_file(template_file)

                current_tab_index = self.notebook.index(self.notebook.select())

                if current_tab_index == 0:
                    # Send to Array
                    emails = self.get_parsed_array_emails()
                    if not emails:
                        raise ValueError("No valid email addresses found in the array list.")

                    res = mailer.send_from_list(
                        emails=emails,
                        subject=subject,
                        html=html_content,
                        delay_seconds=0.5
                    )
                else:
                    # Send to Google Sheet
                    sheet_id = self.sheet_id_entry.get().strip()
                    worksheet_name = self.worksheet_name_entry.get().strip()
                    column_name = self.column_name_entry.get().strip()

                    res = mailer.send_from_sheet(
                        subject=subject,
                        html=html_content,
                        sheet_id=sheet_id,
                        worksheet_name=worksheet_name,
                        column_name=column_name,
                        delay_seconds=0.5
                    )

                self.root.after(0, lambda: messagebox.showinfo(
                    "Send Completed",
                    f"Bulk send completed!\nTotal: {res['total']}\nSuccess: {res['success']}\nFailed: {res['failed']}"
                ))

            except Exception as e:
                logging.error(f"Execution Error: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed during bulk send: {e}"))
            finally:
                self.root.after(0, lambda: self.progress_bar.stop())
                self.root.after(0, lambda: self.status_label.config(text="Ready"))
                self.root.after(0, lambda: self.send_button.config(state=tk.NORMAL))

        threading.Thread(target=run_send, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = ResendBulkMailerApp(root)
    root.mainloop()