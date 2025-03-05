"""
Job: Controllo Jobs Giornalieri 
Obiettivo:
Monitorare Jobs Emerald, fornendo una panoramica dei processi eseguiti oggi, ieri e, se è lunedì, anche dell'altro ieri.
Sorgente dati:

EMRLCBF1.[dbo].[JAPJobs]
EMRLCBF1.[dbo].[JAPProcesses]
EMRLCBF1.dbo.Domains

Struttura delle query:

Dati per oggi: Seleziona tutti i jobs eseguiti oggi.
Dati per ieri: Seleziona i jobs eseguiti ieri, escludendo quelli con JobStatus 'V'.
Dati per l'altro ieri: Seleziona i jobs eseguiti due giorni fa, escludendo quelli con JobStatus 'V', solo se oggi è lunedì.

Invio:
La query restituisce un set di risultati combinato, ordinato per ProcessName (ascendente) e StartExecTimestamp (discendente).
Nota tecnica:

Utilizza NOLOCK su tutte le tabelle per migliorare le prestazioni, accettando potenziali letture sporche.
Converte StartExecTimestamp in formato italiano (dd/mm/yyyy HH:MM:SS).
Utilizza UNION ALL per combinare i risultati dei diversi giorni.
Implementa una logica condizionale per includere i dati dell'altro ieri solo se oggi è lunedì.
Non utilizza tabelle temporanee per evitare overhead di scrittura su disco.

Dettagli implementativi:

Definisce variabili per oggi, ieri, l'altro ieri e il giorno della settimana.
Utilizza una subquery per unire i risultati dei diversi giorni.
Applica filtri specifici per ogni giorno:

Oggi: nessun filtro aggiuntivo
Ieri e l'altro ieri: esclude JobStatus 'V'
L'altro ieri: incluso solo se oggi è lunedì


Unisce le tabelle JAPJobs, JAPProcesses e Domains per ottenere informazioni complete sui jobs.
Ordina il risultato finale per ProcessName (ASC) e StartExecTimestamp (DESC).

Colonne restituite:

ProcessCode
ProcessName
JobStatus
JobStatusDesc (descrizione del JobStatus dalla tabella Domains)
StartExecTimestamp (in formato italiano)


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
        "NomeJob": "ControlloJobsEmerald",
        "tipoJobs": "MAIL_QUERY_BODY_HTML_WP",  # Enum TipoJobs
        "query_path": os.path.join(current_dir, "EMERALD", "ControlloJobsEmerald", "QueryControlloJobsEmerald.sql"),
        "config_path_db": os.path.join(source_dir, "resources.properties"),        
        "config_path_mail": r"D:\Profin\webapps\EMRL\applications\resources\it\skill\skf3\server\resources.properties",        
        "log_path": os.path.join(current_dir, "EMERALD", "ControlloJobsEmerald", "log", "job_ControlloJobsEmerald.log"),
        "subject": "EMERALD: Controllo Jobs Emerald",
        "body": "Controllo Jobs Emerald :<br>",
        "to_email": ", ".join(tipoMails.get_emails(tipoMails.SISTEMI_PROVVIGIONALIE)),        
        "condizione1": "JobStatus != 'V'",
        "condizione2": "another_condition",
        "is_html": True,         
        "is_query_result": True  
    })

    scheduler = Scheduler("Daily Job Scheduler ControlloJobsEmerald")
    scheduler.add_job(json.loads(json_params))
    scheduler.run_jobs()