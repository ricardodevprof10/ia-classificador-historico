
"""
Aula 24 - Página de detecção de anomalias
BRITO SOLUÇÕES TECNOLOGICAS

Página adicional do dashboard Streamlit.
"""

import html

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


URL_RELATORIO = (
    "https://raw.githubusercontent.com/"
    "ricardodevprof10/"
    "ia-classificador-historico/"
    "main/relatorios/"
    "relatorio_anomalias.json"
)

PRETO = "#09090b"
CARTAO = "#18181b"
VERMELHO = "#dc2626"
BRANCO = "#ffffff"


st.set_page_config(
    page_title="Detecção de anomalias | BRITO",
    page_icon="🔴",
    layout="wide"
)


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
        margin-bottom: 30px;
    }

    .cartao {
        background: #18181b;
        border: 1px solid #3f3f46;
        border-top: 3px solid #dc2626;
        border-radius: 12px;
        padding: 20px;
        min-height: 135px;
    }

    .cartao-label {
        color: #d4d4d8;
        font-size: 13px;
        margin-bottom: 12px;
    }

    .cartao-valor {
        color: #ffffff;
        font-size: 29px;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    .alerta {
        background: #291315;
        border: 1px solid #991b1b;
        border-left: 5px solid #ef4444;
        border-radius: 10px;
        padding: 20px;
        margin-top: 22px;
        margin-bottom: 22px;
        color: #ffffff;
    }

    .normal {
        background: #142019;
        border: 1px solid #365c42;
        border-left: 5px solid #22c55e;
        border-radius: 10px;
        padding: 20px;
        margin-top: 22px;
        margin-bottom: 22px;
        color: #ffffff;
    }

    div.stButton > button {
        background: #dc2626 !important;
        color: #ffffff !important;
        border-color: #ef4444 !important;
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


def escapar(valor):
    return html.escape(str(valor))


@st.cache_data(ttl=60)
def carregar_relatorio():
    resposta = requests.get(
        URL_RELATORIO,
        timeout=15
    )

    resposta.raise_for_status()

    return resposta.json()


def exibir_cartao(titulo, valor):
    st.markdown(
        f"""
        <div class="cartao">
            <div class="cartao-label">
                {escapar(titulo)}
            </div>
            <div class="cartao-valor">
                {escapar(valor)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown(
    '<div class="marca">'
    'BRITO SOLUÇÕES TECNOLOGICAS'
    '</div>',
    unsafe_allow_html=True
)

st.title("Detecção de anomalias")

st.markdown(
    '<div class="subtitulo">'
    'Machine Learning | Isolation Forest '
    '| Observabilidade de IA'
    '</div>',
    unsafe_allow_html=True
)

if st.button("↻ Atualizar relatório"):
    st.cache_data.clear()
    st.rerun()


try:
    relatorio = carregar_relatorio()
except (requests.RequestException, ValueError) as erro:
    st.error(
        "Não foi possível carregar o relatório "
        "de anomalias."
    )

    st.info(
        "Execute primeiro o workflow "
        "'Deteccao automatizada de anomalias' "
        "no GitHub Actions."
    )

    st.code(str(erro))
    st.stop()


total = int(
    relatorio.get("total_solicitacoes", 0)
)

quantidade = int(
    relatorio.get("anomalias_detectadas", 0)
)

percentual = float(
    relatorio.get("percentual_anomalias", 0)
)

latencia_p95 = float(
    relatorio.get("latencia_p95_ms", 0)
)

alerta = bool(
    relatorio.get("alerta", False)
)


st.subheader("Visão geral")

col1, col2, col3, col4 = st.columns(4)

with col1:
    exibir_cartao(
        "Solicitações analisadas",
        total
    )

with col2:
    exibir_cartao(
        "Anomalias detectadas",
        quantidade
    )

with col3:
    exibir_cartao(
        "Percentual de anomalias",
        f"{percentual:.2f}%"
    )

with col4:
    exibir_cartao(
        "Latência P95",
        f"{latencia_p95:.2f} ms"
    )


if alerta:
    st.markdown(
        """
        <div class="alerta">
            <strong>
                ALERTA DE ANOMALIAS
            </strong>
            <p>
                Foram detectados comportamentos
                incomuns na latência das
                solicitações analisadas.
                É necessário investigar os
                registros identificados.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <div class="normal">
            <strong>
                NENHUMA ANOMALIA DETECTADA
            </strong>
            <p>
                Nenhuma observação foi classificada
                como anômala nesta execução.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


st.subheader("Registros identificados")

registros = relatorio.get(
    "registros_anormais",
    []
)

if registros:
    df = pd.DataFrame(registros)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    figura = go.Figure()

    figura.add_trace(
        go.Bar(
            x=df["solicitacao"].astype(str),
            y=df["latencia_ms"],
            marker_color=VERMELHO,
            name="Latência anômala",
            hovertemplate=(
                "Solicitação %{x}<br>"
                "Latência: %{y:.2f} ms"
                "<extra></extra>"
            )
        )
    )

    figura.update_layout(
        title="Latências classificadas como anômalas",
        paper_bgcolor=PRETO,
        plot_bgcolor=CARTAO,
        font=dict(color=BRANCO),
        xaxis_title="Solicitação",
        yaxis_title="Latência (ms)",
        yaxis=dict(
            gridcolor="#3f3f46"
        ),
        height=400,
        margin=dict(
            l=30,
            r=20,
            t=60,
            b=40
        )
    )

    st.plotly_chart(
        figura,
        use_container_width=True
    )

    st.caption(
        "O gráfico apresenta apenas os "
        "registros classificados como anômalos."
    )
else:
    st.info(
        "Não existem registros anômalos "
        "para apresentar."
    )


st.subheader("Informações da análise")

st.write(
    "**Detector:**",
    relatorio.get("detector", "Não informado")
)

st.write(
    "**Versão:**",
    relatorio.get(
        "versao_detector",
        "Não informada"
    )
)

st.write(
    "**Data UTC:**",
    relatorio.get(
        "data_utc",
        "Não informada"
    )
)

st.write(
    "**Ambiente:**",
    relatorio.get(
        "ambiente",
        "Não informado"
    )
)

st.warning(
    "Os dados desta aula são sintéticos. "
    "A detecção de anomalias não comprova "
    "falha operacional nem degradação "
    "da qualidade do classificador."
)

st.divider()

st.caption(
    "BRITO SOLUÇÕES TECNOLOGICAS | "
    "Pesquisa e tecnologia a serviço da humanidade."
)
