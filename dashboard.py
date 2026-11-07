
"""
Aula 20 - Dashboard de monitoramento de IA.

Lê relatórios públicos do GitHub e apresenta
indicadores, gráficos e histórico de PSI.
"""

import pandas as pd
import requests
import streamlit as st

USUARIO = "ricardodevprof10"
REPOSITORIO = "ia-classificador-historico"
BRANCH = "main"

URL_BASE = (
    f"https://raw.githubusercontent.com/"
    f"{USUARIO}/{REPOSITORIO}/{BRANCH}/relatorios"
)

st.set_page_config(
    page_title="Monitoramento de IA",
    page_icon="📊",
    layout="wide"
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #111827;
        color: #f9fafb;
    }

    [data-testid="stMetric"] {
        background-color: #1f2937;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #374151;
    }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data(ttl=60)
def carregar_json(nome_arquivo):
    url = f"{URL_BASE}/{nome_arquivo}"

    resposta = requests.get(
        url,
        timeout=15
    )

    resposta.raise_for_status()

    return resposta.json()


st.title("Dashboard de monitoramento de IA")

st.caption(
    "Curso completo de Inteligência Artificial "
    "| MLOps | Aula 20"
)

st.divider()

if st.button("Atualizar dados"):
    st.cache_data.clear()
    st.rerun()

try:
    relatorio = carregar_json(
        "relatorio_monitoramento.json"
    )

except (requests.RequestException, ValueError) as erro:
    st.error(
        "Não foi possível carregar o relatório. "
        "Execute o workflow de monitoramento "
        "e verifique se o arquivo JSON foi "
        "publicado no repositório."
    )

    st.code(str(erro))
    st.stop()


psi = float(relatorio["psi"])
limite = float(relatorio["limite_alerta"])
alerta = bool(relatorio["alerta"])

quantidade = (
    relatorio["quantidade_referencia"]
    + relatorio["quantidade_atual"]
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "PSI",
        f"{psi:.4f}"
    )

with col2:
    st.metric(
        "Limite de alerta",
        f"{limite:.2f}"
    )

with col3:
    st.metric(
        "Documentos analisados",
        quantidade
    )

with col4:
    st.metric(
        "Versão do modelo",
        relatorio["versao"]
    )

st.divider()

if alerta:
    st.warning(
        "Mudança expressiva na distribuição "
        "das categorias previstas."
    )
else:
    st.success(
        "Distribuição dentro do limite "
        "demonstrativo configurado."
    )

st.info(
    "Este indicador não mede diretamente "
    "a acurácia do modelo."
)

st.subheader("Distribuição das previsões")

distribuicoes = relatorio["distribuicoes"]

linhas = []

for categoria, valores in distribuicoes.items():
    linhas.append({
        "Categoria": categoria,
        "Referência (%)": valores["referencia_pct"],
        "Atual (%)": valores["atual_pct"]
    })

df = pd.DataFrame(linhas)

st.bar_chart(
    df.set_index("Categoria"),
    y=["Referência (%)", "Atual (%)"]
)

st.subheader("Tabela de distribuições")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.divider()

st.subheader("Histórico de monitoramento")

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

        df_historico["execucao"] = range(
            1, len(df_historico) + 1
        )

        st.line_chart(
            df_historico.set_index("execucao")[
                ["psi"]
            ]
        )

        st.dataframe(
            df_historico,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "O histórico ainda está vazio."
        )

except (requests.RequestException, ValueError, KeyError):
    st.info(
        "Histórico ainda não disponível."
    )

st.divider()

st.caption(
    "Projeto educacional de monitoramento de IA. "
    "Os dados utilizados são sintéticos."
)
