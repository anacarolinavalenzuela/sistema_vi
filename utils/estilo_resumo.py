def aplicar_estilo_resumo():
    """Aplica estilos customizados apenas para a página de resumo."""
    import streamlit as st
    st.markdown(
        """
        <style>
        /* Padrão para todos os <p> */
        div.st-emotion-cache-9fqyt2 p {
            background-color: rgba(255, 255, 255, 0.85);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.3rem;
            box-shadow: 0 0 6px rgba(0, 0, 0, 0.05);
        }

        /* OL e UL com mesma aparência */
        div.st-emotion-cache-9fqyt2 ol,
        div.st-emotion-cache-9fqyt2 ul {
            background-color: rgba(255, 255, 255, 0.85);
            padding: 1rem 2rem;
            border-radius: 10px;
            box-shadow: 0 0 6px rgba(0, 0, 0, 0.05);
            margin-bottom: 1.3rem;
        }

        /* Espaçamento entre itens */
        div.st-emotion-cache-9fqyt2 ol > li,
        div.st-emotion-cache-9fqyt2 ul > li {
            margin-bottom: 1.25rem; /* mais espaçado */
            line-height: 1.6; /* mais respiro no texto */
        }

        /* Marcadores OL */
        div.st-emotion-cache-9fqyt2 ol > li::marker {
            color: #484F70;
            font-weight: bold;
            font-size: 1.1em;
        }

        /* Marcadores UL */
        div.st-emotion-cache-9fqyt2 ul > li::marker {
            color: #484F70;
            font-size: 1.05em;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
