
"""
Aula 30 - Experimentos e versionamento de IA
BRITO SOLUÇÕES TECNOLOGICAS

Dashboard Streamlit para rastreabilidade
de experimentos de machine learning.

Fonte: relatório JSON gerado na Aula 29.
"""

import html

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


# ============================================
# CONFIGURAÇÕES
# ============================================

URL_RELATORIO = (
    "https://raw.githubusercontent.com/"
    "ricardodevprof10/"
    "ia-classificador-historico/"
    "main/relatorios/"
    "relatorio_experimentos_mlflow.json"
)

PRETO = "#09090b"
CARTAO = "#18181b"
VERMELHO = "#dc2626"
BRANCO = "#ffffff"
CINZA = "#a1a1aa"

st.set_page_config(
    page_title="Experimentos de IA | BRITO",
    page_icon="📈",
    layout="wide"
)


# ============================================
# ESTILOS
# ============================================

st.markdown(
    """
    <style>
    .stApp {
        background: #09090b !important;
        color: #ffffff !important;
    }

    [data-testid="stHeader"] {
        background: #09090b !important;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, p, label {
        color: #ffffff;
    }

    .marca {
        color: #ef4444;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 14px;
    }

    .subtitulo {
        color: #b4b4bd;
        font-size: 15px;
        margin-bottom: 28px;
    }

    .linha {
        height: 3px;
        background: linear-gradient(
            90deg,
            #dc2626,
            #7f1d1d,
            transparent
        );
        margin: 20px 0 28px;
    }

    .cartao {
        background: #18181b;
        border: 1px solid #3f3f46;
        border-top: 3px solid #dc2626;
        border-radius: 12px;
        padding: 20px;
        min-height: 135px;
        margin-bottom: 12px;
    }

    .cartao-label {
        color: #d4d4d8;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .cartao-valor {
        color: #ffffff;
        font-size: 28px;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    .cartao-detalhe {
        color: #a1a1aa;
        font-size: 12px;
        margin-top: 10px;
    }

    .informacao {
        background: #18181b;
        border: 1px solid #3f3f46;
        border-left: 4px solid #dc2626;
        border-radius: 10px;
        padding: 18px;
        margin: 14px 0;
        color: #ffffff;
    }

    div.stButton > button {
        background: #dc2626 !important;
        color: #ffffff !important;
        border: 1px solid #ef4444 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }

    div.stButton > button p {
        color: #ffffff !important;
    }

    [data-testid="stCaptionContainer"] p {
        color: #b4b4bd !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================
# FUNÇÕES
# ============================================

def escapar(valor):
    return html.escape(str(valor))


@st.cache_data(ttl=60)
def carregar_relatorio():
    resposta = requests.get(
        URL_RELATORIO,
        timeout=15
    )

    resposta.raise_for_status()

    dados = resposta.json()

    if not isinstance(dados, dict):
        raise ValueError(
            "O relatório não contém um objeto JSON."
        )

    return dados


def cartao(titulo, valor, detalhe):
    st.markdown(
        f"""
        <div class="cartao">
            <div class="cartao-label">
                {escapar(titulo)}
            </div>
            <div class="cartao-valor">
                {escapar(valor)}
            </div>
            <div class="cartao-detalhe">
                {escapar(detalhe)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def estilizar_grafico(figura, altura=430):
    figura.update_layout(
        paper_bgcolor=PRETO,
        plot_bgcolor=CARTAO,
        font=dict(
            color=BRANCO,
            family="Arial"
        ),
        height=altura,
        margin=dict(
            l=35,
            r=25,
            t=50,
            b=55
        ),
        xaxis=dict(
            color=BRANCO,
            gridcolor="#3f3f46"
        ),
        yaxis=dict(
            color=BRANCO,
            gridcolor="#3f3f46"
        ),
        legend=dict(
            font=dict(color=BRANCO)
        )
    )

    return figura


# ============================================
# CABEÇALHO
# ============================================

st.markdown(
    '<div class="marca">'
    'BRITO SOLUÇÕES TECNOLOGICAS'
    '</div>',
    unsafe_allow_html=True
)

st.title("Experimentos e versionamento de IA")

st.markdown(
    '<div class="subtitulo">'
    'MLflow | Comparação de modelos | '
    'Rastreabilidade | Reprodutibilidade científica'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="linha"></div>',
    unsafe_allow_html=True
)

if st.button("↻ Atualizar experimentos"):
    st.cache_data.clear()
    st.rerun()


# ============================================
# CARREGAMENTO DO RELATÓRIO
# ============================================

try:
    relatorio = carregar_relatorio()

except (
    requests.RequestException,
    ValueError
) as erro:

    st.error(
        "Não foi possível carregar o relatório "
        "de experimentos."
    )

    st.info(
        "Execute a Aula 29 e publique "
        "relatorios/relatorio_experimentos_mlflow.json "
        "na branch main do GitHub."
    )

    st.code(str(erro))
    st.stop()


experimentos = relatorio.get(
    "experimentos",
    []
)

if not isinstance(experimentos, list):
    st.error(
        "O campo experimentos possui formato inválido."
    )
    st.stop()

if not experimentos:
    st.warning(
        "O relatório não contém experimentos."
    )
    st.stop()


# ============================================
# PREPARAÇÃO DOS DADOS
# ============================================

df = pd.DataFrame(experimentos)

colunas_obrigatorias = [
    "modelo",
    "acuracia",
    "f1_macro",
    "run_id"
]

faltantes = [
    coluna
    for coluna in colunas_obrigatorias
    if coluna not in df.columns
]

if faltantes:
    st.error(
        "Campos ausentes no relatório: "
        + ", ".join(faltantes)
    )
    st.stop()

df["acuracia"] = pd.to_numeric(
    df["acuracia"],
    errors="coerce"
)

df["f1_macro"] = pd.to_numeric(
    df["f1_macro"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "acuracia",
        "f1_macro"
    ]
)

if df.empty:
    st.error(
        "Nenhuma métrica numérica válida foi encontrada."
    )
    st.stop()

df = df.sort_values(
    "f1_macro",
    ascending=False
).reset_index(drop=True)

melhor = df.iloc[0]

total_modelos = len(df)

melhor_f1 = float(
    melhor["f1_macro"]
)

melhor_acuracia = float(
    melhor["acuracia"]
)

total_documentos = int(
    relatorio.get(
        "total_documentos",
        0
    )
)


# ============================================
# VISÃO GERAL
# ============================================

st.subheader("Visão geral dos experimentos")

col1, col2, col3, col4 = st.columns(4)

with col1:
    cartao(
        "Modelos avaliados",
        total_modelos,
        "Execuções registradas no relatório"
    )

with col2:
    cartao(
        "Maior F1 macro",
        f"{melhor_f1:.4f}",
        "Maior pontuação registrada"
    )

with col3:
    cartao(
        "Acurácia correspondente",
        f"{melhor_acuracia * 100:.2f}%",
        "Acurácia do modelo com maior F1"
    )

with col4:
    cartao(
        "Documentos utilizados",
        total_documentos,
        "Conjunto sintético"
    )


# ============================================
# MODELO COM MAIOR F1
# ============================================

st.subheader("Modelo com maior F1 macro")

st.markdown(
    f"""
    <div class="informacao">
        <strong>Modelo:</strong>
        {escapar(melhor["modelo"])}
        <p>
            F1 macro:
            <strong>{melhor_f1:.4f}</strong>
        </p>
        <p>
            Acurácia:
            <strong>
                {melhor_acuracia * 100:.2f}%
            </strong>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "A classificação apresentada corresponde "
    "ao conjunto de teste sintético. "
    "Não representa validação independente "
    "para uso em produção."
)


# ============================================
# COMPARAÇÃO DE MODELOS
# ============================================

st.subheader("Comparação de desempenho")

figura = go.Figure()

figura.add_trace(
    go.Bar(
        x=df["modelo"],
        y=df["acuracia"],
        name="Acurácia",
        marker_color="#a1a1aa",
        text=[
            f"{valor:.3f}"
            for valor in df["acuracia"]
        ],
        textposition="outside"
    )
)

figura.add_trace(
    go.Bar(
        x=df["modelo"],
        y=df["f1_macro"],
        name="F1 macro",
        marker_color=VERMELHO,
        text=[
            f"{valor:.3f}"
            for valor in df["f1_macro"]
        ],
        textposition="outside"
    )
)

figura.update_layout(
    title="Acurácia e F1 macro por modelo",
    barmode="group",
    yaxis_title="Pontuação",
    yaxis_range=[0, 1.1]
)

st.plotly_chart(
    estilizar_grafico(figura),
    use_container_width=True
)


# ============================================
# TABELA COMPARATIVA
# ============================================

st.subheader("Tabela de experimentos")

df_tabela = df[
    [
        "modelo",
        "acuracia",
        "f1_macro",
        "run_id"
    ]
].copy()

df_tabela.columns = [
    "Modelo",
    "Acurácia",
    "F1 macro",
    "ID da execução"
]

st.dataframe(
    df_tabela.style.format({
        "Acurácia": "{:.4f}",
        "F1 macro": "{:.4f}"
    }),
    use_container_width=True,
    hide_index=True
)


# ============================================
# CONSULTA INDIVIDUAL
# ============================================

st.subheader("Consultar execução")

modelos_disponiveis = (
    df["modelo"].astype(str).tolist()
)

modelo_selecionado = st.selectbox(
    "Selecione um modelo:",
    modelos_disponiveis
)

registro = df[
    df["modelo"].astype(str)
    == modelo_selecionado
].iloc[0]

col1, col2 = st.columns(2)

with col1:
    st.write(
        "**Modelo:**",
        registro["modelo"]
    )

    st.write(
        "**Acurácia:**",
        f"{registro['acuracia']:.4f}"
    )

with col2:
    st.write(
        "**F1 macro:**",
        f"{registro['f1_macro']:.4f}"
    )

    st.write(
        "**ID da execução:**",
        registro["run_id"]
    )


# ============================================
# RASTREABILIDADE
# ============================================

st.subheader("Rastreabilidade científica")

col1, col2 = st.columns(2)

with col1:
    st.write(
        "**Projeto:**",
        relatorio.get(
            "projeto",
            "Não informado"
        )
    )

    st.write(
        "**Ambiente:**",
        relatorio.get(
            "ambiente",
            "Não informado"
        )
    )

    st.write(
        "**Versão MLflow:**",
        relatorio.get(
            "versao_mlflow",
            "Não informada"
        )
    )

    st.write(
        "**Versão scikit-learn:**",
        relatorio.get(
            "versao_sklearn",
            "Não informada"
        )
    )

with col2:
    st.write(
        "**Treinamento:**",
        relatorio.get(
            "total_treinamento",
            "Não informado"
        )
    )

    st.write(
        "**Teste:**",
        relatorio.get(
            "total_teste",
            "Não informado"
        )
    )

    st.write(
        "**Critério de comparação:**",
        relatorio.get(
            "criterio_comparacao",
            "Não informado"
        )
    )

    st.write(
        "**Data UTC:**",
        relatorio.get(
            "data_utc",
            "Não informada"
        )
    )


# ============================================
# IDENTIFICAÇÃO DO DATASET
# ============================================

st.subheader("Identificação do conjunto de dados")

hash_dataset = relatorio.get(
    "hash_dataset_sha256",
    "Não informado"
)

st.code(
    str(hash_dataset),
    language="text"
)

st.caption(
    "O hash SHA-256 permite verificar "
    "a identidade do conteúdo do dataset. "
    "Ele não substitui a preservação "
    "dos documentos originais."
)


# ============================================
# OBSERVAÇÕES
# ============================================

st.subheader("Limitações metodológicas")

observacoes = relatorio.get(
    "observacoes",
    []
)

if isinstance(observacoes, list):
    for observacao in observacoes:
        st.markdown(
            "- " + escapar(observacao)
        )

st.warning(
    "Os resultados são provenientes de "
    "um laboratório sintético. "
    "A comparação exploratória não constitui "
    "validação científica independente. "
    "Para aplicações reais, são necessários "
    "corpora representativos, validação "
    "adequada e avaliação historiográfica."
)

st.divider()

st.caption(
    "BRITO SOLUÇÕES TECNOLOGICAS | "
    "Pesquisa e tecnologia a serviço da humanidade."
)
