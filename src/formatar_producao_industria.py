import csv
import pandas as pd
from pathlib import Path


# ============================================================
# 1. CAMINHOS DOS ARQUIVOS
# ============================================================

arquivo_bronze = Path(
    "bronze/producao_industria_2012_2025.csv"
)

arquivo_silver = Path(
    "prata/producao_industria_2012_2025_tratada.csv"
)

# Cria a pasta Silver caso ela ainda não exista
arquivo_silver.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. LEITURA DO ARQUIVO ORIGINAL
# ============================================================

with open(
    arquivo_bronze,
    "r",
    encoding="utf-8-sig",
    newline=""
) as arquivo:

    leitor = csv.reader(
        arquivo,
        delimiter=";"
    )

    linhas = list(leitor)


# ============================================================
# 3. IDENTIFICAÇÃO DAS LINHAS DA FONTE
# ============================================================

# Linha 4: meses
linha_meses = linhas[3]

# Linha 5: atividades industriais
linha_atividades = linhas[4]

# Linha 6: valores do Brasil
linha_valores = linhas[5]


# ============================================================
# 4. IDENTIFICAR OS MESES
# ============================================================

meses = []

for coluna, valor in enumerate(linha_meses):

    valor = valor.strip()

    if valor:
        meses.append(
            (coluna, valor)
        )


# ============================================================
# 5. DICIONÁRIO DOS MESES
# ============================================================

meses_pt = {
    "janeiro": 1,
    "fevereiro": 2,
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12
}


# ============================================================
# 6. TRANSFORMAÇÃO PARA FORMATO LONGO
# ============================================================

registros = []

for coluna_inicial, mes in meses:

    # Cada mês possui 27 atividades
    atividades = linha_atividades[
        coluna_inicial:coluna_inicial + 27
    ]

    valores = linha_valores[
        coluna_inicial:coluna_inicial + 27
    ]

    for atividade, valor in zip(
        atividades,
        valores
    ):

        atividade = atividade.strip()
        valor = valor.strip()

        # Ignora células sem atividade
        if not atividade:
            continue

        # Valores ausentes
        if valor in [
            "",
            "-",
            "...",
            "..",
            "X"
        ]:

            valor_numerico = pd.NA

        else:

            try:

                # Converte:
                # 1.234,56 -> 1234.56

                valor_numerico = float(
                    valor
                    .replace(".", "")
                    .replace(",", ".")
                )

            except ValueError:

                valor_numerico = pd.NA

        registros.append({
            "Local": "Brasil",
            "Data_original": mes,
            "Atividade": atividade,
            "Valor": valor_numerico
        })


# ============================================================
# 7. CRIAR DATAFRAME
# ============================================================

dados = pd.DataFrame(
    registros
)


# ============================================================
# 8. SEPARAR MÊS E ANO
# ============================================================

dados[
    ["NomeMes", "Ano"]
] = dados[
    "Data_original"
].str.split(
    " ",
    n=1,
    expand=True
)


# Padronizar nome do mês

dados["NomeMes"] = (
    dados["NomeMes"]
    .str.lower()
    .str.strip()
)


# Converter ano para número

dados["Ano"] = pd.to_numeric(
    dados["Ano"],
    errors="coerce"
).astype("Int64")


# ============================================================
# 9. CONVERTER NOME DO MÊS PARA NÚMERO
# ============================================================

dados["Mes"] = (
    dados["NomeMes"]
    .map(meses_pt)
    .astype("Int64")
)


# ============================================================
# 10. CRIAR DATA
# ============================================================

dados["Data"] = pd.to_datetime(
    dados["Ano"].astype("string")
    + "-"
    + dados["Mes"].astype("string")
    + "-01",
    errors="coerce"
)


# ============================================================
# 11. REMOVER COLUNAS AUXILIARES
# ============================================================

dados = dados[
    [
        "Local",
        "Data",
        "Ano",
        "Mes",
        "Atividade",
        "Valor"
    ]
]


# ============================================================
# 12. GARANTIR TIPO NUMÉRICO
# ============================================================

dados["Valor"] = pd.to_numeric(
    dados["Valor"],
    errors="coerce"
)


# ============================================================
# 13. ORDENAR OS DADOS
# ============================================================

dados = dados.sort_values(
    by=[
        "Data",
        "Atividade"
    ]
).reset_index(
    drop=True
)


# ============================================================
# 14. SALVAR NA CAMADA SILVER
# ============================================================

dados.to_csv(
    arquivo_silver,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 15. MOSTRAR RESULTADO
# ============================================================

print("Tratamento concluído.")

print(
    f"Arquivo original: {arquivo_bronze}"
)

print(
    f"Arquivo tratado: {arquivo_silver}"
)

print(
    f"Quantidade de registros: {len(dados):,}"
)

print(
    f"Quantidade de colunas: {len(dados.columns)}"
)

print()

print("Período:")

print(
    f"{dados['Data'].min()} "
    f"até "
    f"{dados['Data'].max()}"
)

print()

print(
    "Quantidade de atividades:",
    dados["Atividade"].nunique()
)

print()

print("Primeiros registros:")

print(
    dados.head(10).to_string(
        index=False
    )
)