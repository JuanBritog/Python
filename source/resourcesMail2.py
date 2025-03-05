import sys
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def read_properties(file_path):
    properties = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                properties[key.strip()] = value.strip()
    return properties

def create_connectionMail(smtp_server, from_email, emailReplay, subject, body, to_email, to_cc=None, attachment_paths=None, is_html=True, is_query_result=False):
    msg = MIMEMultipart('alternative')
    msg['From'] = f"{from_email}<{emailReplay}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    from_email = f"{from_email}<{emailReplay}>"

    if to_cc:
        msg['Cc'] = to_cc

    warning_message = "Si prega di NON rispondere a questa mail in quanto non presidiata."
    python_version = sys.version.split()[0]
    attenzione = ("ATTENZIONE: Questo documento è indirizzato esclusivamente al destinatario. "
                  "Tutte le informazioni ivi contenute, compresi eventuali allegati, sono soggette a riservatezza "
                  "secondo i termini del D.Lgs. 196/2003 in materia di \"privacy\" e ne è proibita l'utilizzazione "
                  "da parte di altri soggetti. Se dovesse aver ricevuto per errore questo messaggio, La preghiamo "
                  "cortesemente di contattare a U.ITSistemiProvvigionalieAmministrativi_EXT@mediobancapremier.com "
                  "al più presto e di cancellarlo immediatamente dopo. Grazie.")

    footer = f"""
---
{warning_message}
EMAIL AUTOMATICA: Inviato utilizzando Python versione {python_version}

{attenzione}
"""

    html_footer = f"""
    <hr>
    <p><strong>{warning_message}</strong></p>
    <p><i>EMAIL AUTOMATICA: Inviato utilizzando Python versione {python_version}</i></p>
    <p style="font-size: 0.9em; color: #555;">
        {attenzione}
    </p>
    """

    if is_query_result:
        # El cuerpo ya es HTML y contiene el resultado de la consulta
        html_body = body + html_footer
        text_body = "Questo messaggio è in formato HTML. Si prega di utilizzare un client di posta elettronica che supporti l'HTML per visualizzarlo correttamente." + footer
    else:
        text_body = body + footer
        html_body = body + html_footer if is_html else f"<html><body>{body}{html_footer}</body></html>"

    part1 = MIMEText(text_body, 'plain')
    part2 = MIMEText(html_body, 'html')

    msg.attach(part1)
    msg.attach(part2)

    if attachment_paths:
        for attachment_path in attachment_paths:
            if os.path.isfile(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")
                    msg.attach(part)
            else:
                print(f"The file {attachment_path} does not exist and will not be attached.")

    recipients = to_email.split(",") + (to_cc.split(",") if to_cc else [])

    with smtplib.SMTP(smtp_server) as server:
        text = msg.as_string()
        server.sendmail(from_email, recipients, text)
