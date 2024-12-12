import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def pulisci_dati(colonna):
    """
    Pulisce i dati rimuovendo punti e virgole all'interno del df.
    """
    return colonna.replace({r'\.': '', ',': '.'}, regex=True).astype(float)


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
    df_2.loc[(df['Upper_bound'] > 2101.52) & (df_2['Upper_bound'] <= 2626.90), 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.85 / 100) # Rivalutazione al 85%
    df_2.loc[(df['Upper_bound'] > 2626.90) & (df_2['Upper_bound'] <= 3152.28), 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.53 / 100) # Rivalutazione al 53%
    df_2.loc[(df['Upper_bound'] > 3152.28) & (df_2['Upper_bound'] <= 4203.04), 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.47 / 100) # Rivalutazione al 47%
    df_2.loc[(df['Upper_bound'] > 4203.04) & (df_2['Upper_bound'] <= 5253.80), 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.37 / 100) # Rivalutazione al 37%
    df_2.loc[df['Upper_bound'] > 5253.80, 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.32 / 100)
    return df_2

def rivalutazione_umb(df, inflazione, crescita, mediana=0.80, min60mediana=1.00):
    """
    Calcola l'importo rivalutato in base a intervalli di 'Upper_bound' e a un tasso di inflazione.
    Per la prima fascia, la rivalutazione è del 100% dell'inflazione, successivamente decresce.
    Parametri:
    ----------
    df : Tabella con i dati già puliti
    inflazione : Tasso di inflazione (%).
    crescita : Tasso di crescita (%).
    mediana : Percentuale di pensionati appartenenti alla categoria [1576.14 <= 2101.52] che consideriamo sotto la mediana (default 0.80).
    min60mediana : Percentuale di pensionati appartenenti alla categoria [1050.76 <= 1576.14] che consideriamo sotto il 60% della mediana (default 1.00).
    """
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
        # Rivalutazione al 85% dell'inflazione con cap dei salari reali
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

def rivalutazione_fl(df, inflazione):
    """
    Calcola l'importo rivalutato in base a intervalli di 'Upper_bound' e a un tasso di inflazione.
    Per la prima fascia, la rivalutazione è del 100% dell'inflazione, successivamente decresce.
    Parametri:
    ----------
    df : Tabella con i dati già puliti
    inflazione : Tasso di inflazione.
    """
    df_2=df.copy()
    df_2.loc[df['Upper_bound'] <= 1576.14, 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 1.00 / 100) # Rivalutazione al 100%
    df_2.loc[(df['Upper_bound'] > 1576.14) & (df_2['Upper_bound'] <= 2101.52), 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.50 / 100) # Rivalutazione a metà
    df_2.loc[df['Upper_bound'] > 2101.52, 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.00 / 100) # Non rivalutare se superiore a 2101.52
    return df_2

def rivalutazione_nl(df, inflazione):
    """
    Calcola l'importo rivalutato in base a intervalli di 'Upper_bound' e a un tasso di inflazione.
    Per la prima fascia, la rivalutazione è del 100% dell'inflazione, successivamente decresce.
    Parametri:
    ----------
    df : Tabella con i dati già puliti
    inflazione : Tasso di inflazione.
    """
    df_2=df.copy()
    df_2.loc[df['Upper_bound'] <= 1050.76, 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 1.00 / 100)
    df_2.loc[(df['Upper_bound'] > 1050.76) & (df_2['Upper_bound'] <= 1576.14), 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.80 / 100)
    df_2.loc[(df['Upper_bound'] > 1576.14) & (df_2['Upper_bound'] <= 2626.90), 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.60 / 100)
    df_2.loc[(df['Upper_bound'] > 2626.90) & (df_2['Upper_bound'] <= 3152.28), 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.40 / 100)
    df_2.loc[(df['Upper_bound'] > 3152.28) & (df_2['Upper_bound'] <= 4203.04), 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.20 / 100)
    df_2.loc[df['Upper_bound'] > 4203.04, 'Importo rivalutato'] = df_2['Importo complessivo'] * (1 + inflazione * 0.00 / 100)
    return df_2


def plot_importo_per_categoria(dataframe,
                               colore='#ffd957',
                               titolo='Importo per Categoria',
                               xlabel='Categoria',
                               ylabel='Importo (Miliardi)'):
    """
    Crea un grafico a barre che mostra l'importo per categoria in miliardi.

    Parametri:
    - dataframe: DataFrame pandas contenente le colonne 'Categoria' e 'Importo Rivalutato'
    - colore: colore delle barre (default giallo)
    - titolo: titolo del grafico
    - xlabel: etichetta asse x
    - ylabel: etichetta asse y
    """
    import matplotlib.pyplot as plt

    # Crea il grafico
    plt.figure(figsize=(12, 6))

    # Converti importi in miliardi
    importi_miliardi = dataframe['Importo rivalutato'] / 10 ** 9

    # Crea il grafico a barre
    plt.bar(dataframe['Categoria'],
            importi_miliardi,
            color=colore,
            edgecolor='gray')

    # Personalizza il grafico
    plt.xlabel(xlabel, fontsize=12, fontweight='bold')
    plt.ylabel(ylabel, fontsize=12, fontweight='bold')
    plt.title(titolo, fontsize=15, fontweight='bold')
    plt.xticks(rotation=45, ha='right')

    # Rimuovi notazione scientifica
    plt.ticklabel_format(style='plain', axis='y')

    # Aggiungi griglia
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Regola il layout
    plt.tight_layout()

    # Mostra il grafico
    plt.show()

# Esempio di utilizzo
# plot_importo_per_categoria(rivalutazione_pensionati)





