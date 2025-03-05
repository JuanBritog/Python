""" 
Job : Controlli Acessi Mensile
Obiettivo: Generare e inviare un report mensile sui controlli degli accessi, includendo grafici statistici .
Sorgente dati:


Query SQL (QueryControlliAcessi.sql)

Struttura delle query:
La query estrae dati relativi agli accessi degli utenti.
Processo:
a. Esecuzione della query per estrarre i dati degli accessi
c. Creazione di due grafici statistici:

Top 5 Utenti per Percentuale di Accessi (grafico a torta)
Top 20 Utenti per Numero di Accessi (grafico a barre orizzontali)
d. Invio di un'email con allegati

Output:

Grafico "Top5UtentiPercentualeAccessi.png"
Grafico "Top20UtentiAccessi.png"


Invio:

Destinatari: Definiti nella variabile SISTEMI_PROVVIGIONALIE
CC: Definiti nella variabile CLIENTE
Oggetto: "Cruscotto: Controlli Acessi Mensile"
Corpo: "ControlliAcessi"
Allegati: I due grafici

Nota tecnica:

Il job utilizza uno scheduler per l'esecuzione periodica
I grafici sono generati utilizzando matplotlib
La gestione degli errori e il logging sono implementati per garantire la robustezza del processo
Il codice utilizza le librerie pandas per la manipolazione dei dati e locale per la gestione delle date in formato italiano
L'invio dell'email è gestito tramite SMTP, con le configurazioni del server di posta lette da un file di proprietà
   
"""
import json
import sys
import os

# Aggiungi il percorso della cartella 'source' al sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.join(current_dir, 'source')
sys.path.append(source_dir)
sys.path.append(current_dir)

print(f"Current directory: {current_dir}")
print(f"Source directory: {source_dir}")
print(f"sys.path: {sys.path}")

try:
    from source.scheduler import Scheduler    
    from source.tipoMails import tipoMails
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

if __name__ == "__main__":
    json_params = json.dumps({
        "NomeJob": "ControlliAcessiMensile",
        "tipoJobs": "MAIL_QUERY_ALLEGATO_GRAFICI_CA_CSV_MENSILE",  # Enum TipoJobs       
        "query_path": os.path.join(current_dir, "Cruscotto", "ControlliAcessi", "QueryControlliAcessi.sql"),
        "config_path_db": os.path.join(source_dir, "resources.properties"),        
        "config_path_mail": r"D:\Profin\webapps\EMRL\applications\resources\it\skill\skf3\server\resources.properties",        
        "grafici_path": os.path.join(current_dir, "Cruscotto", "ControlliAcessi", "grafici"),  
        "csv_path": os.path.join(current_dir, "Cruscotto", "ControlliAcessi", "csv"),        
        "log_path": os.path.join(current_dir, "Cruscotto", "ControlliAcessi", "job_ControlliAcessi.log"),
        "subject": "Cruscotto: Controlli Acessi Mensile",
        "body": "ControlliAcessi",
		"to_email": ", ".join(tipoMails.get_emails(tipoMails.SISTEMI_PROVVIGIONALIE)),                
        "condizione1": "non_empty",
        "condizione2": "another_condition",
        "mese": "",
        "anno": "",
        "is_html": False 
    })

    scheduler = Scheduler("Monthly Job Scheduler ControlliAcessi")
    scheduler.add_job(json.loads(json_params))
    scheduler.run_jobs()