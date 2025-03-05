import logging
import traceback
import subprocess
import os
import json
from datetime import datetime
import calendar
import sys

# Definizione del percorso base
percorso_base = r"D:\SPA\Python"

# Configurazione del logging
file_log = os.path.join(percorso_base, 'schedulatore_multi_script.log')
formattatore_log = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Configurazione del file di log che viene sovrascritto ad ogni esecuzione
gestore_file = logging.FileHandler(file_log, mode='w')
gestore_file.setFormatter(formattatore_log)

logger = logging.getLogger('Esecutore Multi-Script')
logger.setLevel(logging.INFO)
logger.addHandler(gestore_file)

def esegui_script(nome_script, percorso_script):
    """
    Esegue uno script Python e registra il risultato dell'esecuzione.
    
    Args:
        nome_script: Nome dello script da eseguire
        percorso_script: Percorso completo dello script
        
    Returns:
        bool: True se l'esecuzione ha avuto successo, False altrimenti
    """
    logger.info(f"Avvio dell'esecuzione di {nome_script}")
    try:
        if not os.path.exists(percorso_script):
            logger.error(f"Lo script {percorso_script} non esiste.")
            return False
        
        risultato = subprocess.run(["python", percorso_script], capture_output=True, text=True)
        
        if risultato.returncode == 0:
            logger.info(f"{nome_script} eseguito con successo")
            if risultato.stdout.strip():
                logger.info(f"Output di {nome_script}: {risultato.stdout.strip()}")
            return True
        else:
            logger.error(f"Errore nell'esecuzione di {nome_script}. Codice di uscita: {risultato.returncode}")
            if risultato.stderr.strip():
                logger.error(f"Errore di {nome_script}: {risultato.stderr.strip()}")
            return False
    except Exception as e:
        logger.error(f"Errore durante l'esecuzione di {nome_script}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def carica_configurazione():
    """
    Carica la configurazione dei job dal file JSON.
    
    Returns:
        dict: Configurazione caricata dal file JSON, None se si verifica un errore
    """
    percorso_config = os.path.join(percorso_base, 'config-jobs-daily.json')
    
    if not os.path.exists(percorso_config):
        logger.error(f"File di configurazione non trovato: {percorso_config}")
        return None
        
    try:
        with open(percorso_config, 'r') as f:
            config = json.load(f)
        logger.info(f"Configurazione caricata con successo: {percorso_config}")
        return config
    except json.JSONDecodeError:
        logger.error(f"Errore nella decodifica del file JSON: {percorso_config}")
        return None
    except Exception as e:
        logger.error(f"Errore nel caricamento della configurazione: {str(e)}")
        return None

def ottieni_giorno_attuale():
    """
    Ottiene il nome del giorno della settimana corrente in italiano.
    
    Returns:
        str: Nome del giorno della settimana in italiano
    """
    giorni = ['lunedi', 'martedi', 'mercoledi', 'giovedi', 'venerdi', 'sabato', 'domenica']
    return giorni[datetime.now().weekday()]

def deve_eseguire_job(job):
    """
    Determina se un job deve essere eseguito oggi in base alla sua configurazione.
    
    Args:
        job: Dizionario contenente la configurazione del job
        
    Returns:
        bool: True se il job deve essere eseguito oggi, False altrimenti
    """
    oggi = datetime.now()
    giorno_attuale = ottieni_giorno_attuale()

    if not job.get('enabled', False):
        return False

    # Verifica se il job ha una data di inizio e se è già iniziato
    data_inizio = job.get('data_inizio')
    if data_inizio:
        data_inizio = datetime.strptime(data_inizio, '%Y-%m-%d')
        if oggi.date() < data_inizio.date():
            return False

    # Verifica se il job deve essere eseguito in giorni specifici della settimana
    if 'giorni' in job:
        return giorno_attuale in job['giorni']
    
    # Verifica se il job deve essere eseguito in un giorno specifico del mese
    if 'giorno' in job:
        return str(oggi.day) == str(job['giorno'])

    return False

def esegui_jobs():
    """
    Funzione principale che carica la configurazione ed esegue i job programmati per oggi.
    """
    config = carica_configurazione()
    oggi = datetime.now()
    logger.info(f"Data attuale: {oggi.strftime('%Y-%m-%d')}")

    jobs_eseguiti = 0

    if config and 'jobs' in config:
        for job in config['jobs']:
            if deve_eseguire_job(job):
                percorso_script = os.path.join(percorso_base, job['script'])
                if esegui_script(job['script'], percorso_script):
                    jobs_eseguiti += 1
        logger.info(f"Tutti i job applicabili sono stati eseguiti. Totale jobs eseguiti: {jobs_eseguiti}")
    else:
        logger.warning("Nessun job configurato o configurazione non valida")

if __name__ == "__main__":
    logger.info("Avvio dell'esecuzione dei jobs")
    try:
        esegui_jobs()
    except Exception as e:
        logger.error(f"Errore critico nell'esecuzione dei jobs: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
