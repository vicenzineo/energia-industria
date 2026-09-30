import pandas as pd


def tirar_espacos(df):
    df = df.copy()

    df.columns = df.columns.str.strip()

    for coluna in df.select_dtypes(include=["object", "string"]):
        df[coluna] = df[coluna].astype("string").str.strip()

    return df

def chave_texto(serie):
    s = serie.astype("string").str.strip().str.lower()

    s = s.str.normalize("NFKD")
    s = s.str.encode("ascii", errors="ignore")
    s = s.str.decode("utf-8")

    return s

def variacao_percentual(df, grupo, coluna_valor):
    df = df.copy()

    df["VariacaoPct"] = (
        df.groupby(grupo)[coluna_valor]
        .pct_change() * 100
    )

    return df