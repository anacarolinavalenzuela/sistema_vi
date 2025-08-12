import streamlit as st
from io import BytesIO
from utils.classificar import classificar_documento, normalizar_tipo_documento
from utils.extrair_texto import extrair_texto
from utils.llm import gerar_resumo_padronizado
from utils.html_fix import force_all_to_ol 

@st.cache_data(show_spinner="Gerando resumo...")
def gerar_resumo_com_cache(nome_arquivo, texto, tipo):
    """
    Gera um resumo padronizado do texto, com cache para melhorar performance.
    Retorna aviso se texto estiver vazio.
    """
    if not texto or len(texto.strip()) == 0:
        return "⚠️ Texto vazio ou não extraído para este documento."
    return gerar_resumo_padronizado(texto, tipo)


def mostrar_resumo_tipo():
    """
    Exibe resumos para os documentos filtrados por tipo escolhido na sessão.
    Extrai texto, classifica documentos, filtra pelo tipo e gera resumos formatados.
    """
    tipo = st.session_state.get("tipo_para_resumir", None)
    arquivos = st.session_state.get("uploaded_files", None)

    if not tipo or not arquivos:
        st.warning("Não há documentos para resumir.")
        return

    # Cabeçalho da seção de resumo do tipo selecionado
    st.markdown(f"""
        <div style="
            background-color: rgba(255, 255, 255, 0.85);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            color: black;
            ">
            <h1>📑 Resumos do tipo: {tipo}</h1>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    arquivos_selecionados = []
    textos_cache = {}

    # Extrair texto e classificar documentos para filtrar por tipo desejado
    for arq in arquivos:
        texto_tmp = extrair_texto(BytesIO(arq["content"]), arq["name"])
        textos_cache[arq["name"]] = texto_tmp
        tipo_classificado = normalizar_tipo_documento(classificar_documento(arq["name"], texto_tmp), arq["name"])
        tipo_desejado = normalizar_tipo_documento(tipo)
        if tipo_classificado == tipo_desejado:
            arquivos_selecionados.append(arq)

    if not arquivos_selecionados:
        st.info(f"Nenhum documento do tipo **{tipo}** foi encontrado.")
        return

    # Para cada arquivo filtrado, gerar e mostrar resumo formatado
    for file in arquivos_selecionados:
        st.markdown("---")
        st.markdown(f"### 📎 {file['name']}")
        with st.spinner("Extraindo e resumindo..."):
            texto = textos_cache.get(file["name"])
            resumo = gerar_resumo_com_cache(file["name"], texto, tipo)
            resumo = force_all_to_ol(resumo)  # Ajusta HTML para listas ordenadas
        st.markdown(resumo, unsafe_allow_html=True)  

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # Botão para voltar ao menu anterior de resumos
    _, col1, _ = st.columns([1.6, 2, 1])
    with col1:
        st.button("Voltar ao menu de resumos", on_click=lambda: st.session_state.update({"page": "resumo"}))


@st.cache_data(show_spinner="Classificando os documentos...")
def classificar_com_cache(nome_arquivo: str, conteudo_texto: str = None, client=None) -> str:
    if client is None:
        raise ValueError("O client OpenAI deve ser passado para classificar_com_cache")
    return classificar_documento(nome_arquivo, conteudo_texto, client=client)


def mostrar_resumo():
    """
    Interface para mostrar resumo geral e permitir selecionar o tipo de documento para resumir.
    Organiza o fluxo em 2 etapas:
    1. Classificar documentos enviados
    2. Selecionar tipo para gerar resumos
    """
    st.markdown("""
        <div style="
            background-color: rgba(255, 255, 255, 0.85);
            padding: 10px;
            border-radius: 12px;
            text-align: center;
            color: black;
            ">
            <h1 style="margin-bottom: 10px;">Resumo dos Documentos</h1>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

    if "uploaded_files" not in st.session_state or not st.session_state.uploaded_files:
        st.warning("Nenhum arquivo foi enviado. Volte à página de Upload.")
        return

    files = st.session_state["uploaded_files"]

    # 1. Classificar documentos
    st.markdown(f"### Classificação automática dos arquivos")
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

    classificacoes = {}
    for file in files:
        texto = extrair_texto(BytesIO(file["content"]), file["name"])
        tipo = normalizar_tipo_documento(classificar_com_cache(file["name"], texto, client=client), file["name"])

        if tipo not in classificacoes:
            classificacoes[tipo] = []
        classificacoes[tipo].append(file)

    # Mostrar documentos agrupados por tipo com expander
    for tipo, arquivos in classificacoes.items():
        with st.expander(f"{tipo} ({len(arquivos)} arquivo(s))"):
            for file in arquivos:
                st.markdown(f"- {file['name']}")

    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

    # 2. Selecionar tipo para resumir
    st.markdown(f"### Escolha o tipo de documento que deseja resumir")

    tipos_disponiveis = list(classificacoes.keys())
    tipo_escolhido = st.selectbox("", tipos_disponiveis)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    _, col1, _ = st.columns([1.6, 2, 1])
    with col1:
        if st.button("Gerar resumos para este tipo", key="gerar_resumo_tipo"):
            # Atualiza estado para ir para página de resumo específico
            st.session_state["tipo_para_resumir"] = tipo_escolhido
            st.session_state["page"] = "resumo_tipo"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
