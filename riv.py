import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


# Funzione per pulire i dati rimuovendo punti e virgole e convertendo in float
def pulisci_dati(colonna):
    return colonna.replace({r'\.': '', ',': '.'}, regex=True).astype(float)
#scenario

#funzioni

#baseline: rivalutazioen attuale
#proposta1: rivaluto in base al reddito pensionistico
#proposta 2: rivaluto in base al reddito pensionistico + cambiare la % di rivalutazione così come da schema
#proposta 3: FL
#Porposta 4: King Dati https://www.umbertobertonelli.it/nel-partito-che-vorrei/?doing_wp_cron=1733857743.5291359424591064453125#chapter-1


def rivalutazione(df, inflazione):
    """
    Calcola l'importo rivalutato in base a intervalli di 'Upper_bound' e a un tasso di inflazione.
    Per la prima fascia, la rivalutazione è del 100% dell'inflazione, successivamente decresce.
    Parametri:
    ----------
    df : Tabella con i dati già puliti
    inflazione : Tasso di inflazione (%).
    """
    df_2=df.copy()
    df_2.loc[df['Upper_bound'] <= 2101.52, 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 1.00 / 100)
    df_2.loc[(df['Upper_bound'] > 2101.52) & (df_2['Upper_bound'] <= 2626.90), 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.85 / 100)
    df_2.loc[(df['Upper_bound'] > 2626.90) & (df_2['Upper_bound'] <= 3152.28), 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.53 / 100)
    df_2.loc[(df['Upper_bound'] > 3152.28) & (df_2['Upper_bound'] <= 4203.04), 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.47 / 100)
    df_2.loc[(df['Upper_bound'] > 4203.04) & (df_2['Upper_bound'] <= 5253.80), 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.37 / 100)
    df_2.loc[df['Upper_bound'] > 5253.80, 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.32 / 100)
    return df_2

def rivalutazione_umb(df, inflazione, crescita, mediana=0.80, min60mediana=1.00):
    # Inflazione > 2%
    if inflazione > 2:
        df.loc[df['Upper_bound'] <= 1050.76, 'Importo rivalutato'] = df['Importo complessivo'] * (1 + inflazione * 1.00 / 100)  # Uguale ad oggi
        df.loc[(df['Upper_bound'] > 1050.76) & (df['Upper_bound'] <= 1576.14), 'Importo rivalutato'] = (
            df['Importo complessivo'] * min60mediana * (1 + inflazione * 1.00 / 100) +
            df['Importo complessivo'] * (1 - min60mediana) * (1 + inflazione * 1.00 / 100)  # Assumiamo che parte dei dati sia sotto e sopra il 60% della mediana
        )
        df.loc[(df['Upper_bound'] > 1576.14) & (df['Upper_bound'] <= 2101.52), 'Importo rivalutato'] = (
            df['Importo complessivo'] * mediana * (1 + inflazione * 1.00 / 100) +
            df['Importo complessivo'] * (1 - mediana) * (1 + (min(inflazione * 1.00, crescita) / 100))  # Assumiamo che parte dei dati sia sotto e sopra la mediana
        )
        df.loc[(df['Upper_bound'] > 2101.52) & (df['Upper_bound'] <= 2626.90), 'Importo rivalutato'] = df['Importo complessivo'] * (1 + min(inflazione * 0.85, crescita) / 100)
        df.loc[(df['Upper_bound'] > 2626.90) & (df['Upper_bound'] <= 3152.28), 'Importo rivalutato'] = df['Importo complessivo'] * (1 + min(inflazione * 0.53, crescita) / 100)
        df.loc[(df['Upper_bound'] > 3152.28) & (df['Upper_bound'] <= 4203.04), 'Importo rivalutato'] = df['Importo complessivo'] * (1 + min(inflazione * 0.47, crescita) / 100)
        df.loc[(df['Upper_bound'] > 4203.04) & (df['Upper_bound'] <= 5253.80), 'Importo rivalutato'] = df['Importo complessivo'] * (1 + min(inflazione * 0.37, crescita) / 100)
        df.loc[df['Upper_bound'] > 5253.80, 'Importo rivalutato'] = df['Importo complessivo'] * (1 + min(inflazione * 0.32, crescita) / 100)

    # Inflazione < 2%
    else:
        df.loc[df['Upper_bound'] <= 1050.76, 'Importo rivalutato'] = df['Importo complessivo'] * (1 + inflazione * 1.00 / 100)
        df.loc[(df['Upper_bound'] > 1050.76) & (df['Upper_bound'] <= 1576.14), 'Importo rivalutato'] = (
            df['Importo complessivo'] * min60mediana * (1 + inflazione * 1.00 / 100) +
            df['Importo complessivo'] * (1 - min60mediana) * (1 + min(inflazione * 1.00, crescita) / 100)
        )
        df.loc[(df['Upper_bound'] > 1576.14) & (df['Upper_bound'] <= 2101.52), 'Importo rivalutato'] = (
            df['Importo complessivo'] * mediana * (1 + min(inflazione * 1.00, crescita) / 100) +
            df['Importo complessivo'] * (1 - mediana) * (1 + min(inflazione * 1.00, crescita) / 100)
        )
        df.loc[(df['Upper_bound'] > 2101.52) & (df['Upper_bound'] <= 2626.90), 'Importo rivalutato'] = df['Importo complessivo'] * (1 + min(inflazione * 0.85, crescita))
        df.loc[(df['Upper_bound'] > 2626.90) & (df['Upper_bound'] <= 3152.28), 'Importo rivalutato'] = df['Importo complessivo'] * (1 + min(inflazione * 0.53, crescita))
        df.loc[(df['Upper_bound'] > 3152.28) & (df['Upper_bound'] <= 4203.04), 'Importo rivalutato'] = df['Importo complessivo'] * (1 + min(inflazione * 0.47, crescita))
        df.loc[(df['Upper_bound'] > 4203.04) & (df['Upper_bound'] <= 5253.80), 'Importo rivalutato'] = df['Importo complessivo'] * (1 + min(inflazione * 0.37, crescita))
        df.loc[df['Upper_bound'] > 5253.80, 'Importo rivalutato'] = df['Importo complessivo'] * (1 + min(inflazione * 0.32, crescita))

    return df

