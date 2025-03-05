import pyodbc
from resourcesMail2 import create_connectionMail, read_properties
from resourcesDB import create_connection
from Job import Job
from contextlib import closing
import ast

class MailQueryBodyHtmlWP(Job):
    def __init__(self, params):
        super().__init__(params)
        self.condizione1 = params.get('condizione1', '')

    def apply_condition(self, row, columns):
        if self.condizione1:
            try:
                self.logger.info(f"Valore di condizione1: {self.condizione1}")
                field_values = {}
                for col in columns:
                    if col in self.condizione1:
                        value = str(row[columns.index(col)]).replace(',', '.').replace('%', '')
                        try:
                            field_values[col] = float(value)
                        except ValueError:
                            field_values[col] = value

                condition = self.safe_eval(self.condizione1, field_values)
                return 'style="background-color: #FFCCCB;"' if condition else ''
            except Exception as e:
                self.logger.error(f"Errore durante la valutazione della condizione: {e}")
                return ''
        return ''

    def safe_eval(self, expr, variables):
        operatori_consentiti = {'+', '-', '*', '/', '>', '<', '>=', '<=', '==', '!=', 'and', 'or', 'not'}
        funzioni_consentite = {'abs': abs, 'round': round, 'max': max, 'min': min}

        dizionario_sicuro = {**funzioni_consentite, **variables}

        try:
            expr_analizzata = ast.parse(expr, mode='eval')

            for nodo in ast.walk(expr_analizzata):
                if isinstance(nodo, ast.Name) and nodo.id not in dizionario_sicuro:
                    raise NameError(f"Uso di nome non consentito '{nodo.id}'")
                elif isinstance(nodo, ast.Call) and nodo.func.id not in funzioni_consentite:
                    raise NameError(f"Uso di funzione non consentita '{nodo.func.id}'")
                elif isinstance(nodo, ast.BinOp) and type(nodo.op).__name__ not in operatori_consentiti:
                    raise TypeError(f"Uso di operatore non consentito '{type(nodo.op).__name__}'")

            return eval(compile(expr_analizzata, '<string>', 'eval'), {"__builtins__": {}}, dizionario_sicuro)
        except Exception as e:
            raise ValueError(f"Espressione non valida: {e}")

    def run(self):
        try:
            self.logger.info(f"Esecuzione del job: {self.NomeJob}")

            query = self.read_query(self.query_path)
            self.logger.info(f"Query da eseguire: {query}")

            with closing(create_connection(self.config_path_db)) as connection:
                self.logger.info("Connessione al database stabilita con successo.")                
                try:
                    cursor = connection.cursor()
                    cursor.execute(query)
                    columns = [column[0] for column in cursor.description]
                    results = cursor.fetchall()
                    self.logger.info(f"Query eseguita con successo. Righe recuperate: {len(results)}")
                except pyodbc.Error as e:
                    self.logger.error(f"Errore del database: {e}")
                    print(f"Errore del database: {e}")
                    return

            if not results:
                self.logger.info("La query non ha restituito righe, invio email senza risultati.")
                html_body = self.body + "<p>Nessun record trovato.</p>"
            else:
                table_html = "<table border='1' style='border-collapse: collapse; width: 100%;'>"
                table_html += "<tr>" + "".join(f"<th style='background-color: #003366; color: white; padding: 8px;'>{col}</th>" for col in columns) + "</tr>"
                
                for row in results:
                    row_style = self.apply_condition(row, columns)
                    table_html += f"<tr {row_style}>" + "".join(f"<td style='padding: 8px;'>{cell}</td>" for cell in row) + "</tr>"
                
                table_html += "</table>"

                html_body = f"{self.body}<br><br>{table_html}"

            properties_mail = read_properties(self.config_path_mail)
            emailReplay = properties_mail['emailReplay']
            emailFrom = properties_mail['emailFrom']
            smtpServer = properties_mail['smtpServer']
            
            create_connectionMail(smtpServer, emailFrom, emailReplay, self.subject, html_body, self.to_email, self.cc_email, is_html=True, is_query_result=True)
            self.logger.info("Email con corpo HTML inviata con successo.")
            print("Email inviata con successo.")

        except Exception as e:
            self.logger.error(f"Errore durante l'esecuzione del job: {e}")
            print(f"Errore durante l'esecuzione del job: {e}")