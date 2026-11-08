
"""
Aplicação principal
BRITO SOLUÇÕES TECNOLOGICAS

Plataforma científica de monitoramento
e governança de inteligência artificial.

Páginas:
- Central de monitoramento
- Detecção de anomalias
- Auditoria e governança
- Experimentos e versionamento
"""

import streamlit as st


st.set_page_config(
    page_title="Plataforma de IA | BRITO",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================
# CENTRAL DE MONITORAMENTO
# ============================================

pagina_monitoramento = st.Page(
    "dashboard.py",
    title="Central de monitoramento",
    icon="📊",
    default=True,
    url_path=""
)


# ============================================
# DETECÇÃO DE ANOMALIAS
# ============================================

pagina_anomalias = st.Page(
    "pages/1_Anomalias.py",
    title="Detecção de anomalias",
    icon="🔴",
    url_path="Anomalias"
)


# ============================================
# AUDITORIA E GOVERNANÇA
# ============================================

pagina_auditoria = st.Page(
    "pages/2_Auditoria.py",
    title="Auditoria e governança",
    icon="🛡️",
    url_path="Auditoria"
)


# ============================================
# EXPERIMENTOS E VERSIONAMENTO
# ============================================

pagina_experimentos = st.Page(
    "pages/3_Experimentos.py",
    title="Experimentos e versionamento",
    icon="📈",
    url_path="Experimentos"
)


# ============================================
# NAVEGAÇÃO PRINCIPAL
# ============================================

navegacao = st.navigation(
    {
        "Monitoramento de IA": [
            pagina_monitoramento,
            pagina_anomalias,
            pagina_auditoria,
            pagina_experimentos
        ]
    },
    position="sidebar"
)

navegacao.run()
