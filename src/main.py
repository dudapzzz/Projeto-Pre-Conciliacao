import pandas as pd

from src.limpeza import limpar_titulos, limpar_extrato
from src.conciliacao import (preparar_conciliacao, movimentacoes_sem_titulo)
from src.regras import aplicar_regras
from src.apresentacao import preparar_tabela_principal



titulos_sem_tratamento= pd.read_csv(
    "data/titulo_ficticio.csv",
    sep=";"
)

extrato_sem_tratamento = pd.read_csv(
    "data/extrato_ficticio.csv",
    sep=";"
)

titulos_tratados = limpar_titulos(titulos_sem_tratamento)

extrato_tratado = limpar_extrato(extrato_sem_tratamento)


#so p testar:
# Confere como as datas do extrato foram classificadas.
print("\nConferência das situações das datas:")

print(
    extrato_tratado[
        ["data_movimento", "numero_documento", "situacao_data"]
    ].to_string(index=False)
)

# Conta quantas movimentações existem em cada situação.
print("\nQuantidade por situação:")

print(extrato_tratado["situacao_data"].value_counts(dropna=False))


resultado, movimentacoes_data_problematica = preparar_conciliacao(
    titulos_tratados,
    extrato_tratado
)

movimentacoes_sem_titulo_result= movimentacoes_sem_titulo(
    titulos_tratados,
    extrato_tratado
)
resultado = aplicar_regras(resultado)

tabela_principal = preparar_tabela_principal(resultado)

teste_1005 = resultado[
    resultado["numero_documento"] == "DOC-1005"
].iloc[0]

print("\nTeste específico do DOC-1005:")

print(teste_1005[
    [
        "numero_documento",
        "valor_esperado",
        "valor_conciliacao",
        "diferenca",
        "quantidade_movimentacoes",
        "possui_duplicidade",
        "valor_compativel",
        "valor_inferior",
        "valor_superior",
        "multiplas_movimentacoes",
        "possivel_duplicidade",
        "movimentacao_antes_vencimento",
        "movimentacao_no_vencimento",
        "movimentacao_depois_vencimento",
        "observacao"
    ]
].to_string())

print("Resultado da conciliação:")
print(
    resultado[
        [
            "numero_documento",
            "data_vencimento",
            # "cliente_fornecedor",
            # "valor_esperado",
            # "valor_conciliacao",
            # "diferenca",
            # "quantidade_movimentacoes",
            "primeira_data_movimentacao",
            "diferenca_dias",
            # "tipos_movimentacoes",
            # "possui_duplicidade",
            # "possui_movimentacao",
            # "situacao",
            # "valor_compativel",
            # "valor_inferior",
            # "valor_superior",
            # "multiplas_movimentacoes",
            # "possui_duplicidade",
            # "possui_movimentacao",
            # "observacao",
            "movimentacao_no_vencimento",
            "movimentacao_antes_vencimento",
            "movimentacao_depois_vencimento"
            
        ]
    ]
)
print("\n")
print("Movimentações sem título:")
print(movimentacoes_sem_titulo_result[
    [
        "data_movimento",
        "numero_documento",
        "descricao_historico",
        "valor_movimento",
        "tipo"
    ]
])

print("/n Tabela principal:")
print(tabela_principal.to_string(index=False))

print("\n Movimentações com data ausente ou inválida - revisão manual!!:")

print(
    movimentacoes_data_problematica[
        [
            "data_movimento",
            "numero_documento",
            "descricao_historico",
            "valor_movimento",
            "tipo",
            "situacao_data"
        ]
    ].to_string(index=False)
)