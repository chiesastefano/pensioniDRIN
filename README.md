# Ricalcolo Pensioni: 4 Proposte

Questo repository contiene il progetto per il ricalcolo delle pensioni basato su quattro diverse proposte. L'obiettivo è analizzare e simulare l'impatto delle proposte sulle pensioni, con particolare attenzione alla sostenibilità economica e all'equilibrio sociale.

## Struttura del Repository

- **`data/`**: Contiene i dati riguardati le pensioni e i redditi pensionistici del 2022
- **`graphs/`**: Include i grafici generati durante l'analisi per rappresentare i risultati
- **`ricalcolo.ipynb`**: Notebook Jupyter contenente l'analisi.
- **`riv.py`**: Modulo Python contenente le funzioni per ogni tipo di ricalcolo .

## Descrizione delle Proposte
Lo scenario base è il metodo di ricalcolo applicato dal Governo Meloni dal 2022, il quale si basa su scaglioni e percentuali di rivalutazioni differenti sulla base delle pensioni.
Le quattro proposte sono implementate nel notebook e nello script Python, ognuna con un approccio differente:

1. **Proposta 1**: Calcolo basato sull'applicazione degli scaglioni e delle percentuali del 2022, ma applicati sul reddito pensionistico invece che sulle pensioni.
2. **Proposta 2 (UMB)**: Calcolo con peso dell'inflazione cambiato in base al livello del reddito pensionistico, al livello d'inflazione stesso e alla crescita dei salari reali.
3. **Proposta 3 (FL)**: Scaglioni e percentuali differenti rispetto allo scenario base, sempre applicato sul reddito pensionistico.
4. **Proposta 4 (KD)**: Scaglioni e percentuali differenti rispetto allo scenario base, sempre applicato sul reddito pensionistico.

Per maggiori dettagli, consultare il Notebook.

## Simulazioni
Al momento le simulazioni prevedono un orizzonte di 5 anni, con inflazione al 2% (target BCE) e crescita dei salari reali allo 0%.
Lo script è scritto in modo da potere cambiare facilmente questi parametri. 
