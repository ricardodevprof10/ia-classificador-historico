
"""
Aula 33 - Registro e versionamento de modelos
BRITO SOLUÇÕES TECNOLOGICAS

Registra modelos candidatos e promove
para homologacao apenas os aprovados
no controle automatizado de qualidade.
"""

import hashlib
import json
import os
import sys

from datetime import datetime, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent

ARTEFATOS = BASE / "artefatos_treinamento"
REGISTROS = BASE / "registro_modelos"

ARQUIVO_TREINAMENTO = (
    ARTEFATOS / "relatorio_treinamento.json"
)

ARQUIVO_QUALIDADE = (
    ARTEFATOS / "validacao_qualidade.json"
)

ARQUIVO_REGISTRO = (
    REGISTROS / "registro_modelos.json"
)


def carregar_json(caminho):
    with open(
        caminho,
        "r",
        encoding="utf-8"
    ) as arquivo:
        return json.load(arquivo)


def salvar_json(caminho, dados):
    caminho.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            dados,
            arquivo,
            indent=4,
            ensure_ascii=False
        )


def identificador_arquivo(caminho):
    hash_arquivo = hashlib.sha256()

    with open(caminho, "rb") as arquivo:
        for bloco in iter(
            lambda: arquivo.read(65536),
            b""
        ):
            hash_arquivo.update(bloco)

    return hash_arquivo.hexdigest()


def numero_valido(valor, nome):
    if isinstance(valor, bool):
        raise ValueError(
            f"{nome} nao pode ser booleano."
        )

    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise ValueError(
            f"{nome} deve ser numerico."
        )

    if not 0 <= numero <= 1:
        raise ValueError(
            f"{nome} deve estar entre 0 e 1."
        )

    return numero


def executar_registro():

    print("=" * 60)
    print("BRITO SOLUÇÕES TECNOLOGICAS")
    print("REGISTRO AUTOMATIZADO DE MODELOS")
    print("=" * 60)

    if not ARQUIVO_TREINAMENTO.exists():
        raise FileNotFoundError(
            "Relatorio de treinamento ausente."
        )

    if not ARQUIVO_QUALIDADE.exists():
        raise FileNotFoundError(
            "Relatorio de qualidade ausente."
        )

    treinamento = carregar_json(
        ARQUIVO_TREINAMENTO
    )

    qualidade = carregar_json(
        ARQUIVO_QUALIDADE
    )

    if not isinstance(treinamento, dict):
        raise ValueError(
            "Relatorio de treinamento invalido."
        )

    if not isinstance(qualidade, dict):
        raise ValueError(
            "Relatorio de qualidade invalido."
        )

    modelo = treinamento.get(
        "modelo_selecionado"
    )

    if not isinstance(modelo, str) or not modelo:
        raise ValueError(
            "Modelo selecionado ausente."
        )

    acuracia = numero_valido(
        treinamento.get(
            "acuracia_modelo_selecionado"
        ),
        "Acuracia"
    )

    f1_macro = numero_valido(
        treinamento.get(
            "f1_modelo_selecionado"
        ),
        "F1 macro"
    )

    if qualidade.get("modelo") != modelo:
        raise ValueError(
            "O modelo da validacao nao corresponde "
            "ao modelo treinado."
        )

    if qualidade.get("status") not in (
        "APROVADO",
        "REPROVADO"
    ):
        raise ValueError(
            "Status de qualidade invalido."
        )

    if qualidade.get("acuracia") != acuracia:
        raise ValueError(
            "Acuracia divergente entre relatorios."
        )

    if qualidade.get("f1_macro") != f1_macro:
        raise ValueError(
            "F1 divergente entre relatorios."
        )

    verificacoes = qualidade.get(
        "verificacoes",
        []
    )

    criterios = {
        item.get("criterio"): item.get("aprovado")
        for item in verificacoes
        if isinstance(item, dict)
    }

    esperados = {
        "acuracia_minima",
        "f1_macro_minimo",
        "regressao_f1_macro"
    }

    criterios_aprovados = (
        set(criterios) == esperados
        and all(
            criterios[criterio] is True
            for criterio in esperados
        )
    )

    aprovado = (
        qualidade["status"] == "APROVADO"
        and criterios_aprovados
        and not qualidade.get("erros")
    )

    estado = (
        "HOMOLOGADO"
        if aprovado
        else "REJEITADO"
    )

    hash_treinamento = identificador_arquivo(
        ARQUIVO_TREINAMENTO
    )

    hash_qualidade = identificador_arquivo(
        ARQUIVO_QUALIDADE
    )

    execucao = os.getenv(
        "GITHUB_RUN_ID",
        "local"
    )

    tentativa = os.getenv(
        "GITHUB_RUN_ATTEMPT",
        "1"
    )

    identificador = (
        f"{execucao}-{tentativa}-"
        f"{hash_treinamento[:12]}"
    )

    agora = datetime.now(
        timezone.utc
    ).isoformat()

    registro = {
        "id": identificador,
        "modelo": modelo,
        "versao": identificador,
        "estado": estado,
        "data_utc": agora,
        "metricas": {
            "acuracia": acuracia,
            "f1_macro": f1_macro
        },
        "qualidade": {
            "status": qualidade["status"],
            "criterios_aprovados": (
                criterios_aprovados
            )
        },
        "rastreabilidade": {
            "github_run_id": execucao,
            "github_run_attempt": tentativa,
            "github_sha": os.getenv(
                "GITHUB_SHA",
                "nao_informado"
            ),
            "sha256_treinamento": (
                hash_treinamento
            ),
            "sha256_qualidade": (
                hash_qualidade
            )
        },
        "observacao": (
            "Homologacao para testes, "
            "sem implantacao em producao."
            if aprovado
            else
            "Modelo bloqueado pelo "
            "controle de qualidade."
        )
    }

    if ARQUIVO_REGISTRO.exists():
        banco = carregar_json(
            ARQUIVO_REGISTRO
        )
    else:
        banco = {
            "empresa": (
                "BRITO SOLUÇÕES TECNOLOGICAS"
            ),
            "projeto": (
                "Classificador historico"
            ),
            "modelos": []
        }

    if not isinstance(banco, dict):
        raise ValueError(
            "Estrutura do registro invalida."
        )

    modelos = banco.get("modelos")

    if not isinstance(modelos, list):
        raise ValueError(
            "Lista de modelos invalida."
        )

    modelos = [
        item
        for item in modelos
        if isinstance(item, dict)
        and item.get("id") != identificador
    ]

    modelos.append(registro)

    banco["modelos"] = modelos
    banco["ultima_atualizacao_utc"] = agora

    salvar_json(
        ARQUIVO_REGISTRO,
        banco
    )

    print("\nModelo:", modelo)
    print("Versao:", identificador)
    print("Estado:", estado)
    print("Acuracia:", acuracia)
    print("F1 macro:", f1_macro)

    print(
        "\nRegistro salvo em:",
        ARQUIVO_REGISTRO
    )

    resumo = os.getenv(
        "GITHUB_STEP_SUMMARY"
    )

    if resumo:
        with open(
            resumo,
            "a",
            encoding="utf-8"
        ) as arquivo:
            arquivo.write(
                "## Registro de modelos\n\n"
                f"**Modelo:** {modelo}\n\n"
                f"**Versao:** {identificador}\n\n"
                f"**Estado:** {estado}\n\n"
                f"**F1 macro:** {f1_macro:.4f}\n"
            )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(
            executar_registro()
        )
    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        json.JSONDecodeError
    ) as erro:
        print(
            "Erro no registro:",
            str(erro)
        )
        sys.exit(1)
