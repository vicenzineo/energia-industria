import pandas as pd

def carregar():
    return pd.read_csv(CAMINHO, encoding="latin1", sep=";")

def conferir_estrutura(df):
    print(df.shape)
    print(df.dtypes)

CAMINHO = "./gastos_jundiai/bronze/despesas-detalhadas_restos_2023.csv"

if __name__ == "__main__":
    conferir_estrutura(carregar())