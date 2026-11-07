
"""
Testes automatizados do monitoramento.
"""

import json

import pytest

from monitoramento import (
    calcular_psi,
    executar_monitoramento
)


def test_distribuicoes_iguais():
    referencia = ["A", "A", "B", "B"]
    atual = ["A", "A", "B", "B"]

    psi, _ = calcular_psi(
        referencia,
        atual,
        ["A", "B"]
    )

    assert psi == pytest.approx(0.0, abs=1e-8)


def test_distribuicoes_diferentes():
    referencia = ["A", "A", "B", "B"]
    atual = ["A", "A", "A", "B"]

    psi, _ = calcular_psi(
        referencia,
        atual,
        ["A", "B"]
    )

    assert psi > 0


def test_conjunto_vazio():
    with pytest.raises(ValueError):
        calcular_psi(
            [],
            ["A"],
            ["A"]
        )


def test_categoria_desconhecida():
    with pytest.raises(ValueError):
        calcular_psi(
            ["A"],
            ["B"],
            ["A"]
        )


def test_gera_relatorio(tmp_path):
    relatorio = executar_monitoramento(
        pasta_saida=str(tmp_path)
    )

    arquivo = (
        tmp_path / "relatorio_monitoramento.json"
    )

    assert arquivo.exists()

    with open(
        arquivo,
        "r",
        encoding="utf-8"
    ) as f:
        conteudo = json.load(f)

    assert "psi" in conteudo
    assert "alerta" in conteudo
    assert isinstance(conteudo["alerta"], bool)
    assert conteudo["psi"] == relatorio["psi"]
