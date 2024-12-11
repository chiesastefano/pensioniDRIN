import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Impostazioni per visualizzare tutte le colonne e righe
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)

# Funzione per pulire i dati rimuovendo punti e virgole e convertendo in float
def pulisci_dati(colonna):
    return colonna.replace({r'\.': '', ',': '.'}, regex=True).astype(float)

# Carica i dati dal file Excel per pensionati
pensionati = pd.read_excel('/Users/umbertobertonelli/PycharmProjects/pensioni/dati_pensioni_per_pensionato.xlsx')

# Rimuovi le colonne inutili e limita i dati
del pensionati['Unnamed: 0']
del pensionati['Unnamed: 2']
pensionati = pensionati[0:51]

# Pulisci le colonne 'Importo complessivo' e 'Pensionati'
pensionati['Importo complessivo'] = pulisci_dati(pensionati['Importo complessivo'])
pensionati['Pensionati'] = pulisci_dati(pensionati['Pensionati'])

# Carica i dati dal file Excel per pensioni
pensioni = pd.read_excel('/Users/umbertobertonelli/PycharmProjects/pensioni/dati_pensioni_per_pensione.xlsx')
del pensioni['Unnamed: 0.1']

# Rinominare la colonna e combinare i dati per la categoria
pensioni = pensioni.rename(columns={'Unnamed: 0': 'Categoria'})
pensioni['Categoria'] = pensioni['Classi di importo mensile'] + " " + pensioni['Categoria']
del pensioni['Classi di importo mensile']
pensioni = pensioni[0:51]

# Pulisci le colonne 'Importo complessivo' e 'Numero di'
pensioni['Importo complessivo'] = pulisci_dati(pensioni['Importo complessivo'])
pensioni['Numero di'] = pulisci_dati(pensioni['Numero di'])
# Supponendo che il tuo dataframe sia chiamato df
pensioni['Ultimo valore'] = pensioni['Categoria'].str.extract(r'(\d+,\d+)$').fillna(method='ffill')

# Converting the extracted values from string to float for any further analysis
pensioni['Ultimo valore'] = pensioni['Ultimo valore'].str.replace(',', '.').astype(float)

pensionati['Ultimo valore'] = pensionati['Categoria'].str.extract(r'(\d+,\d+)$').fillna(method='ffill')

# Converting the extracted values from string to float for any further analysis
pensionati['Ultimo valore'] = pensionati['Ultimo valore'].str.replace(',', '.').astype(float)


def rivalutazione_pensioni(df, ultimo_valore, inflazione):
    # Definiamo le condizioni per ogni fascia di rivalutazione
    condizioni = [
        (df[ultimo_valore] <= 2101.52),
        (df[ultimo_valore] > 2101.52) & (df[ultimo_valore] <= 2626.90),
        (df[ultimo_valore] > 2626.90) & (df[ultimo_valore] <= 3152.28),
        (df[ultimo_valore] > 3152.28) & (df[ultimo_valore] <= 4203.04),
        (df[ultimo_valore] > 4203.04) & (df[ultimo_valore] <= 5253.80),
        (df[ultimo_valore] > 5253.80)
    ]

    # Definiamo i valori di rivalutazione corrispondenti a ciascuna fascia
    valori_rivalutazione = [
        1 + inflazione,  # Rivalutazione completa per importi <= 2101.52
        1 + inflazione * 0.85,  # Rivalutazione del 85% per importi > 2101.52 e <= 2626.90
        1 + inflazione * 0.53,  # Rivalutazione del 53% per importi > 2626.90 e <= 3152.28
        1 + inflazione * 0.47,  # Rivalutazione del 47% per importi > 3152.28 e <= 4203.04
        1 + inflazione * 0.37,  # Rivalutazione del 37% per importi > 4203.04 e <= 5253.80
        1 + inflazione * 0.32  # Rivalutazione del 32% per importi > 5253.80
    ]

    dfp=df.copy()

    # Applichiamo la rivalutazione a seconda delle condizioni
    dfp['Rivalutazione'] = np.select(condizioni, valori_rivalutazione, default=1)

    # Calcoliamo l'importo rivalutato
    dfp['Importo rivalutato'] = dfp['Importo complessivo'] * dfp['Rivalutazione']

    return dfp


def rivalutazione_reddito_pensionistico(df, ultimo_valore, inflazione, crescita_salari, reddito_complessivo_annuo):
    # Funzione per calcolare la rivalutazione per ogni riga
    def calcola_rivalutazione(riga):
        # Definiamo le condizioni di rivalutazione per la singola riga
        if riga[ultimo_valore] <= 2101.52:
            rivalutazione = 1 + inflazione
        elif 2101.52 < riga[ultimo_valore] <= 2626.90:
            rivalutazione = 1 + inflazione * 0.85
        elif 2626.90 < riga[ultimo_valore] <= 3152.28:
            rivalutazione = 1 + inflazione * 0.53
        elif 3152.28 < riga[ultimo_valore] <= 4203.04:
            rivalutazione = 1 + inflazione * 0.47
        elif 4203.04 < riga[ultimo_valore] <= 5253.80:
            rivalutazione = 1 + inflazione * 0.37
        else:
            rivalutazione = 1 + inflazione * 0.32

        # Inflazione > 2% e reddito complessivo < 24.000€
        if inflazione > 0.02 and riga[reddito_complessivo_annuo] < 24000:
            return rivalutazione
        # Inflazione > 2% e reddito complessivo >= 24.000€
        elif inflazione > 0.02 and riga[reddito_complessivo_annuo] >= 24000:
            return min(rivalutazione, 1 + crescita_salari)
        # Inflazione <= 2% e reddito complessivo < 14.000€
        elif inflazione <= 0.02 and riga[reddito_complessivo_annuo] < 14000:
            return rivalutazione
        # Inflazione <= 2% e reddito complessivo >= 14.000€
        else:
            return min(rivalutazione, 1 + crescita_salari)

    # Applichiamo la funzione di calcolo a ogni riga del DataFrame
    df['Rivalutazione'] = df.apply(calcola_rivalutazione, axis=1)

    # Calcoliamo l'importo rivalutato
    df['Importo rivalutato'] = df['Importo complessivo'] * df['Rivalutazione']

    return df


# Ciclo sugli scenari
inflazioni = np.arange(0.02, 0.09, 0.02)  # Inflazione dal 2% all'8%
crescita_salari = np.arange(0.01, 0.04, 0.01)  # Crescita dei salari dall'1% al 3%
dati_rivalutazioni = []
for inflazione in inflazioni:
    for crescita in crescita_salari:
        # Rivalutazione standard
        df_rivalutato_standard = rivalutazione_pensioni(pensionati.copy(), 'Ultimo valore', inflazione)
        costo_standard = df_rivalutato_standard['Importo rivalutato'].sum()

        # Rivalutazione personalizzata
        df_rivalutato_personalizzato = rivalutazione_reddito_pensionistico(pensionati.copy(), 'Ultimo valore', inflazione, crescita, 'Importo complessivo')
        costo_personalizzato = df_rivalutato_personalizzato['Importo rivalutato'].sum()

        # Creazione del grafico combinato con due subplot
        fig = make_subplots(rows=2, cols=1, subplot_titles=("Importi rivalutati per categoria: LB2022 VS Proposta, Pensioni 2022, basata su dati Itnerari Prevideniali (XI Rapporto)", "Costi della Rivalutazione"))

        # Grafico per rivalutazione (standard e personalizzata) sul primo subplot
        fig.add_trace(go.Bar(
            x=df_rivalutato_standard['Categoria'],
            y=df_rivalutato_standard['Importo rivalutato'],
            name='Rivalutazione LB 2022'
        ), row=1, col=1)

        fig.add_trace(go.Bar(
            x=df_rivalutato_personalizzato['Categoria'],
            y=df_rivalutato_personalizzato['Importo rivalutato'],
            name='Rivalutazione Proposta'
        ), row=1, col=1)

        # Grafico dei costi (standard e personalizzata) sul secondo subplot
        fig.add_trace(go.Bar(
            x=['Standard'],
            y=[costo_standard - pensioni['Importo complessivo'].sum()],
            name='Costo Rivalutazione LB 2022'
        ), row=2, col=1)

        fig.add_trace(go.Bar(
            x=['Proposta'],
            y=[costo_personalizzato - pensioni['Importo complessivo'].sum()],
            name='Costo Rivalutazione Proposta'
        ), row=2, col=1)
        fig.add_trace(go.Bar(
            x=['Risparmio'],
            y=[-costo_personalizzato + costo_standard],
            name='Risparmio'
        ), row=2, col=1)

        # Aggiornamento del layout
        fig.update_layout(
            title_text=f'Scenario: Inflazione {inflazione*100:.0f}% - Crescita Salari {crescita*100:.0f}%',
            showlegend=True,
            height=1200,
            barmode='group'
        )

        # Visualizza il grafico combinato
        fig.show()

        # Stampa del costo della rivalutazione
        print(f"Costo rivalutazione standard per inflazione {inflazione*100:.0f}% e crescita salari {crescita*100:.0f}%: {costo_standard - pensioni['Importo complessivo'].sum()}")
        print(f"Costo rivalutazione personalizzata per inflazione {inflazione*100:.0f}% e crescita salari {crescita*100:.0f}%: {costo_personalizzato - pensioni['Importo complessivo'].sum()}")
        print(f"Risparmio: {costo_personalizzato - costo_standard}")
        risparmio = costo_personalizzato - costo_standard

        # Salva i dati nell'elenco
        dati_rivalutazioni.append({
            'Inflazione': inflazione,
            'Crescita salari': crescita,
            'Costo standard': costo_standard - pensioni['Importo complessivo'].sum(),
            'Costo personalizzato': costo_personalizzato - pensioni['Importo complessivo'].sum(),
            'Risparmio': -risparmio
        })


