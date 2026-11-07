
"""
Auditoria e governança de inteligência artificial
BRITO SOLUÇÕES TECNOLOGICAS

Página de auditoria do classificador histórico.

Integra:
- Qualidade de classificação
- Métricas por categoria
- Desequilíbrio de treinamento
- Matriz de confusão
- Alertas de auditoria
- Rastreabilidade dos resultados

Os resultados são provenientes de um
laboratório sintético, não do modelo
de produção.
"""

import html

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


# ==========================================
# CONFIGURAÇÕES
# ==========================================

URL_RELATORIO = (
    "https://raw.githubusercontent.com/"
    "ricardodevprof10/"
    "ia-classificador-historico/"
    "main/relatorios/"
    "relatorio_auditoria_vieses.json"
)

PRETO = "#09090b"
CARTAO = "#18181b"
VERMELHO = "#dc2626"
BRANCO = "#ffffff"
CINZA = "#a1a1aa"

st.set_page_config(
    page_title="Auditoria de IA | BRITO",
    page_icon="🛡️",
    layout="wide"
)


# ==========================================
# ESTILOS
# ==========================================

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
        font-size: 30px;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    .cartao-detalhe {
        color: #a1a1aa;
        font-size: 12px;
        margin-top: 10px;
    }

    .alerta {
        background: #291315;
        border: 1px solid #991b1b;
        border-left: 5px solid #ef4444;
        border-radius: 10px;
        padding: 20px;
        margin: 12px 0;
    }

    .normal {
        background: #142019;
        border: 1px solid #365c42;
        border-left: 5px solid #22c55e;
        border-radius: 10px;
        padding: 20px;
        margin: 12px 0;
    }

    .alerta-titulo {
        font-weight: 800;
        font-size: 15px;
        margin-bottom: 8px;
        color: #ffffff;
    }

    .alerta-texto {
        color: #e4e4e7;
        font-size: 14px;
        line-height: 1.6;
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


# ==========================================
# FUNÇÕES
# ==========================================

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
            "O relatório não contém um objeto JSON válido."
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


def alerta_visual(titulo, mensagem, ativo=True):
    classe = "alerta" if ativo else "normal"

    st.markdown(
        f"""
        <div class="{classe}">
            <div class="alerta-titulo">
                {escapar(titulo)}
            </div>
            <div class="alerta-texto">
                {escapar(mensagem)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def estilizar_grafico(figura, altura=400):
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
            t=45,
            b=45
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


# ==========================================
# CABEÇALHO
# ==========================================

st.markdown(
    '<div class="marca">'
    'BRITO SOLUÇÕES TECNOLOGICAS'
    '</div>',
    unsafe_allow_html=True
)

st.title("Auditoria e governança de IA")

st.markdown(
    '<div class="subtitulo">'
    'Qualidade de modelos | Análise de vieses '
    '| Transparência | Inteligência artificial confiável'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="linha"></div>',
    unsafe_allow_html=True
)

if st.button("↻ Atualizar auditoria"):
    st.cache_data.clear()
    st.rerun()


# ==========================================
# CARREGAMENTO
# ==========================================

try:
    relatorio = carregar_relatorio()

except (
    requests.RequestException,
    ValueError
) as erro:

    st.error(
        "Não foi possível carregar o relatório "
        "de auditoria do GitHub."
    )

    st.info(
        "Verifique se o workflow "
        "'Auditoria automatizada de vieses' "
        "foi executado e se o arquivo "
        "relatorios/relatorio_auditoria_vieses.json "
        "está disponível na branch main."
    )

    st.code(str(erro))
    st.stop()


# ==========================================
# INDICADORES GERAIS
# ==========================================

st.subheader("Visão geral da auditoria")

acuracia = float(
    relatorio.get("acuracia", 0)
)

f1_macro = float(
    relatorio.get("f1_macro", 0)
)

diferenca_recall = float(
    relatorio.get("diferenca_recall", 0)
)

total_teste = int(
    relatorio.get("total_teste", 0)
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    cartao(
        "Acurácia",
        f"{acuracia * 100:.2f}%",
        "Acertos no conjunto de teste"
    )

with col2:
    cartao(
        "F1 macro",
        f"{f1_macro:.4f}",
        "Média entre as categorias"
    )

with col3:
    cartao(
        "Diferença de recall",
        f"{diferenca_recall:.4f}",
        "Maior recall menos menor recall"
    )

with col4:
    cartao(
        "Documentos de teste",
        total_teste,
        "Amostra sintética de avaliação"
    )


# ==========================================
# ALERTAS
# ==========================================

st.subheader("Central de alertas de auditoria")

alertas = relatorio.get("alertas", [])

if alertas:
    for item in alertas:
        alerta_visual(
            item.get(
                "tipo",
                "Alerta de auditoria"
            ).replace("_", " ").upper(),
            item.get(
                "mensagem",
                "Condição identificada."
            )
        )
else:
    alerta_visual(
        "NENHUM LIMITE ULTRAPASSADO",
        "Nenhum critério de alerta foi "
        "ultrapassado nesta execução.",
        ativo=False
    )

st.caption(
    "Os alertas representam critérios técnicos "
    "de investigação. Não comprovam "
    "discriminação ou falha historiográfica."
)


# ==========================================
# DISTRIBUIÇÃO DO TREINAMENTO
# ==========================================

st.subheader("Distribuição do treinamento")

distribuicao = relatorio.get(
    "distribuicao_treinamento",
    {}
)

if distribuicao:
    linhas = []

    for categoria, dados in distribuicao.items():
        linhas.append({
            "Categoria": categoria,
            "Documentos": int(
                dados.get("quantidade", 0)
            ),
            "Percentual": (
                float(dados.get("proporcao", 0))
                * 100
            )
        })

    df_distribuicao = pd.DataFrame(linhas)

    figura = go.Figure()

    figura.add_trace(
        go.Bar(
            x=df_distribuicao["Categoria"],
            y=df_distribuicao["Documentos"],
            marker_color=VERMELHO,
            text=df_distribuicao["Documentos"],
            textposition="outside",
            name="Documentos"
        )
    )

    figura.update_layout(
        title="Quantidade de documentos por categoria",
        yaxis_title="Documentos",
        showlegend=False
    )

    st.plotly_chart(
        estilizar_grafico(figura),
        use_container_width=True
    )

    st.dataframe(
        df_distribuicao.style.format({
            "Percentual": "{:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )

    razao = relatorio.get(
        "razao_desequilibrio"
    )

    if razao is not None:
        st.metric(
            "Razão de desequilíbrio",
            f"{float(razao):.2f}"
        )

else:
    st.info(
        "Distribuição de treinamento indisponível."
    )


# ==========================================
# MÉTRICAS POR CATEGORIA
# ==========================================

st.subheader("Desempenho por categoria")

metricas = relatorio.get(
    "metricas_por_categoria",
    {}
)

if metricas:
    linhas = []

    for categoria, dados in metricas.items():
        linhas.append({
            "Categoria": categoria,
            "Precisão": float(
                dados.get("precision", 0)
            ),
            "Recall": float(
                dados.get("recall", 0)
            ),
            "F1": float(
                dados.get("f1", 0)
            ),
            "Suporte": int(
                dados.get("suporte", 0)
            )
        })

    df_metricas = pd.DataFrame(linhas)

    st.dataframe(
        df_metricas.style.format({
            "Precisão": "{:.3f}",
            "Recall": "{:.3f}",
            "F1": "{:.3f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    figura_metricas = go.Figure()

    figura_metricas.add_trace(
        go.Bar(
            x=df_metricas["Categoria"],
            y=df_metricas["Precisão"],
            name="Precisão",
            marker_color=BRANCO
        )
    )

    figura_metricas.add_trace(
        go.Bar(
            x=df_metricas["Categoria"],
            y=df_metricas["Recall"],
            name="Recall",
            marker_color=VERMELHO
        )
    )

    figura_metricas.add_trace(
        go.Bar(
            x=df_metricas["Categoria"],
            y=df_metricas["F1"],
            name="F1",
            marker_color="#737373"
        )
    )

    figura_metricas.update_layout(
        barmode="group",
        title="Comparação de métricas",
        yaxis_title="Pontuação",
        yaxis_range=[0, 1.05]
    )

    st.plotly_chart(
        estilizar_grafico(figura_metricas),
        use_container_width=True
    )

else:
    st.info(
        "Métricas por categoria indisponíveis."
    )


# ==========================================
# MATRIZ DE CONFUSÃO
# ==========================================

st.subheader("Matriz de confusão")

matriz = relatorio.get(
    "matriz_confusao",
    []
)

categorias = relatorio.get(
    "categorias",
    []
)

if matriz and categorias:
    figura_matriz = go.Figure(
        data=go.Heatmap(
            z=matriz,
            x=categorias,
            y=categorias,
            colorscale=[
                [0.0, "#18181b"],
                [0.5, "#7f1d1d"],
                [1.0, "#dc2626"]
            ],
            text=matriz,
            texttemplate="%{text}",
            textfont=dict(
                color=BRANCO,
                size=15
            ),
            hovertemplate=(
                "Real: %{y}<br>"
                "Prevista: %{x}<br>"
                "Documentos: %{z}"
                "<extra></extra>"
            )
        )
    )

    figura_matriz.update_layout(
        title="Categorias reais versus previstas",
        xaxis_title="Categoria prevista",
        yaxis_title="Categoria real"
    )

    figura_matriz.update_yaxes(
        autorange="reversed"
    )

    st.plotly_chart(
        estilizar_grafico(figura_matriz, 480),
        use_container_width=True
    )

    st.caption(
        "Os valores na diagonal representam "
        "classificações corretas. Valores fora "
        "da diagonal representam confusões "
        "entre categorias."
    )

else:
    st.info(
        "Matriz de confusão indisponível."
    )


# ==========================================
# ERROS DE CLASSIFICAÇÃO
# ==========================================

st.subheader("Erros identificados")

erros = relatorio.get(
    "erros_classificacao",
    []
)

if erros:
    df_erros = pd.DataFrame(erros)

    st.dataframe(
        df_erros,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        f"Total de erros registrados: {len(erros)}"
    )

else:
    st.info(
        "Nenhum erro foi registrado "
        "no conjunto de teste."
    )


# ==========================================
# RASTREABILIDADE
# ==========================================

st.subheader("Rastreabilidade da auditoria")

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
        "**Tipo de auditoria:**",
        relatorio.get(
            "tipo",
            "Não informado"
        )
    )

with col2:
    st.write(
        "**Versão:**",
        relatorio.get(
            "versao_auditoria",
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
        "**Alertas registrados:**",
        relatorio.get(
            "quantidade_alertas",
            0
        )
    )


# ==========================================
# LIMITAÇÕES
# ==========================================

st.warning(
    "Esta auditoria utiliza dados sintéticos "
    "e um modelo demonstrativo. Os resultados "
    "não comprovam vieses sociais, discriminação "
    "ou degradação do classificador histórico "
    "utilizado em produção."
)

st.divider()

st.caption(
    "BRITO SOLUÇÕES TECNOLOGICAS | "
    "Pesquisa e tecnologia a serviço da humanidade."
)
