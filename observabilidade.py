
"""
Aula 21 - Observabilidade de sistemas de IA.

Registra eventos, calcula métricas operacionais
e gera alertas automaticamente.

Projeto: Classificador histórico
"""

import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from classificador import treinar_modelo


PASTA_RELATORIOS = Path("relatorios")

ARQUIVO_LOGS = (
    PASTA_RELATORIOS / "logs_observabilidade.jsonl"
)

ARQUIVO_METRICAS = (
    PASTA_RELATORIOS / "metricas_observabilidade.json"
)

LIMITE_ERROS_PCT = 10.0
LIMITE_LATENCIA_MS = 1000.0


TEXTOS = [
    "A escola recebeu novos professores.",
    "O comércio de café cresceu.",
    "O parlamento aprovou uma lei.",
    "O museu organizou uma exposição.",
    "A universidade ampliou seus cursos.",
    "A indústria aumentou sua produção.",
    "Os partidos disputaram eleições.",
    "Os artistas apresentaram pinturas.",
    "Os estudantes receberam livros escolares."
]


def agora_utc():
    return datetime.now(timezone.utc).isoformat()


def registrar_evento(evento):
    PASTA_RELATORIOS.mkdir(
        parents=True,
        exist_ok=True
    )

    with ARQUIVO_LOGS.open(
        "a",
        encoding="utf-8"
    ) as arquivo:
        arquivo.write(
            json.dumps(
                evento,
                ensure_ascii=False
            ) + "\n"
        )


def percentil_95(valores):
    if not valores:
        return 0.0

    ordenados = sorted(valores)
    posicao = (len(ordenados) - 1) * 0.95
    inferior = int(posicao)
    superior = min(inferior + 1, len(ordenados) - 1)
    fracao = posicao - inferior

    return (
        ordenados[inferior] * (1 - fracao)
        + ordenados[superior] * fracao
    )


def processar_texto(modelo, texto, indice):
    inicio = time.perf_counter()

    evento = {
        "data_utc": agora_utc(),
        "id_requisicao": indice,
        "operacao": "classificacao",
        "status": "sucesso",
        "latencia_ms": 0.0,
        "categoria": None,
        "erro": None
    }

    try:
        if not isinstance(texto, str) or not texto.strip():
            raise ValueError(
                "Texto inválido para classificação."
            )

        categoria = modelo.predict([texto])[0]
        evento["categoria"] = str(categoria)

    except Exception as erro:
        evento["status"] = "erro"
        evento["erro"] = type(erro).__name__

    finally:
        evento["latencia_ms"] = round(
            (time.perf_counter() - inicio) * 1000,
            3
        )

        registrar_evento(evento)

    return evento


def calcular_metricas(eventos):
    total = len(eventos)

    if total == 0:
        raise ValueError(
            "Não existem eventos para analisar."
        )

    erros = sum(
        evento["status"] == "erro"
        for evento in eventos
    )

    latencias = [
        float(evento["latencia_ms"])
        for evento in eventos
    ]

    taxa_erros = (erros / total) * 100

    latencia_media = statistics.mean(latencias)
    latencia_p95 = percentil_95(latencias)

    alertas = []

    if taxa_erros > LIMITE_ERROS_PCT:
        alertas.append({
            "tipo": "taxa_erros",
            "severidade": "alta",
            "mensagem": (
                "Taxa de erros acima do limite."
            )
        })

    if latencia_p95 > LIMITE_LATENCIA_MS:
        alertas.append({
            "tipo": "latencia",
            "severidade": "media",
            "mensagem": (
                "Latência P95 acima do limite."
            )
        })

    return {
        "modelo": "classificador_historico",
        "data_utc": agora_utc(),
        "total_requisicoes": total,
        "sucessos": total - erros,
        "erros": erros,
        "taxa_erros_pct": round(taxa_erros, 2),
        "latencia_media_ms": round(
            latencia_media, 3
        ),
        "latencia_p95_ms": round(
            latencia_p95, 3
        ),
        "limite_erros_pct": LIMITE_ERROS_PCT,
        "limite_latencia_ms": LIMITE_LATENCIA_MS,
        "alerta": bool(alertas),
        "alertas": alertas,
        "ambiente": "laboratorio_sintetico"
    }


def executar_observabilidade():
    PASTA_RELATORIOS.mkdir(
        parents=True,
        exist_ok=True
    )

    # Reinicia os logs desta execução.
    ARQUIVO_LOGS.write_text(
        "",
        encoding="utf-8"
    )

    modelo = treinar_modelo()

    eventos = []

    for indice, texto in enumerate(TEXTOS, start=1):
        evento = processar_texto(
            modelo,
            texto,
            indice
        )
        eventos.append(evento)

    # Falha proposital para validar os alertas.
    eventos.append(
        processar_texto(
            modelo,
            None,
            len(TEXTOS) + 1
        )
    )

    metricas = calcular_metricas(eventos)

    with ARQUIVO_METRICAS.open(
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            metricas,
            arquivo,
            ensure_ascii=False,
            indent=2
        )

    print("OBSERVABILIDADE CONCLUÍDA")
    print("-" * 40)

    print(
        "Requisições:",
        metricas["total_requisicoes"]
    )

    print(
        "Sucessos:",
        metricas["sucessos"]
    )

    print(
        "Erros:",
        metricas["erros"]
    )

    print(
        "Taxa de erros:",
        metricas["taxa_erros_pct"],
        "%"
    )

    print(
        "Latência média:",
        metricas["latencia_media_ms"],
        "ms"
    )

    print(
        "Latência P95:",
        metricas["latencia_p95_ms"],
        "ms"
    )

    print(
        "Alerta:",
        metricas["alerta"]
    )

    print(
        "Relatório:",
        ARQUIVO_METRICAS
    )

    return metricas


if __name__ == "__main__":
    executar_observabilidade()
