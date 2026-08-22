from pathlib import Path

import pandas as pd

def carregar():
    pd.read_excel(CAMINHO2, decimal=",")
    pd.read_csv(CAMINHO, sep=";", decimal=",", skiprows=4)
    return pd.read_excel(CAMINHO2, decimal=",")

def conferir_estrutura(df):
    print(df.shape)
    print(df.dtypes)

CAMINHO = Path(__file__).resolve().parent.parent / "bronze" / "producao_industria_2012_2025.csv"
CAMINHO2 = Path(__file__).resolve().parent.parent / "bronze" / "Dados_abertos_Consumo_Mensal.xlsx"

if __name__ == "__main__":
    conferir_estrutura(carregar())