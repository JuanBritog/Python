
import os
import pandas as pd
from resourcesMail2 import create_connectionMail, read_properties
from resourcesDBPanda import create_connection
import logging
import importlib.util
from tipoMails import tipoMails  

class Job:
    def __init__(self, params):
        self.NomeJob = params.get('NomeJob', None)
        self.tipoJobs = params.get('tipoJobs', None)
        self.query_path = params.get('query_path', None)
        self.config_path_db = params.get('config_path_db', None)
        self.config_path_mail = params.get('config_path_mail', None)
        self.config_path = params.get('config_path', None)        
        self.excel_path = params.get('excel_path', None)
        self.file_excel = params.get('file_excel', None)
        self.pdf_path = params.get('pdf_path', None)
        self.csv_path = params.get('csv_path', None)
        self.state_path = params.get('state_path', None)
        self.grafici_path = params.get('grafici_path', None)
        self.log_path = params.get('log_path', None)
        self.subject = params.get('subject', None)
        self.body = params.get('body', None)
        self.to_email = params.get('to_email', None)
        self.cc_email = params.get('cc_email', None)
        self.is_html = params.get('is_html', None)   
        self.is_query_result = params.get('is_query_result', None)  
        self.condizione1 = params.get('condizione1', None)
        self.condizione2 = params.get('condizione2', None)
        self.mese = params.get('mese', None)
        self.anno = params.get('anno', None)
        self.logger = logging.getLogger(f"Job_{self.NomeJob}")
        self.setup_logging()

    def setup_logging(self):
        handler = logging.FileHandler(self.log_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def read_query(self, file_path):
        self.logger.info("Reading query from: %s", file_path)
        with open(file_path, 'r') as f:
            query = f.read().strip()
        self.logger.info("Query read successfully")
        return query

    def run(self):
        raise NotImplementedError("Subclasses should implement this!")
