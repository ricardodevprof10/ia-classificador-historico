
"""
Aula 31 - Pipeline automatizado de machine learning
BRITO SOLUÇÕES TECNOLOGICAS

Treinamento e avaliação automatizados
de classificadores de documentos históricos.

Os documentos são sintéticos e servem
exclusivamente para fins didáticos.
"""

import hashlib
import json
import os
import platform
import sys

from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
import sklearn

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


# ============================================
# CONFIGURAÇÕES
# ============================================

BASE = Path(__file__).resolve().parent.parent

PASTA_SAIDA = BASE / "artefatos_treinamento"
PASTA_SAIDA.mkdir(
    parents=True,
    exist_ok=True
)

SEMENTE = 42
LIMITE_F1 = 0.60

# Para a aula, um resultado abaixo do limite
# gera reprovação de qualidade, mas não
# interrompe o workflow.
#
# Para exigir aprovação em um ambiente
# controlado, configure a variável
# STRICT_QUALITY_GATE=true.

CONTROLE_RIGOROSO = (
    os.getenv(
        "STRICT_QUALITY_GATE",
        "false"
    ).lower() == "true"
)


# ============================================
# CORPUS SINTÉTICO
# ============================================

DOCUMENTOS = {
    "Política": [
        "O parlamento aprovou uma constituição.",
        "O governo publicou um decreto imperial.",
        "Os deputados discutiram uma lei eleitoral.",
        "O presidente anunciou uma reforma política.",
        "A assembleia votou uma proposta legislativa.",
        "O senado debateu direitos constitucionais.",
        "O ministro apresentou medidas administrativas.",
        "Os partidos participaram da eleição.",
        "O governador sancionou a legislação.",
        "A monarquia reorganizou o poder político.",
        "O congresso debateu a representação popular.",
        "O gabinete ministerial discutiu novas leis."
    ],
    "Economia": [
        "O comércio ampliou as exportações agrícolas.",
        "A inflação elevou os preços dos alimentos.",
        "Os trabalhadores reivindicaram salários.",
        "A indústria aumentou a produção nacional.",
        "O mercado financeiro registrou crescimento.",
        "A agricultura impulsionou a economia regional.",
        "As importações afetaram a balança comercial.",
        "O banco financiou atividades industriais.",
        "A arrecadação tributária aumentou.",
        "O setor produtivo enfrentou uma crise.",
        "A produção de café estimulou as exportações.",
        "Os comerciantes negociaram mercadorias."
    ],
    "Cultura": [
        "O teatro apresentou uma peça histórica.",
        "A música popular marcou o festival.",
        "O museu inaugurou uma exposição artística.",
        "A literatura influenciou escritores brasileiros.",
        "As tradições culturais foram preservadas.",
        "Os artistas organizaram um espetáculo musical.",
        "A pintura retratou costumes regionais.",
        "O patrimônio cultural recebeu reconhecimento.",
        "O cinema apresentou produções nacionais.",
        "A dança integrou manifestações populares.",
        "A poesia expressou experiências culturais.",
        "O festival reuniu artistas e músicos."
    ],
    "Educação": [
        "A escola ampliou o acesso à alfabetização.",
        "Os professores organizaram novas aulas.",
        "A universidade inaugurou uma biblioteca.",
        "O ensino público passou por reformas.",
        "Os estudantes participaram de atividades escolares.",
        "A educação básica recebeu investimentos.",
        "O currículo escolar incluiu novas disciplinas.",
        "A formação docente recebeu atenção.",
        "Os alunos frequentaram cursos de história.",
        "A instituição educacional desenvolveu pesquisas.",
        "A escola promoveu atividades pedagógicas.",
        "Os professores avaliaram a aprendizagem."
    ]
}


# ============================================
# PREPARAÇÃO DOS DADOS
# ============================================

def preparar_dados():
    textos = []
    categorias = []

    for categoria, documentos in DOCUMENTOS.items():
        for documento in documentos:
            textos.append(documento)
            categorias.append(categoria)

    dados_identidade = json.dumps(
        {
            "textos": textos,
            "categorias": categorias
        },
        ensure_ascii=False,
        sort_keys=True
    )

    hash_dataset = hashlib.sha256(
        dados_identidade.encode("utf-8")
    ).hexdigest()

    (
        x_treino,
        x_teste,
        y_treino,
        y_teste
    ) = train_test_split(
        textos,
        categorias,
        test_size=0.25,
        random_state=SEMENTE,
        stratify=categorias
    )

    return {
        "x_treino": x_treino,
        "x_teste": x_teste,
        "y_treino": y_treino,
        "y_teste": y_teste,
        "hash_dataset": hash_dataset,
        "total": len(textos)
    }


# ============================================
# CLASSIFICADORES
# ============================================

def criar_modelos():
    return {
        "Regressao_Logistica": LogisticRegression(
            max_iter=2000,
            random_state=SEMENTE
        ),
        "Naive_Bayes": MultinomialNB(),
        "SVM_Linear": LinearSVC(
            random_state=SEMENTE
        )
    }


# ============================================
# AVALIAÇÃO
# ============================================

def avaliar_modelo(
    nome,
    estimador,
    dados
):
    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2)
            )
        ),
        (
            "classificador",
            estimador
        )
    ])

    pipeline.fit(
        dados["x_treino"],
        dados["y_treino"]
    )

    previsoes = pipeline.predict(
        dados["x_teste"]
    )

    acuracia = accuracy_score(
        dados["y_teste"],
        previsoes
    )

    f1 = f1_score(
        dados["y_teste"],
        previsoes,
        average="macro",
        zero_division=0
    )

    categorias = sorted(DOCUMENTOS.keys())

    matriz = confusion_matrix(
        dados["y_teste"],
        previsoes,
        labels=categorias
    )

    relatorio = classification_report(
        dados["y_teste"],
        previsoes,
        labels=categorias,
        output_dict=True,
        zero_division=0
    )

    resultado = {
        "modelo": nome,
        "acuracia": float(acuracia),
        "f1_macro": float(f1),
        "matriz_confusao": matriz.tolist(),
        "categorias": categorias,
        "relatorio_classificacao": relatorio
    }

    return pipeline, resultado


# ============================================
# SALVAR JSON
# ============================================

def salvar_json(nome, dados):
    destino = PASTA_SAIDA / nome

    with open(
        destino,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

    return destino


# ============================================
# PIPELINE PRINCIPAL
# ============================================

def executar_pipeline():
    print("=" * 60)
    print("BRITO SOLUÇÕES TECNOLOGICAS")
    print("PIPELINE AUTOMATIZADO DE IA")
    print("=" * 60)

    dados = preparar_dados()

    print("\nDocumentos:", dados["total"])
    print("Treinamento:", len(dados["x_treino"]))
    print("Teste:", len(dados["x_teste"]))
    print("SHA-256:", dados["hash_dataset"])

    resultados = []
    pipelines = {}

    for nome, estimador in criar_modelos().items():
        print(f"\nTreinando: {nome}")

        pipeline, resultado = avaliar_modelo(
            nome,
            estimador,
            dados
        )

        resultados.append(resultado)
        pipelines[nome] = pipeline

        print(
            f"Acurácia: {resultado['acuracia']:.4f}"
        )
        print(
            f"F1 macro: {resultado['f1_macro']:.4f}"
        )

    resultados.sort(
        key=lambda item: (
            item["f1_macro"],
            item["acuracia"]
        ),
        reverse=True
    )

    melhor = resultados[0]
    aprovado = melhor["f1_macro"] >= LIMITE_F1

    status = (
        "APROVADO"
        if aprovado
        else "REPROVADO"
    )

    # Salva o modelo com maior F1 macro.
    # Arquivos joblib devem ser carregados
    # apenas quando sua origem for confiável.

    caminho_modelo = (
        PASTA_SAIDA /
        "melhor_modelo.joblib"
    )

    joblib.dump(
        pipelines[melhor["modelo"]],
        caminho_modelo
    )

    # Identificação do arquivo do modelo.
    hash_modelo = hashlib.sha256(
        caminho_modelo.read_bytes()
    ).hexdigest()

    # Relatório completo.
    relatorio = {
        "empresa": "BRITO SOLUÇÕES TECNOLOGICAS",
        "projeto": "Classificador histórico",
        "tipo": "treinamento_automatizado",
        "ambiente": "laboratorio_sintetico",
        "data_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "versao_python": platform.python_version(),
        "versao_sklearn": sklearn.__version__,
        "semente": SEMENTE,
        "hash_dataset_sha256": dados["hash_dataset"],
        "hash_modelo_sha256": hash_modelo,
        "total_documentos": dados["total"],
        "total_treinamento": len(dados["x_treino"]),
        "total_teste": len(dados["x_teste"]),
        "criterio_selecao": "f1_macro",
        "limite_f1": LIMITE_F1,
        "modelo_selecionado": melhor["modelo"],
        "f1_modelo_selecionado": melhor["f1_macro"],
        "acuracia_modelo_selecionado": melhor["acuracia"],
        "controle_qualidade": status,
        "experimentos": resultados,
        "observacoes": [
            "Documentos sintéticos.",
            "Experimento didático.",
            "Amostra pequena.",
            "Não representa validação em produção.",
            "Não foi realizado ajuste de hiperparâmetros.",
            "O controle de qualidade é ilustrativo."
        ]
    }

    caminho_relatorio = salvar_json(
        "relatorio_treinamento.json",
        relatorio
    )

    # Tabela resumida.
    tabela = pd.DataFrame([
        {
            "modelo": item["modelo"],
            "acuracia": item["acuracia"],
            "f1_macro": item["f1_macro"]
        }
        for item in resultados
    ])

    caminho_csv = (
        PASTA_SAIDA /
        "comparacao_modelos.csv"
    )

    tabela.to_csv(
        caminho_csv,
        index=False,
        encoding="utf-8"
    )

    # Resumo para GitHub Actions.
    resumo = [
        "# Treinamento automatizado de IA",
        "",
        "BRITO SOLUÇÕES TECNOLOGICAS",
        "",
        f"**Modelo selecionado:** {melhor['modelo']}",
        f"**F1 macro:** {melhor['f1_macro']:.4f}",
        f"**Acurácia:** {melhor['acuracia']:.4f}",
        f"**Limite de F1:** {LIMITE_F1:.2f}",
        f"**Controle de qualidade:** {status}",
        "",
        "## Comparação dos modelos",
        "",
        "| Modelo | Acurácia | F1 macro |",
        "|---|---:|---:|"
    ]

    for item in resultados:
        resumo.append(
            f"| {item['modelo']} | "
            f"{item['acuracia']:.4f} | "
            f"{item['f1_macro']:.4f} |"
        )

    resumo.extend([
        "",
        "Resultados de laboratório com dados sintéticos.",
        "A aprovação não autoriza implantação em produção."
    ])

    texto_resumo = "\n".join(resumo)

    caminho_resumo = (
        PASTA_SAIDA /
        "resumo_treinamento.md"
    )

    caminho_resumo.write_text(
        texto_resumo,
        encoding="utf-8"
    )

    arquivo_github = os.getenv(
        "GITHUB_STEP_SUMMARY"
    )

    if arquivo_github:
        with open(
            arquivo_github,
            "a",
            encoding="utf-8"
        ) as arquivo:
            arquivo.write(
                texto_resumo + "\n"
            )

    print("\n" + "=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)

    print("Modelo:", melhor["modelo"])
    print("F1 macro:", f"{melhor['f1_macro']:.4f}")
    print("Acurácia:", f"{melhor['acuracia']:.4f}")
    print("Controle de qualidade:", status)
    print("Relatório:", caminho_relatorio)
    print("Modelo:", caminho_modelo)
    print("CSV:", caminho_csv)
    print("=" * 60)

    if not aprovado:
        print(
            "\nATENÇÃO: o modelo não atingiu "
            "o limite mínimo de qualidade."
        )

        if CONTROLE_RIGOROSO:
            print(
                "Controle rigoroso ativado: "
                "a execução será reprovada."
            )
            return 1

    return 0


if __name__ == "__main__":
    try:
        codigo_saida = executar_pipeline()
        sys.exit(codigo_saida)

    except Exception as erro:
        print(
            "\nERRO NO PIPELINE:",
            str(erro)
        )
        raise
