import calendar
import locale
from dateutil.relativedelta import relativedelta
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
from resourcesInfo import get_italian_month

matplotlib.use('Agg')

COLOR_PALETTE = [
    '#202742',
    '#ff7f0e',
    '#2ca02c',
    '#d62728',
    '#9467bd',
    '#8c564b']
BACKGROUND_COLOR = '#f0f0f0'
TEXT_COLOR = '#333333'

def set_style():
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial']
    plt.rcParams['axes.edgecolor'] = TEXT_COLOR
    plt.rcParams['text.color'] = TEXT_COLOR
    plt.rcParams['axes.labelcolor'] = TEXT_COLOR
    plt.rcParams['xtick.color'] = TEXT_COLOR
    plt.rcParams['ytick.color'] = TEXT_COLOR
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    plt.rcParams['axes.facecolor'] = '#f0f0f0'
    plt.rcParams['figure.facecolor'] = 'white'

def create_grafici_Top5UtentiPercentualeAccessi(
    logger, connection, output_path, query, mese=None, anno=None):
    logger.info("Creazione del grafico Top 5 Utenti Percentuale Accessi")

    try:
        # Calcola mese e anno se non forniti        
        if mese is None or anno is None:
            data_corrente = datetime.now()               
            if mese is None:
                mese = (data_corrente.month - 1) if data_corrente.month > 1 else 12
            if anno is None:
                anno = data_corrente.year if data_corrente.month > 1 else data_corrente.year - 1

        # Esegui la query e crea il DataFrame
        df = pd.read_sql(query, connection, params=(mese, anno, mese, anno))

        # Log del DataFrame per debugging
        logger.info(f"DataFrame creato: {df}")

        if len(df) < 1:
            logger.warning(
                "Dati insufficienti per creare il grafico Top 5 Utenti Percentuale Accessi")
            return

        # Assicurati che la colonna 'count' sia numerica
        df['count'] = pd.to_numeric(df['count'], errors='coerce')

        # Seleziona i primi 5 utenti
        N = min(5, len(df))
        df_top_utenti = df.head(N)

        # Calcola il totale degli accessi e le percentuali
        total_accessi = df['count'].sum()
        top_utenti_counts = df_top_utenti['count'].tolist()
        altro_count = total_accessi - sum(top_utenti_counts)
        all_counts = top_utenti_counts + [altro_count]
        sizes = [count / total_accessi * 100 for count in all_counts]

        # Prepara le etichette
        labels = list(df_top_utenti['nome_utente']) + ['Altro']

        set_style()

        # Crea il grafico a torta
        fig, ax = plt.subplots(figsize=(10, 8))
        wedges, texts, autotexts = ax.pie(sizes,
                                          labels=None,
                                          colors=COLOR_PALETTE,
                                          autopct='%1.1f%%',
                                          startangle=90,
                                          pctdistance=0.75,
                                          textprops={'fontsize': 10, 'weight': 'bold', 'color': 'white'})

        # Aggiungi l'effetto ciambella
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(centre_circle)

        plt.legend(
            wedges,
            labels,
            title="Utenti",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.3, 1))

        nome_mese = get_italian_month(mese)
        plt.title(
            f'Top 5 Utenti per Percentuale di Accessi {nome_mese} {anno}',
            fontsize=14,
            fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()
        logger.info(
            f"Grafico Top 5 Utenti Percentuale Accessi salvato come {output_path}")
    except Exception as e:
        logger.error(
            f"Errore durante la creazione del grafico Top 5 Utenti Percentuale Accessi: {e}")
        raise

def create_grafici_Top20UtentiAccessi(
        logger,
        connection,
        output_path,
        query,
        mese=None,
        anno=None):
    logger.info("Creazione del grafico Top 20 Utenti Accessi")

    try:
        # Calcola mese e anno se non forniti
        if mese is None or anno is None:
            data_corrente = datetime.now()
            if mese is None:
                mese = (data_corrente.month - 1) if data_corrente.month > 1 else 12
            if anno is None:
                anno = data_corrente.year if data_corrente.month > 1 else data_corrente.year - 1

        # Esegui la query e crea il DataFrame
        df = pd.read_sql(query, connection, params=(mese, anno, mese, anno))

        # Log del DataFrame per debugging
        logger.info(f"DataFrame creato: {df}")

        if len(df) < 1:
            logger.warning(
                "Dati insufficienti per creare il grafico Top 20 Utenti Accessi")
            return

        # Assicurati che la colonna 'count' sia numerica
        df['count'] = pd.to_numeric(df['count'], errors='coerce')

        N = min(20, len(df))
        df_top_utenti = df.head(N)

        set_style()
        fig, ax = plt.subplots(figsize=(18, 10))

        bars = ax.barh(
            df_top_utenti['nome_utente'],
            df_top_utenti['count'],
            color='#202742',
            height=0.7)

        ax.set_xlabel('Numero di Accessi', fontweight='bold')

        nome_mese = get_italian_month(mese)
        ax.set_title(
            f'Numero di Accessi per Utente (Top 20) {nome_mese} {anno}',
            fontweight='bold',
            fontsize=14)

        ax.invert_yaxis()

        for bar in bars:
            width = bar.get_width()
            ax.text(width,
                    bar.get_y() + bar.get_height() / 2,
                    f'{width:.0f}',
                    ha='left',
                    va='center',
                    fontweight='bold',
                    fontsize=10,
                    color='black',
                    bbox=dict(facecolor='white',
                              edgecolor='none',
                              alpha=0.7))

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.set_yticks(range(len(df_top_utenti)))
        ax.set_yticklabels(df_top_utenti['nome_utente'])

        ax.tick_params(axis='y', which='major', pad=5, labelsize=9, left=False)

        for label in ax.yaxis.get_ticklabels():
            label.set_horizontalalignment('left')

        ax.grid(axis='x', linestyle='--', alpha=0.3)

        max_accesses = df_top_utenti['count'].max()
        ax.set_xlim(-max_accesses * 0.25, max_accesses * 1.05)

        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')

        plt.tight_layout()
        plt.subplots_adjust(left=0.25, right=0.95, top=0.95, bottom=0.05)

        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close(fig)
        logger.info(
            f"Grafico Top 20 Utenti Accessi salvato come {output_path}")
    except Exception as e:
        logger.error(
            f"Errore durante la creazione del grafico Top 20 Utenti Accessi: {e}")
        raise
