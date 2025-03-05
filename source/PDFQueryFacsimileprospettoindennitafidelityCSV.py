import os
import shutil
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
from io import BytesIO
from resourceFacsimileprospettoindennitafidelityDB import get_data_from_db, trasform_data
from resourceFacsimileprospettoindennitafidelityFile import readFile
from resourcesZIP import crea_zip_da_cartella
from resourcesCOPY import backup_sposta_file_e_crea_eot
from Job import Job
import csv

class PDFQueryFacsimileprospettoindennitafidelityCSV(Job):
    def run(self):
        try:
            self.logger.info(f"Esecuzione del job: {self.NomeJob}") 
            
            file_path = os.path.join(self.pdf_path, 'file_guida.txt')
            
            # Creare FileGuida.csv
            csv_path = os.path.join(self.pdf_path, 'FileGuida.csv')
            with open(csv_path, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=';')
                
                for ndg, data, ruolo, copertuAssMorte, copertuAssInfort in readFile(file_path, self.logger):
                    if ndg is None:
                        continue

                    print('NDG :', ndg) 
                    print('Data :', data)
                    data_trasform = trasform_data(data)
                    data_trasform2 = trasform_data(data, 2)                                                                
                    
                    result = get_data_from_db(ndg, data, self.config_path_db, self.query_path, self.logger)
                    if result is None or len(result) != 13:
                        self.logger.error(f"Dati insufficienti restituiti per NDG: {ndg}. Saltando questa voce.")
                        continue

                    nome, indirizzo, matcod, rapdat, amount, finemandato, cessionePortafoglio, fidelityPlan, FIRR, tutelaAmount, totale, suffisso, suffisso1 = result

                    if None in [nome, indirizzo, matcod, rapdat, amount, finemandato, cessionePortafoglio, fidelityPlan, FIRR, tutelaAmount, totale, suffisso, suffisso1]:
                        self.logger.error(f"Dati critici mancanti per NDG {ndg}. Saltando la creazione del PDF. Indirizzo {indirizzo}: AUM: {amount}")
                        continue

                    if amount in [None, "Null"]: 
                        self.logger.error(f"Amount restituito None per NDG: {ndg}, Data: {data}")                
                        continue                                  

                    file_loader = FileSystemLoader(self.pdf_path)
                    env = Environment(loader=file_loader)
                    template = env.get_template('Template.html')
                    print('Nome : ', nome)               
                    
                    input_dict = {
                        'nome': nome,
                        'indirizzo': indirizzo,
                        'data': data,
                        'matcod': matcod,
                        'rapdat': rapdat,
                        'amount': amount,
                        'finemandato': finemandato,
                        'FIRR': FIRR,
                        'fidelityPlan': fidelityPlan,
                        'suffisso': suffisso,
                        'copertuAssMorte': copertuAssMorte,
                        'copertuAssInfort': copertuAssInfort, 
                        'data_trasform': data_trasform, 
                        'cessionePortafoglio': cessionePortafoglio,
                        'suffisso1': suffisso1,
                        'ruolo': ruolo,
                        'tutelaAmount': tutelaAmount,
                        'totale': totale
                    }
                    
                    output = template.render(input_dict)
                    htmlstr = output
                    pdf_output = BytesIO()
                    pisa.CreatePDF(htmlstr, dest=pdf_output, encoding='utf-8')
                    
                    folder_path = os.path.join(self.pdf_path, data_trasform2)
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)

                    pdf_output_path = os.path.join(folder_path, f"VALORI_INDENNITARI_{ndg.strip()}_{matcod.strip()}_{data_trasform2}.pdf")
                    with open(pdf_output_path, "wb") as pdf_file:      
                        pdf_file.write(pdf_output.getvalue())

                    self.logger.info(f"PDF creato con successo per NDG {ndg}")
                    print(f"PDF creato con successo per NDG {ndg}")
                    
                    # Scrivere in FileGuida.csv senza spazi bianchi
                    data_odierna = datetime.now().strftime("%Y/%m/%d")
                    csv_row = [
                        ndg.strip(),
                        matcod.strip(),
                        f"VALORI_INDENNITARI_{ndg.strip()}_{matcod.strip()}_{data_trasform2}.pdf",
                        "VALORI_INDENNITARI",
                        data_trasform2,  
                        data_odierna
                    ]
                    csvwriter.writerow(csv_row)
                    
                    print('---------------------------------------------------------------')
            
            # Spostare FileGuida.csv nella cartella dei PDF
            shutil.move(csv_path, os.path.join(folder_path, 'FileGuida.CSV'))
            self.logger.info(f"FileGuida.csv spostato nella cartella dei PDF: {folder_path}")
                    
            # Creazione del file ZIP    
            data_corrente = datetime.now().strftime("%Y%m%d")
            zip_filename = f"PRF_STATINI_VALORI_INDENNITARI_0101_{data_corrente}.ZIP"
            zip_path = os.path.join(self.pdf_path, zip_filename)
            crea_zip_da_cartella(folder_path, zip_path)
            self.logger.info(f"File ZIP creato: {zip_path}")            
            
            nome_file_eot = f"PRF_STATINI_VALORI_INDENNITARI_0101_{data_corrente}.EOT"
            cartella_export = os.path.join(self.pdf_path, "EXPORT")
            file_da_copiare = [zip_filename]
            backup_sposta_file_e_crea_eot(self.pdf_path, file_da_copiare, cartella_export, nome_file_eot)            
            self.logger.info(f"Stato creato cartella EXPORT")  
        except Exception as e:
            self.logger.error(f"Errore durante l'esecuzione del job: {e}")
            print(f"Errore durante l'esecuzione del job: {e}")

