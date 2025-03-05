import pyodbc
from typing import Tuple
import logging
from contextlib import closing
from resourcesDB import create_connection

logger = logging.getLogger(__name__)

def verify_mu06_results(config_path_db: str, sql_file_path: str) -> Tuple[bool, str]:
    """
    Verifies MU06 results and returns appropriate message for email body.
    
    Args:
        config_path_db: Path to database configuration file
        sql_file_path: Path to the SQL file containing the verification query
        
    Returns:
        tuple: (has_errors: bool, message: str)
    """
    try:
        # Read SQL query
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_query = file.read()
            logger.info("Query di verifica MU06 caricata con successo")

        # Create connection and execute query
        with closing(create_connection(config_path_db)) as connection:
            logger.info("Connessione al database stabilita con successo")
            
            try:
                cursor = connection.cursor()
                cursor.execute(sql_query)
                
                # Get column names and results
                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()
                logger.info(f"Query di verifica eseguita con successo. Righe recuperate: {len(results)}")
                
                if not results:
                    logger.info("Nessun risultato trovato nella verifica MU06")
                    return False, "<br>Il report MU06 non presenta squadrature"
                
                # Check if any errors exist (NumeroErrori > 0)
                has_errors = False
                error_details = []
                
                for row in results:
                    tipo_commissione = row[columns.index('TipoCommissione')]
                    numero_errori = row[columns.index('NumeroErrori')]
                    
                    if numero_errori > 0:
                        has_errors = True
                        error_details.append(f"{tipo_commissione} ({numero_errori} errori)")
                
                if has_errors:
                    error_message = "<br>Il report MU06 presenta squadrature nei seguenti tipi:<br>" + "<br>".join(error_details)
                    logger.warning(f"Trovate squadrature nella verifica MU06: {error_message}")
                    return True, error_message
                else:
                    success_message = "<br>Il report MU06 non presenta squadrature<br>"
                    logger.info("Verifica MU06 completata senza errori")
                    return False, success_message
                    
            except pyodbc.Error as e:
                error_message = f"<br>Errore durante l'esecuzione della query di verifica MU06: {str(e)}"
                logger.error(f"Errore del database: {str(e)}")
                print(f"Errore del database: {str(e)}")
                return True, error_message
            
    except Exception as e:
        error_message = f"<br>Errore durante la verifica MU06: {str(e)}"
        logger.error(f"Errore in verify_mu06_results: {str(e)}")
        print(f"Errore in verify_mu06_results: {str(e)}")
        return True, error_message