import pandas as pd

def criar_observacao(linha):
    observacoes = []

    if not linha["possui_movimentacao"]:
        observacoes.append(
            "TÍTULO SEM MOVIMENTAÇÃO IDENTIFICADA"
        )
    else:
        if linha["valor_compativel"]:
            observacoes.append(
                "VALOR COMPATÍVEL"
            )
        if linha ["valor_inferior"]:
            observacoes.append(
                "VALOR INFERIOR AO ESPERADO"
            )
        if linha ["valor_superior"]:
            observacoes.append(
                "VALOR SUPERIOR AO ESPERADO"
            )
        if linha ["multiplas_movimentacoes"]:
            observacoes.append(
                "MÚLTIPLAS MOVIMENTAÇÕES"
            )
        if linha ["possivel_duplicidade"]:
            observacoes.append(
                "POSSÍVEL DUPLICIDADE"
            )

    if not observacoes:
        observacoes.append("ANALISAR")

    return "; ".join(observacoes)

def aplicar_regras(conciliacao: pd.DataFrame) -> pd.DataFrame:
    resultado = conciliacao.copy()

    resultado["situacao"]= "ANALISAR"

    resultado.loc[
        ~resultado["possui_movimentacao"],
        "situacao"
    ] = "TÍTULO SEM MOVIMENTAÇÃO IDENTIFICADA"

    resultado["valor_compativel"]= (
        resultado["diferenca"] == 0
    )

    resultado["valor_inferior"] =(
        (resultado["diferenca"] < 0) & resultado["possui_movimentacao"]
    )

    resultado["valor_superior"] =(
        (resultado["diferenca"] > 0) & resultado["possui_movimentacao"]
    )

    resultado["multiplas_movimentacoes"] =(
        resultado["quantidade_movimentacoes"] > 1
    )

    resultado["possivel_duplicidade"]=(
        resultado["possui_duplicidade"].fillna(False)
    )

    resultado["observacao"] = resultado.apply(
        criar_observacao,
        axis=1 #executa observacao linha por linha
    )

    #datas
    resultado["movimentacao_no_vencimento"] =(
        resultado["diferenca_dias"] == 0
    )

    resultado["movimentacao_antes_vencimento"] =(
        resultado["diferenca_dias"] < 0
    )

    resultado["movimentacao_depois_vencimento"] =(
        resultado["diferenca_dias"] > 0
    )



    return resultado