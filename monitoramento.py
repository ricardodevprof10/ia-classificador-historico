
"""
Aula 19 - Monitoramento automatizado de IA.

Compara distribuições de categorias previstas,
calcula PSI e gera relatórios JSON.
"""

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from classificador import treinar_modelo


LIMITE_ALERTA = 0.25
VERSAO_MODELO = "1.0.0"

# Dados sintéticos para demonstrar o monitoramento
DOCUMENTOS_REFERENCIA = [
    "A escola recebeu novos professores.",
    "A universidade ampliou seus cursos.",
    "O ensino público passou por reformas.",
    "Os estudantes receberam livros escolares.",

    "O comércio de café cresceu.",
    "A indústria aumentou sua produção.",
    "Os bancos financiaram empresas.",
    "A inflação elevou os preços.",

    "O parlamento aprovou uma lei.",
    "O presidente anunciou reformas.",
    "Os partidos disputaram eleições.",
    "Os deputados debateram propostas.",

    "O museu organizou uma exposição.",
    "Os artistas apresentaram pinturas.",
    "A comunidade realizou um festival.",
    "O teatro recebeu apresentações."
]

DOCUMENTOS_ATUAIS = [
    "O parlamento aprovou uma lei.",
    "O presidente anunciou reformas.",
    "Os partidos disputaram eleições.",
    "Os deputados debateram propostas.",
    "O governo publicou um decreto.",
    "O parlamento aprovou uma lei.",
    "O presidente anunciou reformas.",
    "Os partidos disputaram eleições.",
    "Os deputados debateram propostas.",
    "O governo publicou um decreto.",

    "A escola recebeu novos professores.",
    "A universidade ampliou seus cursos.",

    "O comércio de café cresceu.",
    "A indústria aumentou sua produção.",

    "O museu organizou uma exposição.",
    "Os artistas apresentaram pinturas."
]


def calcular_psi(referencia, atual, categorias):
    """Calcula PSI entre distribuições categóricas."""

    if len(referencia) == 0 or len(atual) == 0:
        raise ValueError("Os conjuntos não podem estar vazios.")

    if not categorias:
        raise ValueError("Informe as categorias.")

    referencia = pd.Series(referencia)
    atual = pd.Series(atual)

    categorias = list(categorias)

    desconhecidas = (
        set(referencia) | set(atual)
    ) - set(categorias)

    if desconhecidas:
        raise ValueError(
            f"Categorias desconhecidas: {desconhecidas}"
        )

    p = (
        referencia.value_counts(normalize=True)
        .reindex(categorias, fill_value=0)
        .astype(float)
    )

    q = (
        atual.value_counts(normalize=True)
        .reindex(categorias, fill_value=0)
        .astype(float)
    )

    epsilon = 1e-6

    p = p + epsilon
    q = q + epsilon

    p = p / p.sum()
    q = q / q.sum()

    psi = sum(
        (valor_p - valor_q)
        * math.log(valor_p / valor_q)
        for valor_p, valor_q in zip(p, q)
    )

    distribuicoes = {
        categoria: {
            "referencia_pct": round(float(p[cat]) * 100, 4),
            "atual_pct": round(float(q[cat]) * 100, 4)
        }
        for categoria, cat in zip(categorias, categorias)
    }

    return float(psi), distribuicoes


def executar_monitoramento(
    documentos_referencia=None,
    documentos_atuais=None,
    pasta_saida="relatorios"
):
    """Executa o monitoramento e salva o relatório."""

    if documentos_referencia is None:
        documentos_referencia = DOCUMENTOS_REFERENCIA

    if documentos_atuais is None:
        documentos_atuais = DOCUMENTOS_ATUAIS

    modelo = treinar_modelo()

    previsoes_referencia = modelo.predict(
        documentos_referencia
    )

    previsoes_atuais = modelo.predict(
        documentos_atuais
    )

    categorias = list(modelo.classes_)

    psi, distribuicoes = calcular_psi(
        previsoes_referencia,
        previsoes_atuais,
        categorias
    )

    alerta = psi >= LIMITE_ALERTA

    relatorio = {
        "modelo": "classificador_historico",
        "versao": VERSAO_MODELO,
        "data_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "quantidade_referencia": len(documentos_referencia),
        "quantidade_atual": len(documentos_atuais),
        "metrica": "PSI das categorias previstas",
        "psi": round(psi, 6),
        "limite_alerta": LIMITE_ALERTA,
        "alerta": alerta,
        "distribuicoes": distribuicoes,
        "observacao": (
            "Mudança nas previsões não comprova "
            "redução da acurácia."
        )
    }

    Path(pasta_saida).mkdir(
        parents=True,
        exist_ok=True
    )

    caminho = os.path.join(
        pasta_saida,
        "relatorio_monitoramento.json"
    )

    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            relatorio,
            arquivo,
            ensure_ascii=False,
            indent=2
        )

    print("MONITORAMENTO CONCLUÍDO")
    print("-" * 40)
    print("PSI:", round(psi, 6))
    print("Limite:", LIMITE_ALERTA)
    print("Alerta:", alerta)
    print("Relatório:", caminho)

    return relatorio


if __name__ == "__main__":
    executar_monitoramento()
