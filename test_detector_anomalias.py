
"""
Testes automatizados do detector de anomalias.
"""

import json

import numpy as np
import pytest

from detector_anomalias import (
    gerar_dados_simulados,
    detectar_anomalias,
    salvar_relatorio,
)


def test_geracao_reproduzivel():
    a = gerar_dados_simulados()
    b = gerar_dados_simulados()

    assert len(a) == 103
    assert np.array_equal(a, b)


def test_detector_gera_relatorio():
    dados = gerar_dados_simulados()

    relatorio = detectar_anomalias(dados)

    assert relatorio["total_solicitacoes"] == 103
    assert relatorio["detector"] == "IsolationForest"
    assert isinstance(
        relatorio["anomalias_detectadas"],
        int
    )
    assert isinstance(
        relatorio["alerta"],
        bool
    )


def test_detector_identifica_picos():
    dados = gerar_dados_simulados()

    relatorio = detectar_anomalias(dados)

    indices = {
        item["solicitacao"]
        for item in relatorio["registros_anormais"]
    }

    assert 103 in indices


def test_entrada_insuficiente():
    with pytest.raises(ValueError):
        detectar_anomalias([100, 110, 120])


def test_entrada_invalida():
    dados = np.array(
        [100.0] * 9 + [np.nan]
    )

    with pytest.raises(ValueError):
        detectar_anomalias(dados)


def test_latencia_negativa():
    dados = np.array(
        [100.0] * 9 + [-5.0]
    )

    with pytest.raises(ValueError):
        detectar_anomalias(dados)


def test_salvar_json(tmp_path):
    dados = gerar_dados_simulados()

    relatorio = detectar_anomalias(dados)

    caminho = tmp_path / "relatorio.json"

    salvar_relatorio(
        relatorio,
        caminho
    )

    assert caminho.exists()

    with caminho.open(
        encoding="utf-8"
    ) as arquivo:
        conteudo = json.load(arquivo)

    assert conteudo["total_solicitacoes"] == 103
    assert "registros_anormais" in conteudo
