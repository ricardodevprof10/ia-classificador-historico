
"""
Classificador de documentos históricos.

Curso completo de Inteligência Artificial
Aula 17 - CI/CD com GitHub Actions
"""

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


DADOS = [
    ("A escola recebeu novos professores.", "Educação"),
    ("A universidade ampliou seus cursos.", "Educação"),
    ("Os estudantes receberam livros escolares.", "Educação"),
    ("O ensino público passou por reformas.", "Educação"),
    ("A alfabetização foi prioridade.", "Educação"),
    ("O município inaugurou novas salas de aula.", "Educação"),

    ("O comércio de café cresceu.", "Economia"),
    ("A indústria aumentou sua produção.", "Economia"),
    ("Os bancos financiaram empresas.", "Economia"),
    ("Os comerciantes ampliaram exportações.", "Economia"),
    ("A inflação elevou os preços.", "Economia"),
    ("A agricultura movimentou o mercado.", "Economia"),

    ("O parlamento aprovou uma lei.", "Política"),
    ("O presidente anunciou reformas.", "Política"),
    ("Os partidos disputaram eleições.", "Política"),
    ("Os deputados debateram propostas.", "Política"),
    ("O governo publicou um decreto.", "Política"),
    ("A constituição estabeleceu direitos.", "Política"),

    ("O museu organizou uma exposição.", "Cultura"),
    ("Os artistas apresentaram pinturas.", "Cultura"),
    ("A comunidade realizou um festival.", "Cultura"),
    ("O teatro recebeu apresentações.", "Cultura"),
    ("A literatura preservou tradições.", "Cultura"),
    ("A música marcou as celebrações.", "Cultura")
]


def criar_modelo():
    """Cria um pipeline de classificação de textos."""

    return Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2)
            )
        ),
        (
            "classificador",
            LogisticRegression(
                max_iter=1000,
                random_state=42
            )
        )
    ])


def treinar_modelo():
    """Treina o classificador com dados demonstrativos."""

    textos = [texto for texto, _ in DADOS]
    categorias = [categoria for _, categoria in DADOS]

    modelo = criar_modelo()
    modelo.fit(textos, categorias)

    return modelo


def classificar_texto(modelo, texto):
    """Classifica um texto e retorna a categoria prevista."""

    if not isinstance(texto, str):
        raise TypeError("O texto deve ser uma string.")

    if not texto.strip():
        raise ValueError("O texto não pode estar vazio.")

    return str(modelo.predict([texto])[0])


if __name__ == "__main__":

    modelo = treinar_modelo()

    exemplo = "A escola inaugurou novas salas."

    resultado = classificar_texto(modelo, exemplo)

    print("Texto:", exemplo)
    print("Categoria prevista:", resultado)
