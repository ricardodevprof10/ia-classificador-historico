
"""
Aula 32 - Controle automatizado de qualidade
BRITO SOLUÇÕES TECNOLOGICAS

Valida métricas de modelos de IA
e bloqueia resultados que não atendem
aos critérios mínimos estabelecidos.
"""

import json
import math
import os
import sys

from datetime import datetime, timezone
from pathlib import Path


# ============================================
# CONFIGURAÇÕES
# ============================================

BASE = Path(__file__).resolve().parent.parent

PASTA_ARTEFATOS = (
    BASE / "artefatos_treinamento"
)

PASTA_ARTEFATOS.mkdir(
    parents=True,
    exist_ok=True
)

CAMINHO_RELATORIO = (
    PASTA_ARTEFATOS /
    "relatorio_treinamento.json"
)

CAMINHO_VALIDACAO = (
    PASTA_ARTEFATOS /
    "validacao_qualidade.json"
)

CAMINHO_REFERENCIA = (
    BASE /
    "config" /
    "referencia_modelo.json"
)

LIMITE_ACURACIA = 0.60
LIMITE_F1 = 0.60
QUEDA_MAXIMA_F1 = 0.05


# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def carregar_json(caminho):
    with open(
        caminho,
        "r",
        encoding="utf-8"
    ) as arquivo:
        return json.load(arquivo)


def salvar_json(caminho, dados):
    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def validar_numero(valor, nome):
    if isinstance(valor, bool):
        raise ValueError(
            f"{nome} não pode ser booleano."
        )

    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise ValueError(
            f"{nome} deve ser numérico."
        )

    if not math.isfinite(numero):
        raise ValueError(
            f"{nome} deve ser finito."
        )

    if not 0 <= numero <= 1:
        raise ValueError(
            f"{nome} deve estar entre 0 e 1."
        )

    return numero


# ============================================
# VALIDAÇÃO
# ============================================

def executar_validacao():

    print("=" * 60)
    print("BRITO SOLUÇÕES TECNOLOGICAS")
    print("CONTROLE AUTOMATIZADO DE QUALIDADE")
    print("=" * 60)

    verificacoes = []
    erros = []

    modelo = "Não identificado"
    acuracia = None
    f1 = None
    f1_referencia = None

    try:
        if not CAMINHO_RELATORIO.exists():
            raise FileNotFoundError(
                "Relatório de treinamento não encontrado."
            )

        relatorio = carregar_json(
            CAMINHO_RELATORIO
        )

        if not isinstance(relatorio, dict):
            raise ValueError(
                "O relatório deve ser um objeto JSON."
            )

        modelo = relatorio.get(
            "modelo_selecionado"
        )

        if not isinstance(modelo, str) or not modelo:
            raise ValueError(
                "Modelo selecionado não identificado."
            )

        acuracia = validar_numero(
            relatorio.get(
                "acuracia_modelo_selecionado"
            ),
            "Acurácia"
        )

        f1 = validar_numero(
            relatorio.get(
                "f1_modelo_selecionado"
            ),
            "F1 macro"
        )

        # Critério 1: acurácia.
        verificacoes.append({
            "criterio": "acuracia_minima",
            "valor": acuracia,
            "limite": LIMITE_ACURACIA,
            "aprovado": (
                acuracia >= LIMITE_ACURACIA
            )
        })

        # Critério 2: F1 macro.
        verificacoes.append({
            "criterio": "f1_macro_minimo",
            "valor": f1,
            "limite": LIMITE_F1,
            "aprovado": (
                f1 >= LIMITE_F1
            )
        })

        # Critério 3: regressão de desempenho.
        if not CAMINHO_REFERENCIA.exists():
            raise FileNotFoundError(
                "Arquivo de referência não encontrado."
            )

        referencia = carregar_json(
            CAMINHO_REFERENCIA
        )

        if not isinstance(referencia, dict):
            raise ValueError(
                "A referência deve ser um objeto JSON."
            )

        f1_referencia = validar_numero(
            referencia.get("f1_macro"),
            "F1 macro de referência"
        )

        queda = f1_referencia - f1

        verificacoes.append({
            "criterio": "regressao_f1_macro",
            "valor": float(queda),
            "limite": QUEDA_MAXIMA_F1,
            "aprovado": (
                queda <= QUEDA_MAXIMA_F1
            )
        })

    except (
        OSError,
        ValueError,
        TypeError,
        json.JSONDecodeError
    ) as erro:
        erros.append(str(erro))

    aprovado = (
        len(verificacoes) == 3
        and all(
            item["aprovado"]
            for item in verificacoes
        )
        and not erros
    )

    status = (
        "APROVADO"
        if aprovado
        else "REPROVADO"
    )

    resultado = {
        "empresa": "BRITO SOLUÇÕES TECNOLOGICAS",
        "tipo": "controle_qualidade_modelo",
        "data_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "modelo": modelo,
        "acuracia": acuracia,
        "f1_macro": f1,
        "f1_referencia": f1_referencia,
        "status": status,
        "verificacoes": verificacoes,
        "erros": erros,
        "limites": {
            "acuracia_minima": LIMITE_ACURACIA,
            "f1_macro_minimo": LIMITE_F1,
            "queda_maxima_f1": QUEDA_MAXIMA_F1
        }
    }

    salvar_json(
        CAMINHO_VALIDACAO,
        resultado
    )

    print("\nModelo:", modelo)
    print("Status:", status)

    for item in verificacoes:
        situacao = (
            "APROVADO"
            if item["aprovado"]
            else "REPROVADO"
        )

        print(
            item["criterio"],
            "|",
            situacao,
            "| valor:",
            round(item["valor"], 4)
        )

    for erro in erros:
        print("ERRO:", erro)

    print(
        "\nRelatório:",
        CAMINHO_VALIDACAO
    )

    # Publica o resultado no resumo do GitHub.
    caminho_resumo = os.getenv(
        "GITHUB_STEP_SUMMARY"
    )

    if caminho_resumo:
        linhas = [
            "## Controle de qualidade de IA",
            "",
            f"**Modelo:** {modelo}",
            f"**Status:** {status}",
            "",
            "| Critério | Resultado |",
            "|---|---|"
        ]

        for item in verificacoes:
            situacao = (
                "Aprovado"
                if item["aprovado"]
                else "Reprovado"
            )

            linhas.append(
                f"| {item['criterio']} | "
                f"{situacao} |"
            )

        for erro in erros:
            linhas.append(
                f"\nErro: {erro}"
            )

        with open(
            caminho_resumo,
            "a",
            encoding="utf-8"
        ) as arquivo:
            arquivo.write(
                "\n".join(linhas) + "\n"
            )

    return 0 if aprovado else 1


if __name__ == "__main__":
    sys.exit(
        executar_validacao()
    )
