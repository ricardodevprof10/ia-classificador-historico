
"""
Curso completo de Inteligência Artificial
Aula 24 - Detector automatizado de anomalias

BRITO SOLUÇÕES TECNOLOGICAS
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.ensemble import IsolationForest


PASTA_RELATORIOS = Path("relatorios")
ARQUIVO_RELATORIO = (
    PASTA_RELATORIOS / "relatorio_anomalias.json"
)


def gerar_dados_simulados(semente=42):
    """
    Gera latências fictícias para laboratório.

    Não representa tráfego real de produção.
    """
    rng = np.random.default_rng(semente)

    normais = rng.normal(
        loc=100,
        scale=12,
        size=100
    )

    normais = np.maximum(normais, 1)

    picos = np.array([
        480.0,
        650.0,
        900.0
    ])

    return np.concatenate([normais, picos])


def detectar_anomalias(latencias):
    """
    Identifica observações incomuns.

    Retorna um relatório em formato de dicionário.
    """
    valores = np.asarray(
        latencias,
        dtype=float
    )

    if valores.ndim != 1:
        raise ValueError(
            "As latências devem formar uma lista."
        )

    if len(valores) < 10:
        raise ValueError(
            "São necessárias pelo menos "
            "10 observações."
        )

    if not np.all(np.isfinite(valores)):
        raise ValueError(
            "Existem valores inválidos."
        )

    if np.any(valores < 0):
        raise ValueError(
            "Latências não podem ser negativas."
        )

    modelo = IsolationForest(
        n_estimators=100,
        contamination=0.03,
        random_state=42
    )

    entrada = valores.reshape(-1, 1)

    previsoes = modelo.fit_predict(entrada)

    pontuacoes = modelo.decision_function(
        entrada
    )

    anomalias = []

    for indice, previsao in enumerate(previsoes):
        if previsao == -1:
            anomalias.append({
                "solicitacao": indice + 1,
                "latencia_ms": round(
                    float(valores[indice]),
                    3
                ),
                "pontuacao": round(
                    float(pontuacoes[indice]),
                    6
                )
            })

    quantidade = len(anomalias)
    total = len(valores)

    return {
        "modelo": "classificador_historico",
        "detector": "IsolationForest",
        "versao_detector": "1.0.0",
        "data_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "ambiente": "laboratorio_sintetico",
        "total_solicitacoes": total,
        "anomalias_detectadas": quantidade,
        "percentual_anomalias": round(
            quantidade / total * 100,
            2
        ),
        "latencia_media_ms": round(
            float(np.mean(valores)),
            3
        ),
        "latencia_p95_ms": round(
            float(np.percentile(valores, 95)),
            3
        ),
        "alerta": quantidade > 0,
        "registros_anormais": anomalias
    }


def salvar_relatorio(relatorio, caminho):
    caminho = Path(caminho)

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with caminho.open(
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            relatorio,
            arquivo,
            ensure_ascii=False,
            indent=2
        )


def main():
    print("INICIANDO DETECÇÃO DE ANOMALIAS")
    print("-" * 45)

    latencias = gerar_dados_simulados()

    relatorio = detectar_anomalias(
        latencias
    )

    salvar_relatorio(
        relatorio,
        ARQUIVO_RELATORIO
    )

    print(
        "Solicitações analisadas:",
        relatorio["total_solicitacoes"]
    )

    print(
        "Anomalias detectadas:",
        relatorio["anomalias_detectadas"]
    )

    print(
        "Percentual:",
        relatorio["percentual_anomalias"],
        "%"
    )

    print(
        "Alerta:",
        relatorio["alerta"]
    )

    print(
        "Relatório:",
        ARQUIVO_RELATORIO
    )

    print("-" * 45)
    print("DETECÇÃO CONCLUÍDA")


if __name__ == "__main__":
    main()
