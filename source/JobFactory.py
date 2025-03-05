from tipoJobs import tipoJobs
from MailQueryAllegatoExcel import MailQueryAllegatoExcel
from MailQueryAllegatoExcelOpenpyxl import MailQueryAllegatoExcelOpenpyxl
from MailQueryAllegatoExcelOpenpyxlMultiSheet import MailQueryAllegatoExcelOpenpyxlMultiSheet
from MailQueryAllegatoGraficiControlliAcessiCSVMensile import MailQueryAllegatoGraficiControlliAcessiCSVMensile
from PDFQueryFacsimileprospettoindennitafidelityCSV import PDFQueryFacsimileprospettoindennitafidelityCSV
from MailQueryBodyHtml import MailQueryBodyHtml
from MailQueryBodyHtmlWP import MailQueryBodyHtmlWP  

import logging

logger = logging.getLogger("JobFactory")

class JobFactory:
    @staticmethod
    def create_job(params):
        job_type = params.get('tipoJobs')
        logger.info(f"Creating job of type: {job_type}")
        if job_type == tipoJobs.MAIL_QUERY_ALLEGATO_EXCEL.value:
            return MailQueryAllegatoExcel(params)               
        if job_type == tipoJobs.MAIL_QUERY_ALLEGATO_EXCEL_OPENPYXL.value:
            return MailQueryAllegatoExcelOpenpyxl(params)                
        if job_type == tipoJobs.MAIL_QUERY_ALLEGATO_EXCEL_OPENPYXL_MULTI_SHEET.value:
            return MailQueryAllegatoExcelOpenpyxlMultiSheet(params)                                    
        elif job_type == tipoJobs.MAIL_QUERY_ALLEGATO_GRAFICI_CA_CSV_MENSILE.value:
            return MailQueryAllegatoGraficiControlliAcessiCSVMensile(params)  
        elif job_type == tipoJobs.PDF_QUERY_FS_CSV.value:
            return PDFQueryFacsimileprospettoindennitafidelityCSV(params)
        elif job_type == tipoJobs.MAIL_QUERY_BODY_HTML.value: 
            return MailQueryBodyHtml(params)                          
        elif job_type == tipoJobs.MAIL_QUERY_BODY_HTML_WP.value: 
            return MailQueryBodyHtmlWP(params)                          
        else:
            raise ValueError(f"Unknown job type: {job_type}")