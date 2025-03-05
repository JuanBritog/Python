# C:\Juan\Python\web-esecutore.py
from flask import Flask, jsonify, send_from_directory
import os
import subprocess
import glob
import re

app = Flask(__name__)

def ottieni_file_python():
    file_python = glob.glob('*.py')
    return [f for f in file_python if f != 'web-esecutore.py']

def leggi_descrizione_job(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Buscar comentarios multilinea que contengan la descripción
            description = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if description:
                return description.group(1).strip()
            # Si no hay comentarios multilinea, buscar comentarios de una línea
            description = re.findall(r'#\s*(.*)', content)
            if description:
                return '\n'.join(description)
            return "Nessuna descrizione disponibile"
    except Exception as e:
        return f"Errore nella lettura della descrizione: {str(e)}"

@app.route('/logo.png')
def serve_logo():
    return send_from_directory('.', 'logo.png')

@app.route('/descrizione/<nome_file>')
def ottieni_descrizione(nome_file):
    file_path = os.path.join(os.getcwd(), nome_file)
    descrizione = leggi_descrizione_job(file_path)
    return jsonify({'descrizione': descrizione})

@app.route('/')
def home():
    files = ottieni_file_python()
    righe_tabella_individuali = ''
    for file in files:
        if file != 'esecutore-jobs.py':
            righe_tabella_individuali += f'''
                <tr>
                    <td class="border px-4 py-2">{file}</td>
                    <td class="border px-4 py-2 text-center">
                        <button onclick="eseguiScript('{file}')" 
                                class="button">
                            Esegui
                        </button>
                        <button onclick="mostraDescrizione('{file}')"
                                class="button button-info ml-2">
                            Info
                        </button>
                    </td>
                </tr>
            '''

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gestione Jobs Python</title>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                background-color: #f0f2f5;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }}
            .header {{
                background-color: white;
                padding: 10px 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .logo {{
                height: 40px;
                width: auto;
            }}
            .version {{
                color: #666;
                font-size: 14px;
            }}
            .main-wrapper {{
                padding: 20px;
                flex: 1;
                display: flex;
                justify-content: center;
            }}
            .container {{
                width: 90%;
                max-width: 1600px;
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .footer {{
                background-color: #1a3e72;
                color: white;
                text-align: center;
                padding: 15px;
                font-size: 12px;
            }}
            h1 {{
                color: #1a3e72;
                text-align: center;
                margin-bottom: 30px;
                font-size: 28px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px 20px;
                text-align: left;
            }}
            th {{
                background-color: #1a3e72;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .button {{
                background-color: #4CAF50;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                min-width: 100px;
            }}
            .button:hover {{
                background-color: #45a049;
            }}
            .button-info {{
                background-color: #1a3e72;
            }}
            .button-info:hover {{
                background-color: #15325c;
            }}
            .ml-2 {{
                margin-left: 8px;
            }}
            #risultato {{
                margin-bottom: 30px;
                padding: 20px;
                border-radius: 4px;
                display: none;
            }}
            .successo {{
                background-color: #dff0d8;
                color: #3c763d;
                border: 1px solid #d6e9c6;
            }}
            .errore {{
                background-color: #f2dede;
                color: #a94442;
                border: 1px solid #ebccd1;
            }}
            .tabs {{
                display: flex;
                margin-bottom: 30px;
                border-bottom: 1px solid #dee2e6;
            }}
            .tab {{
                padding: 12px 24px;
                cursor: pointer;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-bottom: none;
                margin-right: 5px;
                border-radius: 4px 4px 0 0;
            }}
            .tab.active {{
                background-color: white;
                border-bottom: 2px solid #1a3e72;
                font-weight: bold;
            }}
            .tab-content {{
                display: none;
            }}
            .tab-content.active {{
                display: block;
            }}
            .executor-section {{
                margin-bottom: 30px;
                padding: 25px;
                background-color: #f8f9fa;
                border-radius: 8px;
            }}
            .text-center {{
                text-align: center;
            }}
            .modal {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                z-index: 1000;
            }}
            .modal-content {{
                position: relative;
                background-color: white;
                margin: 50px auto;
                padding: 20px;
                width: 80%;
                max-width: 800px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .modal-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px solid #dee2e6;
            }}
            .modal-title {{
                color: #1a3e72;
                font-size: 20px;
                font-weight: bold;
                margin: 0;
            }}
            .close-button {{
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: #666;
            }}
            .close-button:hover {{
                color: #333;
            }}
            .modal-body {{
                max-height: 70vh;
                overflow-y: auto;
                white-space: pre-line;
                line-height: 1.5;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <img src="/logo.png" alt="Mediobanca Premier" class="logo">
            <span class="version">v1.2.1</span>
        </div>
        
        <div class="main-wrapper">
            <div class="container">
                <h1>Gestione Jobs Python</h1>
                
                <div id="risultato"></div>

                <div class="executor-section">
                    <table>
                        <thead>
                            <tr>
                                <th>Nome File</th>
                                <th style="width: 250px;">Azione</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>esecutore-jobs.py</td>
                                <td class="text-center">
                                    <button onclick="eseguiScript('esecutore-jobs.py')" 
                                            class="button">
                                        Esegui
                                    </button>
                                    <button onclick="mostraDescrizione('esecutore-jobs.py')"
                                            class="button button-info ml-2">
                                        Info
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="tabs">
                    <div class="tab active" onclick="cambiaTab('tab1', this)">Esecutore Job</div>
                    <div class="tab" onclick="cambiaTab('tab2', this)">File Individuali</div>
                </div>

                <div id="tab1" class="tab-content active">
                    <!-- El contenido del tab1 está arriba -->
                </div>

                <div id="tab2" class="tab-content">
                    <table>
                        <thead>
                            <tr>
                                <th>Nome File</th>
                                <th style="width: 250px;">Azione</th>
                            </tr>
                        </thead>
                        <tbody>
                            {righe_tabella_individuali}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Modal para la descripción -->
        <div id="modal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2 id="modal-title" class="modal-title"></h2>
                    <button class="close-button" onclick="chiudiModal()">&times;</button>
                </div>
                <div id="modal-body" class="modal-body"></div>
            </div>
        </div>

        <div class="footer">
            © 2024 Mediobanca Premier S.p.A. - Gruppo Bancario Mediobanca | P.IVA 10536040966 | Codice Fiscale e Iscrizione al Registro delle Imprese di Milano 10359360152
        </div>

        <script>
        function eseguiScript(nomeFile) {{
            document.getElementById('risultato').style.display = 'block';
            document.getElementById('risultato').innerHTML = 'Esecuzione in corso...';
            document.getElementById('risultato').className = '';
            
            fetch('/esegui/' + encodeURIComponent(nomeFile), {{
                method: 'POST'
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.status === 'success') {{
                    document.getElementById('risultato').innerHTML = 
                        '<strong>Completato:</strong> ' + data.output;
                    document.getElementById('risultato').className = 'successo';
                }} else {{
                    document.getElementById('risultato').innerHTML = 
                        '<strong>Errore:</strong> ' + data.error;
                    document.getElementById('risultato').className = 'errore';
                }}
            }})
            .catch(error => {{
                document.getElementById('risultato').innerHTML = 
                    '<strong>Errore di esecuzione:</strong> ' + error;
                document.getElementById('risultato').className = 'errore';
            }});
        }}

        function cambiaTab(tabId, elemento) {{
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            elemento.classList.add('active');

            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            document.getElementById(tabId).classList.add('active');
        }}

        function mostraDescrizione(nomeFile) {{
            fetch('/descrizione/' + encodeURIComponent(nomeFile))
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('modal-title').textContent = nomeFile;
                    document.getElementById('modal-body').textContent = data.descrizione;
                    document.getElementById('modal').style.display = 'block';
                }})
                .catch(error => {{
                    console.error('Errore:', error);
                    alert('Errore nel caricamento della descrizione');
                }});
        }}

        function chiudiModal() {{
            document.getElementById('modal').style.display = 'none';
        }}

        // Cerrar el modal si se hace clic fuera de él
        window.onclick = function(event) {{
            let modal = document.getElementById('modal');
            if (event.target == modal) {{
                chiudiModal();
            }}
        }}
        </script>
    </body>
    </html>
    '''

@app.route('/esegui/<nome_file>', methods=['POST'])
def esegui(nome_file):
    try:
        if not nome_file.endswith('.py') or not os.path.exists(nome_file):
            raise ValueError("File non valido")
            
        risultato = subprocess.run(
            ['python', nome_file],
            capture_output=True,
            text=True,
            check=True
        )
        
        return jsonify({
            'status': 'success',
            'output': risultato.stdout.strip() or "Eseguito con successo"
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    os.chdir(r'D:\SPA\Python')
    app.run(host='0.0.0.0', port=5000)
