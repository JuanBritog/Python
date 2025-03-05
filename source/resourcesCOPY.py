import os
import shutil
from datetime import datetime

def backup_sposta_file_e_crea_eot(cartella_sorgente, file_da_spostare, cartella_export, nome_file_eot):
    data_corrente = datetime.now().strftime("%Y%m%d")
    
    # Assicurati che la cartella EXPORT esista
    if not os.path.exists(cartella_export):
        os.makedirs(cartella_export)
        print(f"Cartella {cartella_export} creata.")

    # Crea la cartella di backup all'interno di EXPORT
    cartella_backup = os.path.join(cartella_export, f"BK_{data_corrente}")
    if not os.path.exists(cartella_backup):
        os.makedirs(cartella_backup)
        print(f"Cartella di backup {cartella_backup} creata.")

    file_spostati = []
    file_non_trovati = []

    # Backup e spostamento dei file specificati
    for file in file_da_spostare:
        file_attuale = file.replace("{{data_corrente}}", data_corrente)
        percorso_sorgente = os.path.join(cartella_sorgente, file_attuale)
        percorso_backup = os.path.join(cartella_backup, file_attuale)
        percorso_destinazione = os.path.join(cartella_export, file_attuale)
        
        if os.path.exists(percorso_sorgente):
            try:
                # Copia il file nella cartella di backup
                shutil.copy2(percorso_sorgente, percorso_backup)
                print(f"File {file_attuale} copiato in {cartella_backup}")
                
                # Sposta il file nella cartella EXPORT
                shutil.move(percorso_sorgente, percorso_destinazione)
                file_spostati.append(file_attuale)
                print(f"File {file_attuale} spostato in {cartella_export}")
            except Exception as e:
                print(f"Errore durante il backup o lo spostamento di {file_attuale}: {str(e)}")
        else:
            file_non_trovati.append(file_attuale)
            print(f"File {file_attuale} non trovato nella cartella sorgente.")

    # Crea il file EOT
    nome_file_eot_attuale = nome_file_eot.replace("{{data_corrente}}", data_corrente)
    percorso_file_eot = os.path.join(cartella_export, nome_file_eot_attuale)
    
    try:
        with open(percorso_file_eot, 'w') as f:
            f.write(f"File creato il {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"File spostati: {', '.join(file_spostati)}\n")
            f.write(f"File non trovati: {', '.join(file_non_trovati)}\n")
        print(f"File {nome_file_eot_attuale} creato in {cartella_export}")
    except Exception as e:
        print(f"Errore durante la creazione del file EOT: {str(e)}")
