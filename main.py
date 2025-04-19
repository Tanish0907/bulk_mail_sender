import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import logging
from mail import mail
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Set up Google Sheets API credentials
class main:
    def __init__(self, sheet_id, sheet_name):
        self.sheet_id = sheet_id
        self.sheet_name = sheet_name
        self.credentials_path = "./data/credentials.json"
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, self.scope)
        self.client = gspread.authorize(self.creds)
    def get_sheet_data(self):
        try:
            sheet = self.client.open(self.sheet_name)
            worksheet = sheet.worksheet("sheet1")
            data = worksheet.get_all_records()
            self.df = pd.DataFrame(data)
            self.df.columns = self.df.columns.str.strip()
            logging.info("Data retrieved successfully.")
            # return self.df
        except Exception as e:
            logging.error(f"Error retrieving data from sheet: {e}")
            exit()
    def get_email_data(self):
        try:
            self.get_sheet_data()
            self.df = self.df.dropna()
            # print(self.df)
            emails = list(self.df['Email'])
            names = list(self.df['Name'])
            bool = list(self.df['test'])
            self.mail_data=list(zip(emails, names, bool))
            logging.info("Email data retrieved successfully.")
            print(self.mail_data)
        except Exception as e:
            logging.error(f"Error retrieving email data: {e}")
            exit()
    def send_mail(self):
        self.get_email_data()
        logging.info("Email data retrieved successfully.")
        try:
            for email, name, bool in self.mail_data:
                if bool == "Yes":
                    mail(email)
                    logging.info(f"Email sent to {name} at {email}")
                else:
                    logging.info(f"Email not sent to {name} at {email}")
        except Exception as e:
            logging.error(f"Error sending email: {e}")
            exit()

sheet_id = "1euZhdelNxgdj85-smtnDc2TxvkEWkEHAoPtAYFPWuG0"
sheet_name = "test(Responses)"
sheet = main(sheet_id, sheet_name)
sheet.send_mail()
# print(emails,names)