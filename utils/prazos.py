import streamlit as st
from io import BytesIO
from utils.classificar import classificar_documento, normalizar_tipo_documento, criar_cliente_openai
from utils.extrair_texto import extrair_texto
from utils.llm import contar_tokens, dividir_em_chunks
from prompts import PROMPT_PRAZOS


def limitar_prazos(texto: str, max_itens: int = 10) -> list:
    """
    Filtra linhas que começam com marcadores típicos de tópicos de prazos.
    Retorna até max_itens prazos encontrados.
    """
    linhas = [
        linha.strip("-•– ").strip()
        for linha in texto.splitlines()
        if linha.strip().startswith(("-", "•", "–"))
    ]
    return linhas[:max_itens] if linhas else []

@st.cache_data(show_spinner="Extraindo prazos...", ttl=3600)
def extrair_prazos_importantes(file, filename, modelo="gpt-3.5-turbo") -> list:
    """
    Extrai os prazos importantes de um documento usando o prompt específico.
    Divide texto em partes se for muito longo para evitar limite de tokens.
    Retorna lista filtrada e sem duplicatas.
    """
    texto = extrair_texto(file, filename)

    if contar_tokens(texto, modelo) > 10000:
        partes = dividir_em_chunks(texto, max_tokens=3000, modelo=modelo)
    else:
        partes = [texto]

    prazos_extraidos = []

    for i, parte in enumerate(partes):
        prompt = f"""{PROMPT_PRAZOS}

Texto:
\"\"\"{parte}\"\"\"
"""
        try:
            client = criar_cliente_openai()
            resposta = client.chat.completions.create(
                model=modelo,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            conteudo = resposta.choices[0].message.content.strip()

            topicos = limitar_prazos(conteudo)
            prazos_filtrados = [
                t for t in topicos
                if "não especificado" not in t.lower()
                and "ver cláusula" not in t.lower()
                and len(t.split(":")) > 1
            ]
            prazos_extraidos.extend(prazos_filtrados)

        except Exception as e:
            prazos_extraidos.append(f"Erro ao processar parte {i+1}: {e}")

    # Remove duplicatas e limita a 10 prazos
    return list(dict.fromkeys(prazos_extraidos))[:10]

def mostrar_prazos_tipo():
    """
    Exibe interface Streamlit para mostrar prazos extraídos de documentos filtrados por tipo.
    """
    tipo = st.session_state.get("tipo_para_prazo", None)
    arquivos = st.session_state.get("uploaded_files", None)

    if not tipo or not arquivos:
        st.warning("Não há documentos para extrair prazos.")
        return

    st.markdown(f"""
        <div style="
            background-color: rgba(255, 255, 255, 0.85);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            color: black;">
            <h1>Prazos do tipo: {tipo}</h1>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    arquivos_selecionados = [
        arq for arq in arquivos
        if normalizar_tipo_documento(classificar_documento(arq["name"]), arq["name"]) == tipo
    ]

    if not arquivos_selecionados:
        st.info(f"Nenhum documento do tipo **{tipo}** foi encontrado.")
        return

    for file in arquivos_selecionados:
        st.markdown("---")
        st.markdown(f"### 📎 {file['name']}")
        with st.spinner("Extraindo prazos..."):
            prazos = extrair_prazos_importantes(BytesIO(file["content"]), file["name"])
        if not prazos:
            st.warning("Nenhum prazo encontrado.")
        else:
            for p in prazos:
                st.markdown(f"- {p}")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    _, col1, _ = st.columns([1.6, 2, 1])
    with col1:
        st.button("Voltar ao menu de prazos", on_click=lambda: st.session_state.update({"page": "prazos"}))


def mostrar_prazos():
    """
    Exibe interface principal de prazos com lista de documentos agrupados por tipo
    e permite escolher tipo para extrair prazos detalhados.
    """
    st.markdown("""
        <div style="
            background-color: rgba(255, 255, 255, 0.80);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            color: black;">
            <h1>Prazos por Tipo de Documento</h1>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

    if "uploaded_files" not in st.session_state or not st.session_state.uploaded_files:
        st.warning("Nenhum arquivo foi enviado. Volte à página de Upload.")
        return

    arquivos = st.session_state["uploaded_files"]
    classificacoes = {}

    for file in arquivos:
        tipo = normalizar_tipo_documento(classificar_documento(file["name"]), file["name"])

        if tipo not in classificacoes:
            classificacoes[tipo] = []
        classificacoes[tipo].append(file)

    for tipo, arquivos_tipo in classificacoes.items():
        with st.expander(f"{tipo} ({len(arquivos_tipo)} arquivo(s))"):
            for file in arquivos_tipo:
                st.markdown(f"- {file['name']}")

    tipos_disponiveis = list(classificacoes.keys())

    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

    # Selecionar tipo para extrair prazos
    st.markdown(f"### Escolha o tipo de documento para extrair os prazos")
    tipo_escolhido = st.selectbox("", tipos_disponiveis)

    _, col1, _ = st.columns([1.6, 2, 1])
    with col1:
        if st.button("Extrair prazos deste tipo"):
            st.session_state["tipo_para_prazo"] = tipo_escolhido
            st.session_state["page"] = "prazos_tipo"
            st.rerun()
