import pandas as pd

def formatar_moeda(valor):
        if pd.isna(valor):
            return "-"
        
        return ( 
            f"R$ {valor:,.2f}"
            .replace(",", "X")
            .replace(".",",")
            .replace("X", ".")
        )


def preparar_tabela_principal(resultado : pd.DataFrame) -> pd.DataFrame:

    tabela = resultado[
        [
            "numero_documento",
            "cliente_fornecedor",
            "valor_esperado",
            "valor_conciliacao",
            "diferenca",
            "quantidade_movimentacoes",
            "observacao"
        ]
    ].copy()

    tabela = tabela.rename(columns={
        "numero_documento": "Documento",
        "cliente_fornecedor": "Cliente/Fornecedor",
        "valor_esperado": "Valor Esperado",
        "valor_conciliacao": "Valor Encontrado",
        "diferenca": "Diferença",
        "quantidade_movimentacoes": "Movimentações",
        "observacao": "Observação"
    })

    tabela["Movimentações"] = (
        tabela["Movimentações"]
        .astype(int)
    )
    
    sem_movimentacao = ~resultado["possui_movimentacao"]

    tabela.loc[sem_movimentacao, "Valor Encontrado"] = None
    tabela.loc[sem_movimentacao, "Diferença"] = None


    tabela["Valor Esperado"] = (
        tabela["Valor Esperado"]
        .apply(formatar_moeda)
        )

    tabela["Valor Encontrado"]=(
        tabela["Valor Encontrado"]
        .apply(formatar_moeda)
    )

    tabela["Diferença"] =(
        tabela["Diferença"]
        .apply(formatar_moeda)
    )

    return tabela