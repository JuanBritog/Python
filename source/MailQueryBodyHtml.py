import pandas as pd
from resourcesMail2 import create_connectionMail, read_properties
from resourcesDBPanda import create_connection
from Job import Job
from contextlib import closing

class MailQueryBodyHtml(Job):
    def run(self):
        try:
            self.logger.info(f"Running job: {self.NomeJob}")

            query = self.read_query(self.query_path)
            self.logger.info(f"Query to be executed: {query}")

            with closing(create_connection(self.config_path_db)) as connection:
                self.logger.info("Database connection established successfully.")
                try:
                    df = pd.read_sql(query, connection)
                    self.logger.info(f"Query executed successfully. DataFrame shape: {df.shape}")
                except pd.io.sql.DatabaseError as e:
                    self.logger.error(f"Database error: {e}")
                    print(f"Database error: {e}")
                    return

            if df.empty:
                self.logger.info("Query returned no rows, sending email with no results message.")
                html_body = self.body + "<p>Nessun record trovato.</p>"
            else:
                # Calcular el ancho máximo de cada columna
                max_lengths = {}
                for col in df.columns:
                    # Convertir todos los valores a string y obtener la longitud máxima
                    max_content_length = df[col].apply(lambda x: len(str(x)) if x is not None else 0).max()
                    max_lengths[col] = max(max_content_length, len(str(col)))

                # Calcular el ancho total de la tabla
                total_width = sum(max_lengths.values())
                
                # Estilo CSS para la tabla con anchos de columna dinámicos
                table_style = f"""
                <style>
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        max-width: {total_width * 10}px;
                        margin: 20px 0;
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                    }}
                    th, td {{
                        text-align: left;
                        padding: 8px;
                        border: 1px solid #ddd;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        white-space: nowrap;
                    }}
                    th {{
                        background-color: #003366;
                        color: white;
                        font-weight: bold;
                    }}
                    tr:nth-child(even) {{
                        background-color: #f2f2f2;
                    }}
                    tr:hover {{
                        background-color: #e6f2ff;
                    }}
                    {' '.join([f'.col-{i} {{ width: {max_lengths[col] * 100 / total_width}%; }}' for i, col in enumerate(df.columns)])}
                </style>
                """
                
                # Generar la tabla HTML con clases de columna personalizadas
                html_table = df.to_html(index=False, classes='table', border=0)
                
                # Añadir clases a las columnas para el ancho dinámico
                for i, col in enumerate(df.columns):
                    html_table = html_table.replace(f'<th>{col}</th>', f'<th class="col-{i}">{col}</th>')
                    html_table = html_table.replace(f'<td>', f'<td class="col-{i}">', 1)

                html_body = f"{self.body}<br><br>{table_style}{html_table}"

            properties_mail = read_properties(self.config_path_mail)
            emailFrom = properties_mail['emailFrom']
            emailReplay = properties_mail['emailReplay']
            smtpServer = properties_mail['smtpServer']
            
            create_connectionMail(smtpServer, emailFrom, emailReplay, self.subject, html_body, self.to_email, self.cc_email, is_html=True, is_query_result=True)
            self.logger.info("Email with dynamically styled HTML body sent successfully.")
            print("Email sent successfully.")

        except Exception as e:
            self.logger.error(f"Error during job execution: {e}")
            print(f"Error during job execution: {e}")