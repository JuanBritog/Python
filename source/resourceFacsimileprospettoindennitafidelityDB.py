from datetime import datetime
from resourcesDB import create_connection
import logging

def trasform_data(data_str, typeformat=1):
    data_oggetto = datetime.strptime(data_str, "%Y-%m-%d")
    
    if typeformat == 1:
        return data_oggetto.strftime("%d.%m.%y")
    elif typeformat == 2:
        return data_oggetto.strftime("%Y%m%d") 
    else:
        raise ValueError("typeformat 1 o 2")

def get_data_from_db(ndg, data, config_path_db, query_path, logger):
    try:
        queries = {
            'amount': 'QueryFacsimileprospettoindennitafidelityAmount.sql',
            'indirizzo': 'QueryFacsimileprospettoindennitafidelityIndirizzo.sql',
            'nome': 'QueryFacsimileprospettoindennitafidelityNome.sql',                                                
            'CMIndemnity': 'QueryFacsimileprospettoindennitafidelityCMIndemnity.sql'                        
        }
        
        query_results = {}
        for key, query_file in queries.items():
            with open(f"{query_path}\\{query_file}", 'r') as file:
                query_results[key] = file.read()
        
        logger.info("Query file read successfully.")
        connection = create_connection(config_path_db)
        logger.info("Database connection established successfully.")
        cursor = connection.cursor()
        
        # Ejecutar las queries y obtener los resultados
        cursor.execute(query_results['nome'], ndg)
        result = cursor.fetchone()
        if result is not None:
            nome, sesso, matcod, rapdat = result
            suffisso = "Egregio Signore" if sesso == 'M' else "Egregia Sig.ra"
            suffisso1 = "Sig." if sesso == 'M' else "Sig.ra"
        else:
            logger.error(f"Query for nome returned None for NDG: {ndg}")
            nome = sesso = matcod = suffisso = suffisso1 = "Null"
        
        cursor.execute(query_results['CMIndemnity'], ndg, data)
        result = cursor.fetchone()
        if result is not None:
            finemandato,cessionePortafoglio,fidelityPlan,FIRR,tutelaAmount,totale = result                        
        else:
            logger.error(f"Query for CMIndemnity returned None for NDG: {ndg}")
            finemandato = cessionePortafoglio = fidelityPlan = FIRR = tutelaAmount = totale = "Null"    

        logger.info(f"Sesso: {sesso}, Matcod: {matcod}")

        def execute_query_with_logging(query, params, description):
            try:
                cursor.execute(query, params)
                result = cursor.fetchone()
                if result is not None:
                    return result[0]
                else:
                    logger.error(f"Query for {description} returned None for NDG: {ndg}, Data: {data}")
                    return "Null"
            except Exception as e:
                logger.error(f"Error executing query for {description}: {str(e)}")
                return "Null"
        
        indirizzo = execute_query_with_logging(query_results['indirizzo'], (ndg,), 'indirizzo')                    
        amount = execute_query_with_logging(query_results['amount'], (ndg, data), 'amount')                    
        
        return nome, indirizzo, matcod, rapdat, amount, finemandato,cessionePortafoglio,fidelityPlan,FIRR,tutelaAmount,totale, suffisso, suffisso1

    except Exception as e:
        logger.error(f"An error occurred while getting data from DB: {str(e)}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
