from pathlib import Path
from datetime import datetime
import json
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

BRONZE = BASE_DIR / "bronze"
PRATA = BASE_DIR / "prata"

ARQUIVO_CONSUMO = BRONZE / "Dados_abertos_Consumo_Mensal.xlsx"
ARQUIVO_PRODUCAO = PRATA / "producao_industria_2012_2025_tratada.csv"

def carregar_dados():
    consumo = pd.read_excel(ARQUIVO_CONSUMO)
    producao = pd.read_csv(ARQUIVO_PRODUCAO)

    return consumo, producao

def tratar_consumo(df):
    df = df.copy()

    linhas_antes = len(df)

    df["Data"] = pd.to_datetime(
        df["Data"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    df["DataExcel"] = pd.to_datetime(
        df["DataExcel"],
        errors="coerce"
    )

    df["Consumo"] = pd.to_numeric(
        df["Consumo"],
        errors="coerce"
    )

    df["Consumidores"] = pd.to_numeric(
        df["Consumidores"],
        errors="coerce"
    )

    df = df[df["Data"].dt.year >= 2012].copy()
    df = df[df["Data"].dt.year != 2020].copy()
    df = df[df["Data"].dt.year < 2026].copy()

    df = df.drop(
        columns=[
            "Regiao",
            "Sistema",
            "DataVersao"
        ]
    )

    df = df.drop_duplicates()

    print(f"Consumo: {linhas_antes} -> {len(df)} linhas")

    return df

def tratar_producao(df):
    df = df.copy()

    linhas_antes = len(df)

    df["Ano"] = pd.to_numeric(
        df["Ano"],
        errors="coerce"
    ).astype("Int64")

    df["Mes"] = pd.to_numeric(
        df["Mes"],
        errors="coerce"
    ).astype("Int64")

    df["Valor"] = pd.to_numeric(
        df["Valor"],
        errors="coerce"
    )

    df["Data"] = pd.to_datetime(
        df["Data"],
        errors="coerce"
    )

    print("\nValores de Local:")
    print(df["Local"].value_counts(dropna=False))

    df = df.drop(columns=["Local"])

    ausentes = df.isna().sum()

    print("\nAusentes na produção:")
    print(ausentes[ausentes > 0])

    duplicados = df.duplicated().sum()

    print(f"Duplicados exatos na produção: {duplicados}")

    df = df.drop_duplicates()

    valores_invalidos = (df["Valor"] <= 0).sum()

    print(
        f"Valores de produção menores ou iguais a zero: "
        f"{valores_invalidos}"
    )

    print("\nAnos presentes na produção:")
    print(sorted(df["Ano"].dropna().unique()))

    print(f"\nProdução: {linhas_antes} -> {len(df)} linhas")

    return df

def validar_dados(consumo, producao):

    print("\n" + "=" * 60)
    print("VALIDAÇÕES")
    print("=" * 60)

    anos_consumo = set(consumo["Data"].dt.year.dropna().unique())
    anos_producao = set(producao["Ano"].dropna().astype(int).unique())

    anos_comuns = sorted(anos_consumo & anos_producao)

    print("\nAnos comuns às duas fontes:")
    print(anos_comuns)

    print("\nAnos apenas no consumo:")
    print(sorted(anos_consumo - anos_producao))

    print("\nAnos apenas na produção:")
    print(sorted(anos_producao - anos_consumo))

    chave_producao = ["Ano", "Mes", "Atividade"]

    duplicados_chave = producao.duplicated(
        subset=chave_producao
    ).sum()

    print(
        f"\nDuplicados na chave {chave_producao}: "
        f"{duplicados_chave}"
    )

    print("\nPeríodo do consumo:")
    print(consumo["Data"].min(), "até", consumo["Data"].max())

    print("\nPeríodo da produção:")
    print(producao["Data"].min(), "até", producao["Data"].max())

def salvar_parquet(consumo, producao):

    arquivo_consumo = PRATA / "consumo_mensal.parquet"
    arquivo_producao = PRATA / "producao_industria.parquet"

    consumo.to_parquet(
        arquivo_consumo,
        index=False
    )

    producao.to_parquet(
        arquivo_producao,
        index=False
    )

    print("\nArquivos salvos:")
    print(arquivo_consumo)
    print(arquivo_producao)

    return arquivo_consumo, arquivo_producao

def registrar_proveniencia(
    consumo_antes,
    consumo_depois,
    producao_antes,
    producao_depois
):

    registro = {
        "transformado_em": datetime.now().isoformat(
            timespec="seconds"
        ),

        "fontes": {
            "consumo": ARQUIVO_CONSUMO.name,
            "producao": ARQUIVO_PRODUCAO.name
        },

        "saidas": {
            "consumo": "consumo_mensal.parquet",
            "producao": "producao_industria.parquet"
        },

        "linhas": {
            "consumo_antes": consumo_antes,
            "consumo_depois": consumo_depois,
            "producao_antes": producao_antes,
            "producao_depois": producao_depois
        },

        "decisoes": [
            "Conversão das colunas de data para datetime.",
            "Conversão das variáveis numéricas para tipos numéricos.",
            "Remoção dos registros de consumo anteriores a 2012.",
            "Remoção dos registros de consumo de 2020, "
            "pois não existem dados correspondentes na produção industrial.",
            "Remoção dos registros de consumo de 2026, "
            "pois não existem dados correspondentes na produção industrial.",
            "Remoção da coluna DataVersao do consumo por ser constante "
            "e representar a versão/data de aquisição da fonte.",
            "Remoção da coluna Local da produção por ser constante "
            "com o valor Brasil.",
            "Remoção de duplicados exatos.",
            "Valores extremos não foram removidos automaticamente."
        ]
    }

    arquivo = PRATA / "proveniencia.jsonl"

    with arquivo.open(
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            json.dumps(
                registro,
                ensure_ascii=False
            ) + "\n"
        )

    print("\nProveniência registrada em:")
    print(arquivo)

def main():

    print("=" * 60)
    print("TRATAMENTO DOS DADOS")
    print("=" * 60)

    consumo, producao = carregar_dados()

    consumo_antes = len(consumo)
    producao_antes = len(producao)

    print("\nDados carregados:")
    print(f"Consumo: {consumo.shape}")
    print(f"Produção: {producao.shape}")

    consumo = tratar_consumo(consumo)
    producao = tratar_producao(producao)

    validar_dados(
        consumo,
        producao
    )

    salvar_parquet(
        consumo,
        producao
    )

    registrar_proveniencia(
        consumo_antes,
        len(consumo),
        producao_antes,
        len(producao)
    )

    print("\nTratamento concluído.")

if __name__ == "__main__":
    main()