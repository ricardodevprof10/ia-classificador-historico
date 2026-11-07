
"""
Testes da Aula 21.
"""

import pytest

from observabilidade import (
    calcular_metricas,
    percentil_95
)


def criar_evento(status, latencia):
    return {
        "status": status,
        "latencia_ms": latencia
    }


def test_percentil_95():
    valores = [10, 20, 30, 40, 50]

    resultado = percentil_95(valores)

    assert resultado == pytest.approx(48.0)


def test_percentil_sem_dados():
    assert percentil_95([]) == 0.0


def test_metricas_sem_erros():
    eventos = [
        criar_evento("sucesso", 10),
        criar_evento("sucesso", 20)
    ]

    resultado = calcular_metricas(eventos)

    assert resultado["total_requisicoes"] == 2
    assert resultado["erros"] == 0
    assert resultado["taxa_erros_pct"] == 0
    assert resultado["alerta"] is False


def test_alerta_por_erros():
    eventos = [
        criar_evento("sucesso", 10),
        criar_evento("erro", 20)
    ]

    resultado = calcular_metricas(eventos)

    assert resultado["taxa_erros_pct"] == 50
    assert resultado["alerta"] is True

    assert any(
        alerta["tipo"] == "taxa_erros"
        for alerta in resultado["alertas"]
    )


def test_alerta_por_latencia():
    eventos = [
        criar_evento("sucesso", 1500),
        criar_evento("sucesso", 1600)
    ]

    resultado = calcular_metricas(eventos)

    assert resultado["alerta"] is True

    assert any(
        alerta["tipo"] == "latencia"
        for alerta in resultado["alertas"]
    )


def test_sem_eventos():
    with pytest.raises(ValueError):
        calcular_metricas([])
