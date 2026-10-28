import pandas as pd

from src.conciliacao import preparar_conciliacao
from src.limpeza import limpar_titulos, limpar_extrato

def criar_titulo(numero, valor):
    return pd.DataFrame([{
        "data_vencimento": pd.Timestamp("2026-10-10"),
        "numero_documento": numero,
        "cliente_fornecedor": "Cliente teste",
        "valor_esperado": valor,
        "status_sistema": "PAGO"
    }])

def criar_extrato(movimentacoes):
    return pd.DataFrame([
        {
            "data_movimento": pd.Timestamp(data),
            "numero_documento": documento,
            "descricao_historico": descricao,
            "valor_movimento": valor,
            "tipo": tipo
        }
        for data, documento, descricao, valor, tipo in movimentacoes
    ])

def test_movimentacao_valor_zero():
    titulos = criar_titulo("DOC-2001", 0.0)

    extrato = criar_extrato([
        (
            "2026-10-10",
            "DOC-2001",
            "descricao",
            0.0,
            "CREDITO"
        )
    ])

    resultado, _ = preparar_conciliacao(titulos, extrato)


    assert resultado.loc[0, "possui_movimentacao"] == True

    assert resultado.loc[0, "valor_conciliacao"] == 0.0

    assert resultado.loc[0, "diferenca"] == 0.0


def test_movimentacoes_diferentes_nao_sao_duplicadas():
    titulos= criar_titulo("DOC-2002", 250.0)

    extrato  = criar_extrato([
        (
            "2026-10-10",
            "DOC-2002",
            "PIX 1",
            100.0,
            "CREDITO"
        ),
        (
            "2026-10-11",
            "DOC-2002",
            "PIX 2",
            150.0,
            "CREDITO"
        )
    ])

    resultado, _ = preparar_conciliacao(titulos, extrato)

    assert resultado.loc[0, "quantidade_movimentacoes"] == 2

    assert resultado.loc[0, "valor_conciliacao"] == 250.0

    assert resultado.loc[0, "possui_duplicidade"] == False


def test_valor_negativo_e_preservado():
    titulos = criar_titulo("DOC-2003", 800.0)

    extrato= criar_extrato([
        (
            "2026-10-10",
            "DOC-2003",
            "PAGAMENTO",
            -800.0,
            "DEBITO"
        )
    ])

    resultado, _ = preparar_conciliacao(titulos, extrato)

    assert resultado.loc[0, "valor_conciliacao"] == 800.0

    assert extrato.loc[0, "valor_movimento"] == -800.0

    assert extrato.loc[0, "tipo"] == "DEBITO"

def test_documento_repetido_titulos():
    titulos = pd.DataFrame([
        {
            "data_vencimento": pd.Timestamp("2026-10-10"),
            "numero_documento": "DOC-2004",
            "cliente_fornecedor": "Cliente A",
            "valor_esperado": 500.0,
            "status_sistema": "PAGO"
        },

        {
            "data_vencimento": pd.Timestamp("2026-10-10"),
            "numero_documento": "DOC-2004",
            "cliente_fornecedor": "Cliente B",
            "valor_esperado": 500.0,
            "status_sistema": "PAGO"
        }
    ])

    extrato = criar_extrato([
        (
            "2026-10-10",
            "DOC-2004",
            "PIX RECEBIDO",
            500.0,
            "CREDITO"
        )
    ])

    resultado, _ = preparar_conciliacao(titulos, extrato)

    assert "documento_repetido" in resultado.columns

    assert resultado["documento_repetido"].all() == True

    assert len(resultado) == 2

    assert not resultado["possui_movimentacao"].any()



def test_documento_vazio_nao_concilia():
    titulos = criar_titulo("", 100.0)

    extrato = criar_extrato([
        (
            "2026-10-10",
            "",
            "PIX RECEBIDO",
            100.0,
            "CREDITO"
        )
    ])

    resultado, _ = preparar_conciliacao(titulos, extrato)

    assert resultado.loc[0, "possui_movimentacao"] == False

def test_documento_ausente_nao_concilia():
    titulos = criar_titulo(float("nan"), 100.0)

    extrato = criar_extrato([
        (
            "2026-10-10",
            float("nan"),
            "PIX RECEBIDO",
            100.0,
            "CREDITO"
        )
    ])

    resultado, _ = preparar_conciliacao(titulos, extrato)

    assert resultado.loc[0, "possui_movimentacao"] == False

def test_data_invalida():
    titulos = pd.DataFrame([{
        "Data_Vencimento": "31/02/2026",
        "Numero_Documento": "DOC-2005",
        "Cliente_Fornecedor": "Cliente teste",
        "Valor_Esperado": 500.0,
        "Status_Sistema": "PAGO"
    }])

    resultado = limpar_titulos(titulos)

    assert pd.isna(resultado.loc[0, "data_vencimento"])

def test_data_vazia():
        titulos = pd.DataFrame([{
            "Data_Vencimento": None,
            "Numero_Documento": "DOC-2006",
            "Cliente_Fornecedor": "Cliente teste",
            "Valor_Esperado": 500.0,
            "Status_Sistema": "PAGO"
        }])

        resultado = limpar_titulos(titulos)

        assert pd.isna(resultado.loc[0, "data_vencimento"])

def test_data_vazia_extrato():
    extrato = pd.DataFrame([{
        "Data_Movimento": None,
        "Numero_Documento": "DOC-2007",
        "Descricao_Historico": "PIX RECEBIDO",
        "Valor_Movimento": 500.0,
        "Tipo": "CREDITO"
    }])

    resultado = limpar_extrato(extrato)

    assert pd.isna(resultado.loc[0, "data_movimento"])

def test_situacao_data_extrato():
    extrato = pd.DataFrame([
        {
            "Data_Movimento": "31/02/2026",
            "Numero_Documento": "DOC-2008",
            "Descricao_Historico": "PIX RECEBIDO",
            "Valor_Movimento": 500.0,
            "Tipo": "CREDITO"
        },
        {
            "Data_Movimento": None,
            "Numero_Documento": "DOC-2009",
            "Descricao_Historico": "PIX RECEBIDO",
            "Valor_Movimento": 500.0,
            "Tipo": "CREDITO"
        },
        {
            "Data_Movimento": "10/10/2026",
            "Numero_Documento": "DOC-2010",
            "Descricao_Historico": "PIX RECEBIDO",
            "Valor_Movimento": 500.0,
            "Tipo": "CREDITO"
        }
    ])

    resultado= limpar_extrato(extrato)

    assert resultado.loc[0, "situacao_data"] == "DATA_INVALIDA"
    assert resultado.loc[1, "situacao_data"] == "DATA_AUSENTE"
    assert resultado.loc[2, "situacao_data"] == "VALIDA"


def test_datas_problematicas():
    
    extrato = pd.DataFrame({
        "Data_Movimento": ["", "32/10/2026"],
        "Numero_Documento": ["DOC-9001", "DOC-9002"],
        "Descricao_Historico": ["PIX", "TED"],
        "Valor_Movimento": [100.0, 200.0],
        "Tipo": ["CREDITO", "CREDITO"]
    })

    extrato_tratado = limpar_extrato(extrato)

    assert extrato_tratado["situacao_data"].tolist() == [
        "DATA_AUSENTE",
        "DATA_INVALIDA"
    ]


def test_data_problematica_nao_concilia():
    titulos = pd.DataFrame({
        "data_vencimento": [pd.Timestamp("2026-10-10")]
        "numero_documento": ["DOC-9003"],
        "cliente_fornecedor": ["Cliente A"],
        "valor_esperado": [100.0],
        "status_sistema" : ["ABERTO"]
    })

    extrato = pd.DataFrame({
        "data_movimento": [
            pd.Timestamp("2026-10-10"),
            pd.NaT
        ],
        "numero_documento": ["DOC-9003", "DOC-9003"],
        

