
"""
Dashboard de monitoramento de IA
BRITO SOLUÇÕES TECNOLOGICAS

Tema: preto, vermelho e branco.
Fonte: relatórios JSON publicados no GitHub.
"""

import html

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


USUARIO = "ricardodevprof10"
REPOSITORIO = "ia-classificador-historico"
BRANCH = "main"

URL_BASE = (
    "https://raw.githubusercontent.com/"
    f"{USUARIO}/{REPOSITORIO}/{BRANCH}/relatorios"
)

PRETO = "#09090b"
CARTAO = "#18181b"
VERMELHO = "#dc2626"
VERMELHO_CLARO = "#f87171"
BRANCO = "#ffffff"
CINZA = "#a1a1aa"


st.set_page_config(
    page_title="Monitoramento de IA | BRITO",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================
# ESTILO VISUAL
# =========================================

st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
    }

    html, body, [class*="css"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        color: #ffffff !important;
        font-family: Arial, sans-serif;
    }

    .stApp {
        background: #09090b !important;
        color: #ffffff !important;
    }

    [data-testid="stHeader"] {
        background: #09090b !important;
    }

    [data-testid="stSidebar"] {
        background: #111114 !important;
    }

    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    h1, h2, h3, h4, h5, h6,
    p, label, span {
        color: #ffffff;
    }

    [data-testid="stCaptionContainer"] p {
        color: #b4b4bd !important;
    }

    .marca {
        color: #ef4444 !important;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }

    .titulo-principal {
        color: #ffffff !important;
        font-size: clamp(28px, 3vw, 43px);
        font-weight: 800;
        margin-bottom: 8px;
    }

    .subtitulo {
        color: #b4b4bd !important;
        font-size: 15px;
        margin-bottom: 25px;
    }

    .linha-vermelha {
        height: 3px;
        background: linear-gradient(
            90deg,
            #dc2626,
            #7f1d1d,
            transparent
        );
        margin: 22px 0 28px;
    }

    .metric-card {
        background: #18181b;
        border: 1px solid #34343a;
        border-top: 3px solid #dc2626;
        border-radius: 12px;
        padding: 23px 20px;
        min-height: 145px;
        margin-bottom: 14px;
    }

    .metric-label {
        color: #c4c4cc !important;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 13px;
    }

    .metric-value {
        color: #ffffff !important;
        font-size: clamp(26px, 3vw, 37px);
        font-weight: 800;
        line-height: 1.2;
    }

    .metric-detail {
        color: #a1a1aa !important;
        font-size: 12px;
        margin-top: 12px;
    }

    .alerta {
        background: #271214;
        border: 1px solid #991b1b;
        border-left: 5px solid #ef4444;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0 26px;
    }

    .alerta-titulo {
        color: #ffffff !important;
        font-size: 17px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .alerta-texto {
        color: #e4e4e7 !important;
        font-size: 14px;
        line-height: 1.6;
    }

    .normal {
        background: #142019;
        border: 1px solid #365c42;
        border-left: 5px solid #22c55e;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0 26px;
    }

    .secao-titulo {
        color: #ffffff !important;
        font-size: 22px;
        font-weight: 800;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .secao-descricao {
        color: #a1a1aa !important;
        font-size: 14px;
        margin-bottom: 18px;
    }

    div.stButton > button {
        background: #dc2626 !important;
        color: #ffffff !important;
        border: 1px solid #ef4444 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 9px 20px !important;
    }

    div.stButton > button:hover {
        background: #b91c1c !important;
        color: #ffffff !important;
        border-color: #f87171 !important;
    }

    div.stButton > button p {
        color: #ffffff !important;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #38383f;
        border-radius: 8px;
    }

    hr {
        border-color: #38383f !important;
    }

    .rodape {
        color: #a1a1aa !important;
        font-size: 12px;
        text-align: center;
        padding: 25px 0;
    }

    @media (max-width: 700px) {
        .metric-card {
            min-height: 125px;
            padding: 17px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================
# FUNÇÕES AUXILIARES
# =========================================

@st.cache_data(ttl=60)
def carregar_json(nome_arquivo):
    url = f"{URL_BASE}/{nome_arquivo}"

    resposta = requests.get(
        url,
        timeout=15
    )

    resposta.raise_for_status()
    return resposta.json()


def cartao(titulo, valor, detalhe):
    titulo = html.escape(str(titulo))
    valor = html.escape(str(valor))
    detalhe = html.escape(str(detalhe))

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{titulo}</div>
            <div class="metric-value">{valor}</div>
            <div class="metric-detail">{detalhe}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def estilizar_grafico(figura, altura=410):
    figura.update_layout(
        paper_bgcolor=PRETO,
        plot_bgcolor=CARTAO,
        font=dict(
            family="Arial",
            color=BRANCO,
            size=13
        ),
        height=altura,
        margin=dict(
            l=30,
            r=25,
            t=35,
            b=35
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(color=BRANCO)
        ),
        xaxis=dict(
            color=BRANCO,
            showgrid=False,
            linecolor="#52525b",
            tickfont=dict(color=BRANCO)
        ),
        yaxis=dict(
            color=BRANCO,
            gridcolor="#34343a",
            zerolinecolor="#52525b",
            tickfont=dict(color=BRANCO)
        ),
        hoverlabel=dict(
            bgcolor="#27272a",
            font_color=BRANCO
        )
    )

    return figura


# =========================================
# CABEÇALHO
# =========================================

st.markdown(
    '<div class="marca">'
    'BRITO SOLUÇÕES TECNOLOGICAS'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="titulo-principal">'
    'Dashboard de monitoramento de IA'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">'
    'Monitoramento de modelos | '
    'Análise de distribuições | MLOps'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="linha-vermelha"></div>',
    unsafe_allow_html=True
)

if st.button("↻ Atualizar dados"):
    st.cache_data.clear()
    st.rerun()


# =========================================
# CARREGAMENTO
# =========================================

try:
    relatorio = carregar_json(
        "relatorio_monitoramento.json"
    )

except (requests.RequestException, ValueError) as erro:
    st.error(
        "Não foi possível carregar o relatório JSON. "
        "Verifique o workflow no GitHub Actions."
    )
    st.code(str(erro))
    st.stop()


psi = float(relatorio["psi"])
limite = float(relatorio["limite_alerta"])
alerta = bool(relatorio["alerta"])

quantidade_referencia = int(
    relatorio["quantidade_referencia"]
)

quantidade_atual = int(
    relatorio["quantidade_atual"]
)

total_documentos = (
    quantidade_referencia + quantidade_atual
)

versao = relatorio["versao"]


# =========================================
# INDICADORES
# =========================================

st.markdown(
    '<div class="secao-titulo">'
    'Visão geral'
    '</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    cartao(
        "PSI atual",
        f"{psi:.4f}",
        "Índice de estabilidade"
    )

with col2:
    cartao(
        "Limite de alerta",
        f"{limite:.2f}",
        "Limite configurado"
    )

with col3:
    cartao(
        "Documentos analisados",
        total_documentos,
        "Referência + atual"
    )

with col4:
    cartao(
        "Versão do modelo",
        versao,
        "Classificador histórico"
    )


# =========================================
# STATUS
# =========================================

if alerta:
    st.markdown(
        """
        <div class="alerta">
            <div class="alerta-titulo">
                ⚠ ALERTA DE MONITORAMENTO
            </div>
            <div class="alerta-texto">
                Foi identificada uma mudança expressiva
                na distribuição das categorias previstas.
                O PSI ultrapassou o limite configurado.
                Isso não comprova perda de acurácia.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <div class="normal">
            <div class="alerta-titulo">
                MONITORAMENTO NORMAL
            </div>
            <div class="alerta-texto">
                O PSI está dentro do limite
                configurado para o experimento.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================
# DISTRIBUIÇÕES
# =========================================

st.markdown(
    '<div class="secao-titulo">'
    'Distribuição das categorias'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="secao-descricao">'
    'Comparação entre as previsões de referência '
    'e as previsões atuais.'
    '</div>',
    unsafe_allow_html=True
)

linhas = []

for categoria, valores in relatorio[
    "distribuicoes"
].items():
    linhas.append({
        "Categoria": categoria,
        "Referência (%)": float(
            valores["referencia_pct"]
        ),
        "Atual (%)": float(
            valores["atual_pct"]
        )
    })

df = pd.DataFrame(linhas)

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=df["Categoria"],
        y=df["Referência (%)"],
        name="Referência",
        marker_color=BRANCO,
        text=df["Referência (%)"],
        textposition="outside",
        textfont=dict(color=BRANCO),
        hovertemplate="%{x}: %{y:.2f}%<extra></extra>"
    )
)

fig.add_trace(
    go.Bar(
        x=df["Categoria"],
        y=df["Atual (%)"],
        name="Atual",
        marker_color=VERMELHO,
        text=df["Atual (%)"],
        textposition="outside",
        textfont=dict(color=BRANCO),
        hovertemplate="%{x}: %{y:.2f}%<extra></extra>"
    )
)

fig.update_layout(
    barmode="group",
    yaxis_title="Percentual (%)",
    bargap=0.28
)

fig.update_yaxes(
    range=[
        0,
        max(
            10,
            float(
                df[
                    ["Referência (%)", "Atual (%)"]
                ].max().max()
            ) * 1.20
        )
    ]
)

fig = estilizar_grafico(fig)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =========================================
# TABELA
# =========================================

st.markdown(
    '<div class="secao-titulo">'
    'Detalhamento por categoria'
    '</div>',
    unsafe_allow_html=True
)

st.dataframe(
    df.style.format({
        "Referência (%)": "{:.2f}%",
        "Atual (%)": "{:.2f}%"
    }),
    use_container_width=True,
    hide_index=True
)


# =========================================
# HISTÓRICO
# =========================================

st.markdown(
    '<div class="secao-titulo">'
    'Histórico de monitoramento'
    '</div>',
    unsafe_allow_html=True
)

try:
    historico = carregar_json(
        "historico_monitoramento.json"
    )

    df_historico = pd.DataFrame(historico)

    if not df_historico.empty:
        df_historico["data_utc"] = pd.to_datetime(
            df_historico["data_utc"],
            utc=True
        )

        df_historico = df_historico.sort_values(
            "data_utc"
        )

        df_historico["Execução"] = range(
            1,
            len(df_historico) + 1
        )

        fig_historico = go.Figure()

        fig_historico.add_trace(
            go.Scatter(
                x=df_historico["Execução"],
                y=df_historico["psi"],
                mode="lines+markers",
                name="PSI",
                line=dict(
                    color=VERMELHO,
                    width=3
                ),
                marker=dict(
                    size=9,
                    color=BRANCO,
                    line=dict(
                        color=VERMELHO,
                        width=2
                    )
                )
            )
        )

        fig_historico.add_hline(
            y=limite,
            line_color=VERMELHO_CLARO,
            line_dash="dash",
            annotation_text="Limite de alerta",
            annotation_font_color=BRANCO
        )

        fig_historico.update_layout(
            xaxis_title="Execução",
            yaxis_title="PSI"
        )

        fig_historico = estilizar_grafico(
            fig_historico,
            altura=350
        )

        st.plotly_chart(
            fig_historico,
            use_container_width=True
        )

        st.dataframe(
            df_historico,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "Ainda não há registros no histórico."
        )

except (
    requests.RequestException,
    ValueError,
    KeyError
):
    st.info(
        "O histórico ainda não está disponível."
    )


# =========================================
# RODAPÉ
# =========================================

st.markdown(
    '<div class="linha-vermelha"></div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="rodape">
        BRITO SOLUÇÕES TECNOLOGICAS<br>
        Pesquisa e tecnologia a serviço da humanidade.<br>
        Dashboard educacional de monitoramento de IA.
    </div>
    """,
    unsafe_allow_html=True
)
