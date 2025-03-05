import pandas as pd
from datetime import datetime
from resourcesInfo import get_italian_month

def create_CSV(logger, connection, csv_path, query, mese=None, anno=None):
    try:
        # Calcola mese e anno se non forniti
        if mese is None or anno is None:
            data_corrente = datetime.now()
            if mese is None:
                mese = (data_corrente.month - 1) if data_corrente.month > 1 else 12
            if anno is None:
                anno = data_corrente.year if data_corrente.month > 1 else data_corrente.year - 1

        # Esegui la query e crea il DataFrame - passa i parametri due volte per il UNION
        df = pd.read_sql(query, connection, params=(mese, anno, mese, anno))

        # Log del DataFrame per debugging
        logger.info(f"DataFrame creato: {df}")

        # Ottieni il nome del mese in italiano
        nome_mese_italiano = get_italian_month(mese)

        # Crea il nome del file CSV
        nome_file_csv = f"Accessi{nome_mese_italiano}{anno}.csv"
        percorso_completo = f"{csv_path}/{nome_file_csv}"

        # Scrivi i risultati nel file CSV        
        df.to_csv(percorso_completo, index=False, encoding='utf-8', sep=';')

        logger.info(f"File CSV creato con successo: {percorso_completo}")
        return percorso_completo

    except Exception as e:
        logger.error(f"Errore durante la creazione del file CSV: {e}")
        raise