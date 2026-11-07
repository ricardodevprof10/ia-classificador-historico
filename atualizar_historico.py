
"""
Aula 20 - Histórico de monitoramento de IA.
"""

import json
from pathlib import Path

PASTA = Path("relatorios")

ARQUIVO_ATUAL = (
    PASTA / "relatorio_monitoramento.json"
)

ARQUIVO_HISTORICO = (
    PASTA / "historico_monitoramento.json"
)


def atualizar_historico():
    if not ARQUIVO_ATUAL.exists():
        raise FileNotFoundError(
            "Relatório atual não encontrado."
        )

    with ARQUIVO_ATUAL.open(
        "r", encoding="utf-8"
    ) as arquivo:
        atual = json.load(arquivo)

    historico = []

    if ARQUIVO_HISTORICO.exists():
        with ARQUIVO_HISTORICO.open(
            "r", encoding="utf-8"
        ) as arquivo:
            historico = json.load(arquivo)

    if not isinstance(historico, list):
        raise ValueError(
            "O histórico deve ser uma lista."
        )

    registro = {
        "data_utc": atual["data_utc"],
        "modelo": atual["modelo"],
        "versao": atual["versao"],
        "psi": atual["psi"],
        "alerta": atual["alerta"]
    }

    historico.append(registro)

    # Manter no máximo 100 registros
    historico = historico[-100:]

    with ARQUIVO_HISTORICO.open(
        "w", encoding="utf-8"
    ) as arquivo:
        json.dump(
            historico,
            arquivo,
            ensure_ascii=False,
            indent=2
        )

    print("Histórico atualizado.")
    print("Total de registros:", len(historico))


if __name__ == "__main__":
    atualizar_historico()
