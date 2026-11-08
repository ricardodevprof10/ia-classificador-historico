
"""
Aula 34 - Monitoramento e retreinamento
BRITO SOLUÇÕES TECNOLOGICAS

Analisa o PSI do classificador historico
e determina se um novo treinamento
deve ser solicitado.

O PSI e um indicador de mudanca de
distribuicao, nao de perda de acuracia.
"""

import json
import math
import os
import sys
import urllib.error
import urllib.request

from datetime import datetime, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent

PASTA_SAIDA = BASE / "artefatos_retreinamento"

PASTA_SAIDA.mkdir(
    parents=True,
    exist_ok=True
)

ARQUIVO_DECISAO = (
    PASTA_SAIDA /
    "decisao_retreinamento.json"
)

URL_MONITORAMENTO = (
    "https://raw.githubusercontent.com/"
    "ricardodevprof10/"
    "ia-classificador-historico/"
    "main/relatorios/"
    "relatorio_monitoramento.json"
)

LIMITE_PADRAO = 0.25


def buscar_relatorio():
    requisicao = urllib.request.Request(
        URL_MONITORAMENTO,
        headers={
            "User-Agent": (
                "BRITO-MLOps-Monitoramento"
            )
        }
    )

    with urllib.request.urlopen(
        requisicao,
        timeout=20
    ) as resposta:
        conteudo = resposta.read().decode(
            "utf-8"
        )

    return json.loads(conteudo)


def buscar_campo(dados, nomes):
    """
    Procura um campo em objetos JSON aninhados.
    """

    if isinstance(dados, dict):
        for nome in nomes:
            if nome in dados:
                return dados[nome]

        for valor in dados.values():
            resultado = buscar_campo(
                valor,
                nomes
            )

            if resultado is not None:
                return resultado

    elif isinstance(dados, list):
        for item in dados:
            resultado = buscar_campo(
                item,
                nomes
            )

            if resultado is not None:
                return resultado

    return None


def converter_numero(valor, nome):
    if isinstance(valor, bool):
        raise ValueError(
            f"{nome} nao pode ser booleano."
        )

    numero = float(valor)

    if not math.isfinite(numero):
        raise ValueError(
            f"{nome} deve ser finito."
        )

    if numero < 0:
        raise ValueError(
            f"{nome} nao pode ser negativo."
        )

    return numero


def salvar_decisao(dados):
    with open(
        ARQUIVO_DECISAO,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def executar():

    print("=" * 60)
    print("BRITO SOLUÇÕES TECNOLOGICAS")
    print("ANALISE AUTOMATIZADA DE RETREINAMENTO")
    print("=" * 60)

    decisao = {
        "empresa": (
            "BRITO SOLUÇÕES TECNOLOGICAS"
        ),
        "projeto": "Classificador historico",
        "data_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "fonte": URL_MONITORAMENTO,
        "status": "ERRO",
        "retreinamento_necessario": False,
        "psi_atual": None,
        "limite_psi": None,
        "motivo": "",
        "erro": None
    }

    try:
        relatorio = buscar_relatorio()

        if not isinstance(relatorio, dict):
            raise ValueError(
                "O relatorio deve ser um objeto JSON."
            )

        psi_bruto = buscar_campo(
            relatorio,
            [
                "psi_atual",
                "psi_total",
                "psi",
                "valor_psi"
            ]
        )

        limite_bruto = buscar_campo(
            relatorio,
            [
                "limite_psi",
                "psi_limite",
                "threshold_psi",
                "limiar_psi"
            ]
        )

        if psi_bruto is None:
            raise ValueError(
                "Campo PSI nao encontrado. "
                "Verifique a estrutura do relatorio."
            )

        psi = converter_numero(
            psi_bruto,
            "PSI"
        )

        if limite_bruto is None:
            limite = LIMITE_PADRAO
        else:
            limite = converter_numero(
                limite_bruto,
                "Limite PSI"
            )

        if limite <= 0:
            raise ValueError(
                "O limite PSI deve ser positivo."
            )

        necessita = psi > limite

        decisao["psi_atual"] = psi
        decisao["limite_psi"] = limite

        decisao["retreinamento_necessario"] = (
            necessita
        )

        if necessita:
            decisao["status"] = (
                "REAVALIACAO_NECESSARIA"
            )

            decisao["motivo"] = (
                "PSI acima do limite. "
                "Retreinamento experimental "
                "e nova avaliacao recomendados."
            )
        else:
            decisao["status"] = (
                "MONITORAMENTO_ESTAVEL"
            )

            decisao["motivo"] = (
                "PSI dentro do limite. "
                "Nenhum retreinamento solicitado."
            )

    except (
        ValueError,
        TypeError,
        KeyError,
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError
    ) as erro:
        decisao["erro"] = str(erro)
        decisao["motivo"] = (
            "Nao foi possivel avaliar o drift. "
            "O retreinamento automatico "
            "foi interrompido."
        )

    salvar_decisao(decisao)

    print(
        "\nStatus:",
        decisao["status"]
    )

    print(
        "PSI:",
        decisao["psi_atual"]
    )

    print(
        "Limite:",
        decisao["limite_psi"]
    )

    print(
        "Motivo:",
        decisao["motivo"]
    )

    print(
        "Relatorio:",
        ARQUIVO_DECISAO
    )

    caminho_saida = os.getenv(
        "GITHUB_OUTPUT"
    )

    if caminho_saida:
        with open(
            caminho_saida,
            "a",
            encoding="utf-8"
        ) as arquivo:
            arquivo.write(
                "retreinar="
                + str(
                    decisao[
                        "retreinamento_necessario"
                    ]
                ).lower()
                + "\n"
            )

    caminho_resumo = os.getenv(
        "GITHUB_STEP_SUMMARY"
    )

    if caminho_resumo:
        with open(
            caminho_resumo,
            "a",
            encoding="utf-8"
        ) as arquivo:
            arquivo.write(
                "## Monitoramento de IA\n\n"
                f"**Status:** {decisao['status']}\n\n"
                f"**PSI:** {decisao['psi_atual']}\n\n"
                f"**Limite:** {decisao['limite_psi']}\n\n"
                f"**Motivo:** {decisao['motivo']}\n"
            )

    if decisao["status"] == "ERRO":
        print(
            "\nERRO:",
            decisao["erro"]
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(
        executar()
    )
