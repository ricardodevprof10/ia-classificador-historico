
"""
Testes automatizados do classificador histórico.
"""

import pytest

from classificador import (
    DADOS,
    criar_modelo,
    treinar_modelo,
    classificar_texto
)


@pytest.fixture(scope="module")
def modelo_treinado():
    return treinar_modelo()


def test_dataset_nao_esta_vazio():
    assert len(DADOS) > 0


def test_dataset_possui_quatro_categorias():
    categorias = {
        categoria for _, categoria in DADOS
    }

    assert categorias == {
        "Educação",
        "Economia",
        "Política",
        "Cultura"
    }


def test_pipeline_possui_etapas():
    modelo = criar_modelo()

    assert "tfidf" in modelo.named_steps
    assert "classificador" in modelo.named_steps


def test_modelo_consegue_treinar(modelo_treinado):
    assert hasattr(modelo_treinado, "classes_")


def test_classificacao_retorna_categoria_valida(
    modelo_treinado
):
    resultado = classificar_texto(
        modelo_treinado,
        "A escola recebeu novos estudantes."
    )

    categorias_validas = {
        "Educação",
        "Economia",
        "Política",
        "Cultura"
    }

    assert resultado in categorias_validas


def test_texto_vazio_gera_erro(modelo_treinado):
    with pytest.raises(ValueError):
        classificar_texto(modelo_treinado, "")


def test_texto_invalido_gera_erro(modelo_treinado):
    with pytest.raises(TypeError):
        classificar_texto(modelo_treinado, None)
