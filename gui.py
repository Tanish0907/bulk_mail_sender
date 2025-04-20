import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
import sys
from main import main

# Custom logging handler to capture logs for display in the GUI
class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        logging.Handler.__init__(self)
        self.text_widget = text_widget
        
    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')
        self.text_widget.after(0, append)

class EmailSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Sender from Google Sheets")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Input Settings", padding="10")
        input_frame.pack(fill=tk.X, pady=10)
        
        # Sender Email
        ttk.Label(input_frame, text="Sender Email:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sender_email = ttk.Entry(input_frame, width=50)
        self.sender_email.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.sender_email.insert(0, "sharmatanish097654@gmail.com")  # Default value from mail.py
        
        # Password
        ttk.Label(input_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password = ttk.Entry(input_frame, width=50, show="*")
        self.password.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.password.insert(0, "aojj tmmw bplp nden ")  # Default value from mail.py
        
        # Google Sheets ID
        ttk.Label(input_frame, text="Google Sheets ID:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.sheet_id = ttk.Entry(input_frame, width=50)
        self.sheet_id.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.sheet_id.insert(0, "1euZhdelNxgdj85-smtnDc2TxvkEWkEHAoPtAYFPWuG0")  # Default value from main.py
        
        # Sheet Name
        ttk.Label(input_frame, text="Sheet Name:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.sheet_name = ttk.Entry(input_frame, width=50)
        self.sheet_name.grid(row=3, column=1, sticky=tk.W, pady=5) 
        self.sheet_name.insert(0, "test(Responses)")  # Default value from main.py
        
        # Worksheet Name
        ttk.Label(input_frame, text="Worksheet Name:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.worksheet_name = ttk.Entry(input_frame, width=50)
        self.worksheet_name.grid(row=4, column=1, sticky=tk.W, pady=5)
        self.worksheet_name.insert(0, "sheet1")  # Default value from main.py
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.send_button = ttk.Button(button_frame, text="Send Emails", command=self.send_emails)
        self.send_button.pack(side=tk.RIGHT, padx=5)
        
        self.preview_button = ttk.Button(button_frame, text="Preview Data", command=self.preview_data)
        self.preview_button.pack(side=tk.RIGHT, padx=5)
        
        # Status indicators
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.progress_bar = ttk.Progressbar(status_frame, mode="indeterminate")
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Logging section
        log_frame = ttk.LabelFrame(main_frame, text="Log Output", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_display = scrolledtext.ScrolledText(log_frame, state='disabled', height=15)
        self.log_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure logging to display in the text widget
        self.setup_logging()
    
    def setup_logging(self):
        # Create text handler
        text_handler = TextHandler(self.log_display)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        text_handler.setFormatter(formatter)
        
        # Add the handler to the logger
        root_logger.addHandler(text_handler)
    
    def update_email_sender(self):
        """Updates the mail.py file with the new sender email and password"""
        try:
            with open('mail.py', 'r') as file:
                content = file.read()
                
            # Update sender email
            sender_pattern = "SENDER = '.*'"
            updated_content = content.replace(
                content.split("SENDER = ")[1].split("\n")[0], 
                f"'{self.sender_email.get()}'"
            )
            
            # Update password
            password_pattern = "PASSWORD = '.*'"
            updated_content = updated_content.replace(
                updated_content.split("PASSWORD = ")[1].split("\n")[0], 
                f"'{self.password.get()}'"
            )
            
            with open('mail.py', 'w') as file:
                file.write(updated_content)
                
            logging.info("Updated sender email configuration")
            return True
        except Exception as e:
            logging.error(f"Failed to update sender email: {e}")
            return False
    
    def preview_data(self):
        """Retrieves data from the sheet and shows a preview"""
        try:
            self.status_label.config(text="Retrieving data...")
            self.progress_bar.start()
            
            # Check if inputs are provided
            if not self.validate_inputs():
                return
            
            # Create an instance of the main class
            sheet_handler = main(
                sheet_id=self.sheet_id.get(), 
                sheet_name=self.sheet_name.get()
            )
            
            # Get data
            sheet_handler.get_email_data()
            
            # Display the data
            if hasattr(sheet_handler, 'mail_data') and sheet_handler.mail_data:
                preview_window = tk.Toplevel(self.root)
                preview_window.title("Data Preview")
                preview_window.geometry("600x400")
                
                # Create a treeview to display the data
                columns = ("Email", "Name", "Send Email")
                tree = ttk.Treeview(preview_window, columns=columns, show="headings")
                
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=150)
                
                for i, (email, name, send) in enumerate(sheet_handler.mail_data):
                    tree.insert("", tk.END, values=(email, name, send))
                
                tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                summary_label = ttk.Label(
                    preview_window, 
                    text=f"Total records: {len(sheet_handler.mail_data)}, "
                         f"Emails to send: {sum(1 for _, _, send in sheet_handler.mail_data if send == 'Yes')}"
                )
                summary_label.pack(pady=10)
            else:
                messagebox.showinfo("Preview", "No data found or unable to retrieve data")
        except Exception as e:
            logging.error(f"Error previewing data: {e}")
            messagebox.showerror("Error", f"Failed to preview data: {str(e)}")
        finally:
            self.progress_bar.stop()
            self.status_label.config(text="Ready")
    
    def validate_inputs(self):
        """Validate that all required inputs are provided"""
        if not self.sender_email.get():
            messagebox.showerror("Input Error", "Sender email is required")
            return False
        
        if not self.password.get():
            messagebox.showerror("Input Error", "Email password is required")
            return False
            
        if not self.sheet_id.get():
            messagebox.showerror("Input Error", "Google Sheets ID is required")
            return False
            
        if not self.sheet_name.get():
            messagebox.showerror("Input Error", "Sheet Name is required")
            return False
            
        if not self.worksheet_name.get():
            messagebox.showerror("Input Error", "Worksheet Name is required")
            return False
            
        return True
    
    def send_emails(self):
        """Send emails based on the Google Sheet data"""
        try:
            if not self.validate_inputs():
                return
            
            # Confirm before sending
            if not messagebox.askyesno("Confirm", "Are you sure you want to send emails?"):
                return
            
            self.status_label.config(text="Sending emails...")
            self.progress_bar.start()
            self.send_button.config(state=tk.DISABLED)
            
            # Update the sender email in mail.py
            if not self.update_email_sender():
                messagebox.showerror("Error", "Failed to update sender email configuration")
                return
            
            # Create and run the email sender
            sheet_handler = main(
                sheet_id=self.sheet_id.get(), 
                sheet_name=self.sheet_name.get()
            )
            
            # Override the worksheet name if it's different from the default
            sheet_handler.worksheet_name = self.worksheet_name.get()
            
            # Send emails
            sheet_handler.send_mail()
            
            messagebox.showinfo("Success", "Emails have been sent successfully!")
            
        except Exception as e:
            logging.error(f"Error sending emails: {e}")
            messagebox.showerror("Error", f"Failed to send emails: {str(e)}")
        finally:
            self.progress_bar.stop()
            self.status_label.config(text="Ready")
            self.send_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    # Set up the Tkinter root
    root = tk.Tk()
    app = EmailSenderApp(root)
    root.mainloop()