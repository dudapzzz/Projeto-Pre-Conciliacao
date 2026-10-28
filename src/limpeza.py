import pandas as pd

def limpar_titulos(df: pd.DataFrame) -> pd.DataFrame:


    titulos_limpos = df.copy()

    titulos_limpos= titulos_limpos.rename(columns={
        "Data_Vencimento" : "data_vencimento",
        "Numero_Documento" : "numero_documento",
        "Cliente_Fornecedor" : "cliente_fornecedor",
        "Valor_Esperado" : "valor_esperado",
        "Status_Sistema" : "status_sistema"
    }
    )

    titulos_limpos["data_vencimento"] = pd.to_datetime(
        titulos_limpos["data_vencimento"],
        format="%d/%m/%Y",
        errors="coerce" # converte valores inválidos em NaT
    )

    titulos_limpos["numero_documento"] =(
        titulos_limpos["numero_documento"]
        .astype(str)
        .str.strip()
    )

    return titulos_limpos


def limpar_extrato(df: pd.DataFrame) -> pd.DataFrame:

    extrato_limpo = df.copy()

    extrato_limpo = extrato_limpo.rename(columns={
        "Data_Movimento" : "data_movimento",
        "Numero_Documento" : "numero_documento",
        "Descricao_Historico": "descricao_historico",
        "Valor_Movimento" : "valor_movimento",
        "Tipo": "tipo"
    })

    data_original = extrato_limpo["data_movimento"]

    data_vazia= (
        data_original.isna()
        | data_original.astype("string").str.strip().eq("").fillna(False)
    )

    data_convertida = pd.to_datetime(
        data_original,
        format="%d/%m/%Y",
        errors="coerce"
    )

    extrato_limpo["situacao_data"] = "VALIDA"

    extrato_limpo.loc[data_vazia, "situacao_data"] = "DATA_AUSENTE"

    data_invalida = ~data_vazia & data_convertida.isna()
    extrato_limpo.loc[data_invalida, "situacao_data"] = "DATA_INVALIDA"
    

    extrato_limpo["data_movimento"]= pd.to_datetime(
        extrato_limpo["data_movimento"],
        format="%d/%m/%Y",
        errors="coerce"
    )
    
    extrato_limpo["numero_documento"]= (
        extrato_limpo["numero_documento"]
        .astype(str)
        .str.strip()
    )

    return extrato_limpo