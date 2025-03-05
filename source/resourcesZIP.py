import os
import zipfile
from datetime import datetime
import sys
import argparse

def crea_zip_da_cartella(percorso_cartella, modello_nome_zip):
    # Ottieni la data corrente
    data_corrente = datetime.now().strftime("%Y%m%d")
    
    # Crea il nome del file ZIP
    nome_file_zip = modello_nome_zip.format(data_corrente=data_corrente)
    
    # Crea il file ZIP
    with zipfile.ZipFile(nome_file_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for radice, cartelle, files in os.walk(percorso_cartella):
            for file in files:
                percorso_file = os.path.join(radice, file)
                nome_archiviazione = os.path.relpath(percorso_file, percorso_cartella)
                zipf.write(percorso_file, nome_archiviazione)
    
    print(f"File ZIP creato: {nome_file_zip}")
