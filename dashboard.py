
"""
Aula 22 - Central de monitoramento de IA
BRITO SOLUÇÕES TECNOLOGICAS

Integra:
- Monitoramento estatístico (PSI)
- Observabilidade operacional
- Histórico de monitoramento
- Central de alertas

Executar com:
streamlit run dashboard.py
"""

import html
from datetime import datetime

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


# ==========================================
# CONFIGURAÇÃO
# ==========================================

st.set_page_config(
    page_title="Central de Monitoramento | BRITO",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================
# ESTILO VISUAL
# ==========================================

st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
    }

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
        color: #ef4444 !important;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 12px;
    }

    .titulo {
        color: #ffffff !important;
        font-size: clamp(27px, 3vw, 42px);
        font-weight: 800;
        margin-bottom: 8px;
    }

    .subtitulo {
        color: #b4b4bd !important;
        font-size: 15px;
        margin-bottom: 25px;
    }

    .linha {
        height: 3px;
        background: linear-gradient(
            90deg,
            #dc2626,
            #7f1d1d,
            transparent
        );
        margin: 24px 0 30px;
    }

    .secao {
        color: #ffffff !important;
        font-size: 22px;
        font-weight: 800;
        margin: 25px 0 15px;
    }

    .descricao {
        color: #b4b4bd !important;
        font-size: 14px;
        margin-bottom: 20px;
    }

    .cartao {
        background: #18181b;
        border: 1px solid #3f3f46;
        border-top: 3px solid #dc2626;
        border-radius: 12px;
        padding: 22px 18px;
        min-height: 140px;
        margin-bottom: 14px;
    }

    .cartao-label {
        color: #d4d4d8 !important;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .cartao-valor {
        color: #ffffff !important;
        font-size: clamp(25px, 2.8vw, 35px);
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    .cartao-detalhe {
        color: #a1a1aa !important;
        font-size: 12px;
        margin-top: 10px;
    }

    .alerta {
        background: #271214;
        border: 1px solid #991b1b;
        border-left: 5px solid #ef4444;
        border-radius: 10px;
        padding: 20px;
        margin: 12px 0;
    }

    .alerta-titulo {
        color: #ffffff !important;
        font-size: 16px;
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
        margin: 12px 0;
    }

    div.stButton > button {
        background: #dc2626 !important;
        color: #ffffff !important;
        border: 1px solid #ef4444 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }

    div.stButton > button:hover {
        background: #b91c1c !important;
        color: #ffffff !important;
    }

    div.stButton > button p {
        color: #ffffff !important;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #3f3f46;
        border-radius: 8px;
    }

    [data-testid="stCaptionContainer"] p {
        color: #b4b4bd !important;
    }

    .rodape {
        text-align: center;
        color: #a1a1aa !important;
        font-size: 12px;
        line-height: 1.9;
        padding: 20px;
    }

    @media (max-width: 700px) {
        .cartao {
            padding: 15px;
            min-height: 120px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# FUNÇÕES DE DADOS
# ==========================================

@st.cache_data(ttl=60)
def carregar_json(nome):
    url = f"{URL_BASE}/{nome}"

    resposta = requests.get(
        url,
        timeout=15
    )

    resposta.raise_for_status()

    return resposta.json()


def carregar_opcional(nome):
    try:
        return carregar_json(nome)
    except (
        requests.RequestException,
        ValueError
    ):
        return None


def seguro(valor):
    return html.escape(str(valor))


def cartao(titulo, valor, detalhe):
    st.markdown(
        f"""
        <div class="cartao">
            <div class="cartao-label">
                {seguro(titulo)}
            </div>
            <div class="cartao-valor">
                {seguro(valor)}
            </div>
            <div class="cartao-detalhe">
                {seguro(detalhe)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def alerta_visual(titulo, mensagem, ativo=True):
    classe = "alerta" if ativo else "normal"

    st.markdown(
        f"""
        <div class="{classe}">
            <div class="alerta-titulo">
                {seguro(titulo)}
            </div>
            <div class="alerta-texto">
                {seguro(mensagem)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def titulo_secao(titulo, descricao=""):
    st.markdown(
        f'<div class="secao">{seguro(titulo)}</div>',
        unsafe_allow_html=True
    )

    if descricao:
        st.markdown(
            f'<div class="descricao">'
            f'{seguro(descricao)}</div>',
            unsafe_allow_html=True
        )


def estilizar_grafico(figura, altura=380):
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
            l=25,
            r=25,
            t=40,
            b=35
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
            font=dict(color=BRANCO)
        ),
        xaxis=dict(
            color=BRANCO,
            showgrid=False,
            linecolor="#52525b"
        ),
        yaxis=dict(
            color=BRANCO,
            gridcolor="#34343a",
            zerolinecolor="#52525b"
        ),
        hoverlabel=dict(
            bgcolor="#27272a",
            font_color=BRANCO
        )
    )

    return figura


def formatar_data(valor):
    if not valor:
        return "Não informada"

    try:
        data = datetime.fromisoformat(
            str(valor).replace("Z", "+00:00")
        )
        return data.strftime("%d/%m/%Y %H:%M UTC")
    except (ValueError, TypeError):
        return str(valor)


# ==========================================
# CABEÇALHO
# ==========================================

st.markdown(
    '<div class="marca">'
    'BRITO SOLUÇÕES TECNOLOGICAS'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="titulo">'
    'Central de monitoramento de IA'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">'
    'Observabilidade | Monitoramento estatístico '
    '| Alertas inteligentes | MLOps'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="linha"></div>',
    unsafe_allow_html=True
)

if st.button("↻ Atualizar indicadores"):
    st.cache_data.clear()
    st.rerun()


# ==========================================
# CARREGAR RELATÓRIOS
# ==========================================

try:
    estatistico = carregar_json(
        "relatorio_monitoramento.json"
    )
except (
    requests.RequestException,
    ValueError
) as erro:
    st.error(
        "Não foi possível carregar o relatório "
        "estatístico do GitHub."
    )
    st.code(str(erro))
    st.stop()

operacional = carregar_opcional(
    "metricas_observabilidade.json"
)

historico = carregar_opcional(
    "historico_monitoramento.json"
)


# ==========================================
# VISÃO ESTATÍSTICA
# ==========================================

titulo_secao(
    "Monitoramento estatístico",
    "Acompanhamento da distribuição "
    "das categorias previstas."
)

psi = float(estatistico["psi"])
limite = float(estatistico["limite_alerta"])
alerta_psi = bool(estatistico["alerta"])

total_documentos = (
    int(estatistico["quantidade_referencia"])
    + int(estatistico["quantidade_atual"])
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
        "Limite de PSI",
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
        estatistico["versao"],
        "Classificador histórico"
    )


# ==========================================
# VISÃO OPERACIONAL
# ==========================================

titulo_secao(
    "Observabilidade operacional",
    "Métricas de execução, erros "
    "e tempos de resposta."
)

if operacional:
    total = int(
        operacional["total_requisicoes"]
    )

    erros = int(
        operacional["erros"]
    )

    taxa = float(
        operacional["taxa_erros_pct"]
    )

    latencia_media = float(
        operacional["latencia_media_ms"]
    )

    p95 = float(
        operacional["latencia_p95_ms"]
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        cartao(
            "Solicitações",
            total,
            "Total processado"
        )

    with col2:
        cartao(
            "Taxa de erros",
            f"{taxa:.1f}%",
            f"{erros} falhas registradas"
        )

    with col3:
        cartao(
            "Latência média",
            f"{latencia_media:.2f} ms",
            "Tempo médio por solicitação"
        )

    with col4:
        cartao(
            "Latência P95",
            f"{p95:.2f} ms",
            "Percentil 95"
        )

else:
    st.info(
        "O relatório operacional ainda não "
        "está disponível. Execute o workflow "
        "'Observabilidade de IA' no GitHub Actions."
    )


# ==========================================
# CENTRAL DE ALERTAS
# ==========================================

titulo_secao(
    "Central de alertas",
    "Condições que exigem investigação."
)

if alerta_psi:
    alerta_visual(
        "ALERTA ESTATÍSTICO",
        (
            f"PSI de {psi:.4f} acima do limite "
            f"de {limite:.2f}. Foi detectada "
            "uma mudança na distribuição "
            "das previsões. Isso não comprova "
            "degradação da acurácia."
        )
    )
else:
    alerta_visual(
        "MONITORAMENTO ESTATÍSTICO NORMAL",
        "O PSI está dentro do limite configurado.",
        ativo=False
    )

if operacional:
    alertas = operacional.get("alertas", [])

    if alertas:
        for item in alertas:
            severidade = str(
                item.get("severidade", "não informada")
            ).upper()

            alerta_visual(
                f"ALERTA OPERACIONAL — {severidade}",
                item.get(
                    "mensagem",
                    "Condição operacional detectada."
                )
            )
    else:
        alerta_visual(
            "SEM ALERTAS OPERACIONAIS",
            "Nenhum limite operacional foi "
            "ultrapassado nesta execução.",
            ativo=False
        )

    if operacional.get("ambiente") == "laboratorio_sintetico":
        st.caption(
            "As métricas operacionais pertencem "
            "a um laboratório sintético, "
            "não a tráfego real de produção."
        )
else:
    st.info(
        "A avaliação de alertas operacionais "
        "ficará disponível após a publicação "
        "do relatório de observabilidade."
    )


# ==========================================
# GRÁFICO DE DISTRIBUIÇÕES
# ==========================================

titulo_secao(
    "Distribuição das previsões",
    "Comparação entre o período de referência "
    "e a amostra atual."
)

linhas = []

for categoria, valores in estatistico[
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
        hovertemplate=(
            "%{x}: %{y:.2f}%<extra></extra>"
        )
    )
)

fig.add_trace(
    go.Bar(
        x=df["Categoria"],
        y=df["Atual (%)"],
        name="Atual",
        marker_color=VERMELHO,
        hovertemplate=(
            "%{x}: %{y:.2f}%<extra></extra>"
        )
    )
)

fig.update_layout(
    barmode="group",
    bargap=0.28,
    yaxis_title="Percentual (%)"
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

st.plotly_chart(
    estilizar_grafico(fig),
    use_container_width=True
)

st.dataframe(
    df.style.format({
        "Referência (%)": "{:.2f}%",
        "Atual (%)": "{:.2f}%"
    }),
    use_container_width=True,
    hide_index=True
)


# ==========================================
# HISTÓRICO DE PSI
# ==========================================

titulo_secao(
    "Histórico de monitoramento",
    "Evolução do PSI ao longo das execuções."
)

if isinstance(historico, list) and historico:
    df_h = pd.DataFrame(historico)

    if "psi" in df_h.columns:
        df_h["Execução"] = range(
            1,
            len(df_h) + 1
        )

        fig_h = go.Figure()

        fig_h.add_trace(
            go.Scatter(
                x=df_h["Execução"],
                y=df_h["psi"],
                mode="lines+markers",
                name="PSI",
                line=dict(
                    color=VERMELHO,
                    width=3
                ),
                marker=dict(
                    color=BRANCO,
                    size=9,
                    line=dict(
                        color=VERMELHO,
                        width=2
                    )
                )
            )
        )

        fig_h.add_hline(
            y=limite,
            line_color=VERMELHO_CLARO,
            line_dash="dash",
            annotation_text="Limite de alerta",
            annotation_font_color=BRANCO
        )

        fig_h.update_layout(
            xaxis_title="Execução",
            yaxis_title="PSI"
        )

        st.plotly_chart(
            estilizar_grafico(fig_h, 340),
            use_container_width=True
        )

        st.dataframe(
            df_h,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(
            "O histórico não contém a coluna PSI."
        )
else:
    st.info(
        "Histórico ainda não disponível."
    )


# ==========================================
# INFORMAÇÕES DOS RELATÓRIOS
# ==========================================

titulo_secao("Informações dos relatórios")

data_estatistica = (
    estatistico.get("data_monitoramento")
    or estatistico.get("data_utc")
)

st.write(
    "**Último relatório estatístico:**",
    formatar_data(data_estatistica)
)

if operacional:
    st.write(
        "**Último relatório operacional:**",
        formatar_data(
            operacional.get("data_utc")
        )
    )

st.caption(
    "Os relatórios são gerados em execuções "
    "independentes e podem ter datas diferentes. "
    "O painel não representa telemetria contínua "
    "em tempo real."
)


# ==========================================
# RODAPÉ
# ==========================================

st.markdown(
    '<div class="linha"></div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="rodape">
        BRITO SOLUÇÕES TECNOLOGICAS<br>
        Pesquisa e tecnologia a serviço
        da humanidade.<br>
        Central educacional de monitoramento de IA
    </div>
    """,
    unsafe_allow_html=True
)
