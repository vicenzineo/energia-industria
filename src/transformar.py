from pathlib import Path
from datetime import datetime
import json
import pandas as pd
from limpeza import tirar_espacos, chave_texto, variacao_percentual

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

    df = tirar_espacos(df)

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

    df = df[
        (df["Data"].dt.year >= 2012) &
        (df["Data"].dt.year != 2020) &
        (df["Data"].dt.year < 2026)
    ].copy()

    df = df.drop(columns=["Regiao", "Sistema", "DataVersao", "DataExcel"])

    df = df.drop_duplicates()

    df = df.sort_values(
    ["Classe", "TipoConsumidor", "Data"]
    )

    df = variacao_percentual(
        df,
        grupo=["Classe", "TipoConsumidor"],
        coluna_valor="Consumo"
    )

    df["Ano"] = df["Data"].dt.year.astype("Int64")
    df["Mes"] = df["Data"].dt.month.astype("Int64")

    print(
        f"Consumo: {linhas_antes} -> {len(df)} linhas"
    )

    return df

def tratar_producao(df):
    df = df.copy()

    linhas_antes = len(df)

    df = tirar_espacos(df)

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

    df = df.drop(columns=["Local"])

    df = df.drop_duplicates()

    df = df.sort_values(
    ["Atividade", "Ano", "Mes"]
    )

    df = variacao_percentual(
        df,
        grupo=["Atividade"],
        coluna_valor="Valor"
    )

    print(
        f"\nProdução: {linhas_antes} -> {len(df)} linhas"
    )

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

    print("\nAusentes no consumo:")
    print(consumo.isna().sum()[consumo.isna().sum() > 0])

    print("\nAusentes na produção:")
    print(producao.isna().sum()[producao.isna().sum() > 0])

    print("\nConsistência temporal do consumo:")

    inconsistencias = (
        (consumo["Data"].dt.year != consumo["Ano"]) |
        (consumo["Data"].dt.month != consumo["Mes"])
    ).sum()

    print(
        f"Registros com inconsistência entre Data, Ano e Mes: "
        f"{inconsistencias}"
    )

    print("\nConsistência temporal da produção:")

    inconsistencias = (
        (producao["Data"].dt.year != producao["Ano"]) |
        (producao["Data"].dt.month != producao["Mes"])
    ).sum()

    print(
        f"Registros com inconsistência entre Data, Ano e Mes: "
        f"{inconsistencias}"
    )

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
        "atributos_derivados": [
        {
            "nome": "VariacaoPct",
            "fonte": "consumo",
            "calculo": "Variação percentual do Consumo em relação à observação anterior do mesmo grupo.",
            "grupo": ["Classe", "TipoConsumidor"]
        },
        {
            "nome": "VariacaoPct",
            "fonte": "producao",
            "calculo": "Variação percentual do Valor em relação à observação anterior da mesma atividade.",
            "grupo": ["Atividade"]
        }
        ],
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
            "Remoção da coluna DataExcel do consumo por ser equivalente a Data",
            "Remoção da coluna Local da produção por ser constante "
            "com o valor Brasil.",
            "Remoção de duplicados exatos.",
            "Valores extremos não foram removidos automaticamente.",
            "Padronização de espaços em nomes de colunas e valores textuais.",
            "Criação dos atributos derivados de variação percentual.",
            "Criação das colunas Ano e Mes a partir da data do consumo.",
            "Variação percentual calculada dentro de cada grupo temporal.",
            "Os valores textuais de Classe, TipoConsumidor e Atividade foram verificados e não apresentaram inconsistências que justificassem a criação de chaves ou mapas de padronização.",
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