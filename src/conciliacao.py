import pandas as pd

def juntar_tipos(tipos):
        return ", ".join(tipos)

def preparar_conciliacao(
    titulos: pd.DataFrame,
    extrato: pd.DataFrame
) -> pd.DataFrame:
    extrato_copia = extrato.copy()

    contagem_documentos = titulos["numero_documento"].value_counts()

    documentos_repetidos = contagem_documentos[
        contagem_documentos > 1
    ].index

    titulos_copia= titulos.copy()

    titulos_copia["documento_repetido"] = (
        titulos_copia["numero_documento"].isin(documentos_repetidos)
    )

    extrato_copia["valor_conciliacao"] =(
        extrato_copia["valor_movimento"].abs()
        #o abs transforma os valores - em positivo. Para a conciliação, precisamos que todos os valores sejam positivos para que possamos comparar corretamente com os títulos a pagar e a receber.
   )

    duplicados = extrato_copia.duplicated(
        subset=[
            "data_movimento",
            "numero_documento",
            "descricao_historico",
            "valor_movimento",
            "tipo"
        ],
        
        keep=False
        #serve para marcar todos os duplicados como True, e não apenas o primeiro ou o último
   )

    extrato_copia["eh_duplicado"] = duplicados

    #Função que responde qual o valor movimentado para cada dcumento
    total_extrato = (
        extrato_copia
        .groupby("numero_documento")
        .agg(
            valor_conciliacao = ("valor_conciliacao", "sum"),
            quantidade_movimentacoes=("numero_documento", "count"),
            primeira_data_movimentacao=("data_movimento", "min"),
            tipos_movimentacoes=("tipo", juntar_tipos),
            possui_duplicidade=("eh_duplicado", "any")
        )
        .reset_index() #serve para transformar em dataframe para fazer o merge com os titulos
    )

    titulos_com_documento= titulos_copia[
        titulos_copia["numero_documento"].notna() 
        & titulos_copia["numero_documento"].astype(str).str.strip().ne("")
    ].copy()

    extrato_com_documento = total_extrato[
        total_extrato["numero_documento"].notna()
        & total_extrato["numero_documento"].astype(str).str.strip().ne("")
    ].copy()

    conciliacao_identificados = titulos_com_documento.merge(
        extrato_com_documento,
        on="numero_documento",
        how="left"
    )

    titulos_sem_documento = titulos_copia[
        titulos_copia["numero_documento"].isna()
        | titulos_copia["numero_documento"].astype(str).str.strip().eq("")
    ].copy()

    titulos_sem_documento["valor_conciliacao"] = float("nan")
    titulos_sem_documento["quantidade_movimentacoes"] = float("nan")
    titulos_sem_documento["primeira_data_movimentacao"] = pd.NaT
    titulos_sem_documento["tipos_movimentacoes"] = None
    titulos_sem_documento["possui_duplicidade"] = False
    
    conciliacao = pd.concat(
        [conciliacao_identificados, titulos_sem_documento],
        ignore_index=True
    )

    documentos_ambiguos = conciliacao["documento_repetido"].fillna(False)

    conciliacao.loc[documentos_ambiguos, "valor_conciliacao"] = float("nan")
    conciliacao.loc[documentos_ambiguos, "quantidade_movimentacoes"] = float("nan")
    conciliacao.loc[documentos_ambiguos, "primeira_data_movimentacao"] = pd.NaT
    conciliacao.loc[documentos_ambiguos, "tipos_movimentacoes"] = None
    conciliacao.loc[documentos_ambiguos, "possui_duplicidade"] = False

    conciliacao["valor_conciliacao"] =(
        conciliacao["valor_conciliacao"]
        .fillna(0)
    )

    conciliacao["quantidade_movimentacoes"]=(
        conciliacao["quantidade_movimentacoes"].fillna(0)
    )

    conciliacao["possui_movimentacao"]=(
        conciliacao["quantidade_movimentacoes"] > 0
    )

    conciliacao["diferenca"] =(
        conciliacao["valor_conciliacao"] - conciliacao["valor_esperado"] 
    )

    conciliacao["diferenca_dias"] =(
        conciliacao["primeira_data_movimentacao"] - conciliacao["data_vencimento"]
    ).dt.days # converte a diferença de datas em dias

    return conciliacao

def movimentacoes_sem_titulo(
    titulos: pd.DataFrame,
    extrato: pd.DataFrame
    ) -> pd.DataFrame:

    documentos_titulos= set(
        titulos["numero_documento"]
    )

    movimentacoes_sem_titulo = extrato[
        ~extrato["numero_documento"].isin(documentos_titulos)
    ].copy()

    return movimentacoes_sem_titulo