import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import locale
import logging
import traceback
from Job import Job
# from resourcesControlliAcessiGrafici import create_grafici_Top5UtentiPercentualeAccessi, create_grafici_Top20UtentiAccessi
from resourcesControlliAcessiGrafici import create_grafici_Top20UtentiAccessi
from resourcesControlliAcessiCSVSQL import create_CSV
from resourcesMail2 import create_connectionMail, read_properties
from resourcesDBPanda import create_connection
from resourcesInfo import get_italian_month

def delete_existing_graphs(grafici_path, logger):
    """Elimina i grafici esistenti nella cartella specificata."""
    graph_names = [
        # 'Top5UtentiPercentualeAccessi.png',
        'Top20UtentiAccessi.png'
    ]
    for graph_name in graph_names:
        graph_path = os.path.join(grafici_path, graph_name)
        if os.path.exists(graph_path):
            try:
                os.remove(graph_path)
                logger.info(f"Grafico esistente eliminato: {graph_path}")
            except Exception as e:
                logger.warning(
                    f"Impossibile eliminare il grafico esistente {graph_path}: {e}")

class MailQueryAllegatoGraficiControlliAcessiCSVMensile(Job):
    def run(self):
        try:
            self.logger.info(f"Esecuzione del job: {self.NomeJob}")

            # Elimina i grafici esistenti prima di crearne di nuovi
            delete_existing_graphs(self.grafici_path, self.logger)

            # Leggi la query dal file
            query = self.read_query(self.query_path)

            # Stabilisci la connessione al database
            connection = create_connection(self.config_path_db)

            # Calcola mese e anno
            data_corrente = datetime.now()
            if hasattr(self, 'mese') and self.mese:
                mese = int(self.mese)
            else:
                mese = (data_corrente.month - 1) if data_corrente.month > 1 else 12

            if hasattr(self, 'anno') and self.anno:
                anno = int(self.anno)
            else:
                anno = data_corrente.year if data_corrente.month > 1 else data_corrente.year - 1

            # Creazione del file CSV
            try:
                csv_file_path = create_CSV(
                    self.logger,
                    connection,
                    self.csv_path,  # Assicurati che self.csv_path sia definito
                    query,
                    mese,
                    anno
                )
                self.logger.info(f"File CSV creato con successo: {csv_file_path}")
            except Exception as e:
                self.logger.error(f"Errore durante la creazione del file CSV: {e}")
                self.logger.error(traceback.format_exc())
                csv_file_path = None

            # Creazione dei grafici con gestione degli errori
            grafici_creati = []
            # try:
            #     create_grafici_Top5UtentiPercentualeAccessi(
            #         self.logger,
            #         connection,
            #         os.path.join(self.grafici_path, 'Top5UtentiPercentualeAccessi.png'),
            #         query,
            #         mese,
            #         anno
            #     )
            #     grafici_creati.append('Top5UtentiPercentualeAccessi.png')
            # except Exception as e:
            #     self.logger.error(
            #         f"Errore durante la creazione del grafico Top5UtentiPercentualeAccessi: {e}")
            #     self.logger.error(traceback.format_exc())

            try:
                create_grafici_Top20UtentiAccessi(
                    self.logger,
                    connection,
                    os.path.join(self.grafici_path, 'Top20UtentiAccessi.png'),
                    query,
                    mese,
                    anno
                )
                grafici_creati.append('Top20UtentiAccessi.png')
            except Exception as e:
                self.logger.error(
                    f"Errore durante la creazione del grafico Top20UtentiAccessi: {e}")
                self.logger.error(traceback.format_exc())

            properties_mail = read_properties(self.config_path_mail)
            emailReplay = properties_mail['emailReplay']
            emailFrom = properties_mail['emailFrom']
            smtpServer = properties_mail['smtpServer']
            locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')

            # Preparazione degli allegati (grafici e CSV)
            attachment_paths = []
            for graph_name in grafici_creati:
                graph_path = os.path.join(self.grafici_path, graph_name)
                if os.path.exists(graph_path):
                    attachment_paths.append(graph_path)
                else:
                    self.logger.warning(
                        f"Grafico non trovato nonostante sia stato creato: {graph_path}")
            
            # Aggiungi il file CSV agli allegati se è stato creato con successo
            if csv_file_path and os.path.exists(csv_file_path):
                attachment_paths.append(csv_file_path)
            else:
                self.logger.warning("File CSV non trovato o non creato.")

            # Aggiorna l'oggetto dell'email con mese e anno
            nome_mese_italiano = get_italian_month(mese)
            subject_with_date = f"{self.subject} - {nome_mese_italiano} {anno}"

            is_html = self.is_html if hasattr(self, 'is_html') else False
            create_connectionMail(
                smtpServer,
                emailFrom,
                emailReplay,
                subject_with_date,  # Usa l'oggetto aggiornato con mese e anno
                self.body,
                self.to_email,
                self.cc_email,
                attachment_paths,
                is_html=is_html
            )
            self.logger.info("Email con allegati (grafici e CSV) inviata con successo.")
            print("Processo completato con successo!")

        except Exception as e:
            self.logger.error(f"Errore durante l'esecuzione del job: {e}")
            self.logger.error(traceback.format_exc())
            print(f"Errore durante l'esecuzione del job: {e}")
        finally:
            # Chiudi la connessione al database
            if 'connection' in locals():
                connection.close()

    def read_query(self, query_path):
        with open(query_path, 'r') as file:
            return file.read()