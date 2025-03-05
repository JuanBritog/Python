import os
import pandas as pd
from resourcesMail2 import create_connectionMail, read_properties
from resourcesDBPanda import create_connection
import logging
from Job import Job
from contextlib import closing

class MailQueryAllegatoExcel(Job):
    def run(self):
        try:
            self.logger.info(f"Running job: {self.NomeJob}")
            
            if not os.path.exists(self.excel_path):
                os.makedirs(self.excel_path)
                self.logger.info(f"Created directory: {self.excel_path}")
            
            query = self.read_query(self.query_path)
            self.logger.info(f"Query to be executed: {query}")
            is_html = self.is_html if self.is_html is not None else False
            
            with closing(create_connection(self.config_path_db)) as connection:
                self.logger.info("Database connection established successfully.")
                try:
                    df = pd.read_sql(query, connection)
                    self.logger.info(f"Query executed successfully. DataFrame shape: {df.shape}")
                except pd.io.sql.DatabaseError as e:
                    self.logger.error(f"Database error: {e}")
                    print(f"Database error: {e}")
                    return
            
            if df.empty:
                self.logger.info("Query returned no rows, sending email without attachment.")
                self.body += "\n\nNessun record trovato."
                properties_mail = read_properties(self.config_path_mail)
                emailFrom = properties_mail['emailFrom']
                emailReplay = properties_mail['emailReplay']
                smtpServer = properties_mail['smtpServer']
                create_connectionMail(smtpServer,emailFrom ,emailReplay, self.subject, self.body, self.to_email, self.cc_email,is_html=is_html)
                self.logger.info("Email sent successfully.")
                print("Email sent successfully.") 
                return
            
            excel_path = os.path.join(self.excel_path, self.file_excel)
            df.to_excel(excel_path, index=False)
            self.logger.info("Query results saved to Excel.")
            
            properties_mail = read_properties(self.config_path_mail)
            emailFrom = properties_mail['emailFrom']
            emailReplay = properties_mail['emailReplay']
            smtpServer = properties_mail['smtpServer']
            create_connectionMail(smtpServer, emailFrom,emailReplay, self.subject, self.body, self.to_email, self.cc_email, [excel_path],is_html=is_html)
            self.logger.info("Email with attachment sent successfully.")
            print("Email sent successfully.")
        
        except Exception as e:
            self.logger.error(f"Error during job execution: {e}")
            print(f"Error during job execution: {e}")
