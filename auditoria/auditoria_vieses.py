
"""
Auditoria automatizada de vieses
BRITO SOLUÇÕES TECNOLOGICAS

Laboratório sintético de avaliação
de classificadores históricos.

Gera:
- Métricas por categoria
- Análise de desequilíbrio
- Matriz de confusão
- Relatório JSON
- Indicadores de atenção

Não representa auditoria do modelo
de produção.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.pipeline import make_pipeline


# ==========================================
# CONFIGURAÇÕES
# ==========================================

RAIZ = Path(__file__).resolve().parents[1]

DIRETORIO_RELATORIOS = RAIZ / "relatorios"

DIRETORIO_RELATORIOS.mkdir(
    parents=True,
    exist_ok=True
)

ARQUIVO_RELATORIO = (
    DIRETORIO_RELATORIOS
    / "relatorio_auditoria_vieses.json"
)

CATEGORIAS = [
    "Política",
    "Economia",
    "Cultura",
    "Educação",
]

LIMITE_F1 = 0.60
LIMITE_DIFERENCA_RECALL = 0.30
LIMITE_DESBALANCEAMENTO = 3.0


# ==========================================
# DADOS SINTÉTICOS
# ==========================================

politica = [
    "O governo aprovou uma nova lei.",
    "O parlamento debateu a constituição.",
    "Os deputados votaram uma reforma.",
    "O presidente anunciou um decreto.",
    "A eleição mobilizou os partidos.",
    "O ministério publicou uma decisão.",
    "O congresso discutiu a legislação.",
    "O governador sancionou o projeto.",
    "O senado aprovou uma proposta.",
    "O imperador reorganizou o governo.",
]

economia = [
    "O comércio aumentou as exportações.",
    "A inflação elevou os preços.",
    "Os trabalhadores receberam salários.",
    "A indústria expandiu a produção.",
    "O mercado registrou crescimento.",
]

cultura = [
    "O teatro apresentou uma peça.",
    "O museu inaugurou uma exposição.",
    "A música marcou o festival.",
    "A literatura influenciou artistas.",
]

educacao = [
    "A escola recebeu novos estudantes.",
    "Os professores organizaram as aulas.",
    "A universidade ampliou a biblioteca.",
]

TEXTOS_TREINO = (
    politica * 5
    + economia * 2
    + cultura
    + educacao
)

ROTULOS_TREINO = (
    ["Política"] * (len(politica) * 5)
    + ["Economia"] * (len(economia) * 2)
    + ["Cultura"] * len(cultura)
    + ["Educação"] * len(educacao)
)

TEXTOS_TESTE = [
    "O congresso nacional aprovou a reforma eleitoral.",
    "O presidente promulgou uma legislação.",
    "O parlamento discutiu o novo decreto.",
    "As exportações agrícolas cresceram no mercado.",
    "Os salários aumentaram na indústria.",
    "A inflação prejudicou o comércio.",
    "O festival apresentou música e teatro.",
    "Artistas organizaram uma exposição no museu.",
    "A literatura ganhou destaque cultural.",
    "Professores discutiram o ensino nas escolas.",
    "A universidade recebeu novos alunos.",
    "A biblioteca apoiou a educação dos estudantes.",
]

ROTULOS_TESTE = [
    "Política",
    "Política",
    "Política",
    "Economia",
    "Economia",
    "Economia",
    "Cultura",
    "Cultura",
    "Cultura",
    "Educação",
    "Educação",
    "Educação",
]


# ==========================================
# FUNÇÕES
# ==========================================

def criar_modelo():
    return make_pipeline(
        TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2)
        ),
        LogisticRegression(
            max_iter=2000,
            random_state=42
        )
    )


def calcular_distribuicao(rotulos):
    total = len(rotulos)

    return {
        categoria: {
            "quantidade": rotulos.count(categoria),
            "proporcao": round(
                rotulos.count(categoria) / total,
                4
            )
        }
        for categoria in CATEGORIAS
    }


def avaliar_desequilibrio(distribuicao):
    quantidades = [
        item["quantidade"]
        for item in distribuicao.values()
        if item["quantidade"] > 0
    ]

    if not quantidades:
        return None

    return round(
        max(quantidades) / min(quantidades),
        4
    )


def executar_auditoria():
    print("Iniciando auditoria de IA...")

    modelo = criar_modelo()

    modelo.fit(
        TEXTOS_TREINO,
        ROTULOS_TREINO
    )

    previsoes = modelo.predict(
        TEXTOS_TESTE
    )

    acuracia = accuracy_score(
        ROTULOS_TESTE,
        previsoes
    )

    f1_macro = f1_score(
        ROTULOS_TESTE,
        previsoes,
        labels=CATEGORIAS,
        average="macro",
        zero_division=0
    )

    metricas = classification_report(
        ROTULOS_TESTE,
        previsoes,
        labels=CATEGORIAS,
        output_dict=True,
        zero_division=0
    )

    matriz = confusion_matrix(
        ROTULOS_TESTE,
        previsoes,
        labels=CATEGORIAS
    )

    distribuicao = calcular_distribuicao(
        ROTULOS_TREINO
    )

    razao_desequilibrio = avaliar_desequilibrio(
        distribuicao
    )

    recalls = [
        float(metricas[categoria]["recall"])
        for categoria in CATEGORIAS
    ]

    diferenca_recall = round(
        max(recalls) - min(recalls),
        4
    )

    alertas = []

    if f1_macro < LIMITE_F1:
        alertas.append({
            "tipo": "baixo_f1_macro",
            "mensagem": (
                "O F1 macro ficou abaixo "
                "do limite configurado."
            )
        })

    if diferenca_recall > LIMITE_DIFERENCA_RECALL:
        alertas.append({
            "tipo": "diferenca_recall",
            "mensagem": (
                "Foi identificada diferença "
                "elevada de recall entre categorias."
            )
        })

    if (
        razao_desequilibrio is not None
        and razao_desequilibrio
        > LIMITE_DESBALANCEAMENTO
    ):
        alertas.append({
            "tipo": "desequilibrio_treinamento",
            "mensagem": (
                "O conjunto de treinamento "
                "apresenta desequilíbrio elevado."
            )
        })

    erros = []

    for texto, real, previsto in zip(
        TEXTOS_TESTE,
        ROTULOS_TESTE,
        previsoes
    ):
        if real != previsto:
            erros.append({
                "documento": texto,
                "categoria_real": real,
                "categoria_prevista": str(previsto)
            })

    relatorio = {
        "empresa": "BRITO SOLUÇÕES TECNOLOGICAS",
        "projeto": "Classificador histórico",
        "tipo": "auditoria_exploratoria",
        "ambiente": "laboratorio_sintetico",
        "versao_auditoria": "1.0.0",
        "data_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_treinamento": len(TEXTOS_TREINO),
        "total_teste": len(TEXTOS_TESTE),
        "categorias": CATEGORIAS,
        "acuracia": round(float(acuracia), 4),
        "f1_macro": round(float(f1_macro), 4),
        "diferenca_recall": diferenca_recall,
        "razao_desequilibrio": razao_desequilibrio,
        "distribuicao_treinamento": distribuicao,
        "metricas_por_categoria": {
            categoria: {
                "precision": round(
                    float(metricas[categoria]["precision"]),
                    4
                ),
                "recall": round(
                    float(metricas[categoria]["recall"]),
                    4
                ),
                "f1": round(
                    float(metricas[categoria]["f1-score"]),
                    4
                ),
                "suporte": int(
                    metricas[categoria]["support"]
                )
            }
            for categoria in CATEGORIAS
        },
        "matriz_confusao": matriz.tolist(),
        "erros_classificacao": erros,
        "limites": {
            "f1_macro_minimo": LIMITE_F1,
            "diferenca_recall_maxima": (
                LIMITE_DIFERENCA_RECALL
            ),
            "razao_desequilibrio_maxima": (
                LIMITE_DESBALANCEAMENTO
            )
        },
        "alerta": len(alertas) > 0,
        "quantidade_alertas": len(alertas),
        "alertas": alertas,
        "observacoes": [
            "Dados sintéticos.",
            "Modelo demonstrativo.",
            "Não representa o classificador de produção.",
            "Alertas indicam condições para investigação.",
            "Não comprovam discriminação algorítmica."
        ]
    }

    with open(
        ARQUIVO_RELATORIO,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            relatorio,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

    print("\nAuditoria concluída.")
    print("Acurácia:", relatorio["acuracia"])
    print("F1 macro:", relatorio["f1_macro"])
    print(
        "Diferença de recall:",
        relatorio["diferenca_recall"]
    )
    print(
        "Razão de desequilíbrio:",
        relatorio["razao_desequilibrio"]
    )
    print(
        "Quantidade de alertas:",
        relatorio["quantidade_alertas"]
    )
    print("Relatório:", ARQUIVO_RELATORIO)

    return relatorio


if __name__ == "__main__":
    executar_auditoria()
