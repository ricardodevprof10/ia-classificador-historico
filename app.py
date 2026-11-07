
"""
BRITO SOLUÇÕES TECNOLOGICAS

Navegação principal da plataforma de
monitoramento de inteligência artificial.

Páginas:
- Central de monitoramento de IA
- Detecção de anomalias
"""

from pathlib import Path

import streamlit as st


DIRETORIO_PROJETO = Path(__file__).resolve().parent

ARQUIVO_DASHBOARD = DIRETORIO_PROJETO / "dashboard.py"

ARQUIVO_ANOMALIAS = (
    DIRETORIO_PROJETO
    / "pages"
    / "1_Anomalias.py"
)


def iniciar_aplicacao():

    arquivos_ausentes = []

    if not ARQUIVO_DASHBOARD.is_file():
        arquivos_ausentes.append("dashboard.py")

    if not ARQUIVO_ANOMALIAS.is_file():
        arquivos_ausentes.append(
            "pages/1_Anomalias.py"
        )

    if arquivos_ausentes:
        st.error(
            "Não foi possível iniciar a navegação. "
            "Os seguintes arquivos não foram encontrados:"
        )

        for arquivo in arquivos_ausentes:
            st.code(arquivo)

        st.stop()

    pagina_monitoramento = st.Page(
        "dashboard.py",
        title="Central de monitoramento",
        icon="📊",
        default=True
    )

    pagina_anomalias = st.Page(
        "pages/1_Anomalias.py",
        title="Detecção de anomalias",
        icon="🔴"
    )

    navegacao = st.navigation(
        {
            "Monitoramento de IA": [
                pagina_monitoramento,
                pagina_anomalias
            ]
        },
        position="sidebar",
        expanded=True
    )

    navegacao.run()


if __name__ == "__main__":
    iniciar_aplicacao()
