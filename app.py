
"""
Aplicação principal
BRITO SOLUÇÕES TECNOLOGICAS

Sistema integrado de monitoramento,
detecção de anomalias e auditoria de IA.
"""

import streamlit as st


st.set_page_config(
    page_title="Monitoramento de IA | BRITO",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# PÁGINAS DA APLICAÇÃO
# ==========================================

pagina_monitoramento = st.Page(
    "dashboard.py",
    title="Central de monitoramento",
    icon="📊",
    default=True,
    url_path=""
)

pagina_anomalias = st.Page(
    "pages/1_Anomalias.py",
    title="Detecção de anomalias",
    icon="🔴",
    url_path="Anomalias"
)

pagina_auditoria = st.Page(
    "pages/2_Auditoria.py",
    title="Auditoria e governança",
    icon="🛡️",
    url_path="Auditoria"
)


# ==========================================
# NAVEGAÇÃO CENTRALIZADA
# ==========================================

navegacao = st.navigation(
    {
        "Monitoramento de IA": [
            pagina_monitoramento,
            pagina_anomalias,
            pagina_auditoria
        ]
    },
    position="sidebar"
)

navegacao.run()
