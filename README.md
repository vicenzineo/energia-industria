Alertas da producao da industria:
Local tem constante Brasil em todos, pode ser descartada.
Atividade é distribuída uniformemente

Alertas do consumo mensal:
DataVersao tem um valor constante "2026-07-17 00:00:00" que pode ser retirado.
Consumidores tem alta correlação com Consumo
Regiao e Sistema tem alta correlação

Os dados começam em 2004, mas os dados da fonte primária começam em 2012. Pode-se apagar os dados anteriores a 2012.
Além disso, na produção da indústria não há o ano de 2020. Pode-se também retirar o deste ano.
E no consumo há o ano de 2026, que não existe na producao.
Como os dados da producao não estão separados por estado, as colunas Regiao e Sistema serão retiradas.
Data e DataExcel de consumo também fornecem as mesmas informações, assim, DataExcel será removida.

Atributos derivados

Durante a etapa de transformação dos dados, foram criados atributos derivados para representar a variação temporal das variáveis analisadas.

VariacaoPct

Representa a variação percentual do valor em relação à observação temporal anterior dentro de cada grupo.

Consumo de energia:
Calculada sobre a coluna Consumo, agrupando as observações por Classe e TipoConsumidor.

Produção industrial:
Calculada sobre a coluna Valor, agrupando as observações por Atividade.

A fórmula utilizada é:

VariacaoPct = ((valor_atual / valor_anterior) - 1) × 100

A primeira observação de cada grupo não possui uma observação anterior e, portanto, não possui uma variação percentual calculável.

O atributo foi criado para permitir a análise da evolução temporal do consumo de energia elétrica e da produção industrial, contribuindo posteriormente para a investigação da relação entre essas duas fontes de dados.
