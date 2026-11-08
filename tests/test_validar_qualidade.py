
"""
Testes automatizados da Aula 32
BRITO SOLUÇÕES TECNOLOGICAS
"""

import importlib.util
from pathlib import Path

import pytest


BASE = Path(__file__).resolve().parent.parent

ARQUIVO = (
    BASE /
    "scripts" /
    "validar_qualidade.py"
)

spec = importlib.util.spec_from_file_location(
    "validar_qualidade_aula32",
    ARQUIVO
)

modulo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(modulo)


def test_numero_valido():
    assert modulo.validar_numero(
        0.75,
        "F1"
    ) == 0.75


def test_numero_negativo():
    with pytest.raises(ValueError):
        modulo.validar_numero(
            -0.1,
            "F1"
        )


def test_numero_acima_de_um():
    with pytest.raises(ValueError):
        modulo.validar_numero(
            1.5,
            "Acurácia"
        )


def test_numero_infinito():
    with pytest.raises(ValueError):
        modulo.validar_numero(
            float("inf"),
            "F1"
        )


def test_booleano_invalido():
    with pytest.raises(ValueError):
        modulo.validar_numero(
            True,
            "F1"
        )


def test_aprovacao(
    tmp_path,
    monkeypatch
):
    pasta = tmp_path / "artefatos"
    pasta.mkdir()

    referencia = (
        tmp_path /
        "referencia.json"
    )

    modulo.salvar_json(
        referencia,
        {"f1_macro": 0.70}
    )

    modulo.salvar_json(
        pasta / "relatorio_treinamento.json",
        {
            "modelo_selecionado": "SVM_Linear",
            "acuracia_modelo_selecionado": 0.80,
            "f1_modelo_selecionado": 0.75
        }
    )

    monkeypatch.setattr(
        modulo,
        "CAMINHO_RELATORIO",
        pasta / "relatorio_treinamento.json"
    )

    monkeypatch.setattr(
        modulo,
        "CAMINHO_VALIDACAO",
        pasta / "validacao_qualidade.json"
    )

    monkeypatch.setattr(
        modulo,
        "CAMINHO_REFERENCIA",
        referencia
    )

    monkeypatch.delenv(
        "GITHUB_STEP_SUMMARY",
        raising=False
    )

    codigo = modulo.executar_validacao()

    assert codigo == 0

    resultado = modulo.carregar_json(
        pasta / "validacao_qualidade.json"
    )

    assert resultado["status"] == "APROVADO"


def test_reprovacao(
    tmp_path,
    monkeypatch
):
    pasta = tmp_path / "artefatos"
    pasta.mkdir()

    referencia = (
        tmp_path /
        "referencia.json"
    )

    modulo.salvar_json(
        referencia,
        {"f1_macro": 0.70}
    )

    modulo.salvar_json(
        pasta / "relatorio_treinamento.json",
        {
            "modelo_selecionado": "Naive_Bayes",
            "acuracia_modelo_selecionado": 0.50,
            "f1_modelo_selecionado": 0.45
        }
    )

    monkeypatch.setattr(
        modulo,
        "CAMINHO_RELATORIO",
        pasta / "relatorio_treinamento.json"
    )

    monkeypatch.setattr(
        modulo,
        "CAMINHO_VALIDACAO",
        pasta / "validacao_qualidade.json"
    )

    monkeypatch.setattr(
        modulo,
        "CAMINHO_REFERENCIA",
        referencia
    )

    monkeypatch.delenv(
        "GITHUB_STEP_SUMMARY",
        raising=False
    )

    codigo = modulo.executar_validacao()

    assert codigo == 1

    resultado = modulo.carregar_json(
        pasta / "validacao_qualidade.json"
    )

    assert resultado["status"] == "REPROVADO"
