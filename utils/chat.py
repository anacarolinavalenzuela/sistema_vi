import streamlit as st
from utils.extrair_texto import extrair_texto
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LCDocument
from io import BytesIO

def criar_chain(textos):
    """
    Cria um ConversationalRetrievalChain a partir de uma lista de textos.
    Divide textos em chunks, cria embeddings e indexa em FAISS para buscas.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = text_splitter.split_text("\n\n".join(textos))
    docs = [LCDocument(page_content=chunk) for chunk in chunks]
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = ChatOpenAI(temperature=0.3)
    return ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever)

def mostrar_baloes(chat_history):
    """
    Renderiza as mensagens da conversa em balões estilizados, separando pergunta e resposta.
    """
    for pergunta, resposta in chat_history:
        st.markdown(f"""
        <div style='text-align: right; margin: 8px 0;'>
            <span style='
                background-color: #DCF8C6;
                color: #000;
                padding: 8px 12px;
                border-radius: 15px 15px 0 15px;
                display: inline-block;
                max-width: 70%;
                word-wrap: break-word;
                font-size: 15px;
                box-shadow: 1px 1px 2px #aaa;
            '>{pergunta}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='text-align: left; margin: 8px 0;'>
            <span style='
                background-color: #FFF;
                color: #000;
                padding: 8px 12px;
                border-radius: 15px 15px 15px 0;
                display: inline-block;
                max-width: 70%;
                word-wrap: break-word;
                font-size: 15px;
                box-shadow: 1px 1px 2px #aaa;
            '>{resposta}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<div id='end_chat'></div>", unsafe_allow_html=True)
    st.markdown("""
        <script>
            const endChat = window.parent.document.querySelector('#end_chat');
            if(endChat){
                endChat.scrollIntoView({behavior: 'smooth'});
            }
        </script>
    """, unsafe_allow_html=True)

def mostrar_chat():
    """
    Exibe a interface do chat que permite perguntas sobre todos os documentos ou um documento específico.
    Gerencia o estado da conversa e da interface usando st.session_state.
    """
    st.markdown("""
        <div style="background-color: rgba(255, 255, 255, 0.85); 
        padding: 20px; 
        border-radius: 12px; 
        text-align: center; 
        color: black;">
            <h1 style="margin-bottom: 2px;">Chat com os Documentos</h1>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

    if "uploaded_files" not in st.session_state or not st.session_state.uploaded_files:
        st.warning("Nenhum documento enviado ainda. Volte à página de Upload.")
        return

    arquivos = st.session_state["uploaded_files"]
    nomes = st.session_state["uploaded_files_names"]

    # Inicializa estados do chat geral (todos documentos)
    if "chat_todos" not in st.session_state:
        st.session_state.chat_todos = []

    if "limpar_input_todos" not in st.session_state:
        st.session_state.limpar_input_todos = False

    if st.session_state.limpar_input_todos:
        st.session_state.input_todos = ""
        st.session_state.limpar_input_todos = False

    # Cria chain para todos os documentos, só uma vez, e guarda na sessão
    if "chain_todos" not in st.session_state:
        textos_todos = [extrair_texto(BytesIO(f["content"]), f["name"]) for f in arquivos]
        st.session_state.chain_todos = criar_chain(textos_todos)

    chain_todos = st.session_state.chain_todos

    st.markdown("### 📄 Pergunte algo sobre todos os documentos:")

    col1, col2 = st.columns([8, 1])
    with col1:
        pergunta_todos = st.text_input(
            "Exemplos:\n1) Qual foi a mudança entre o último termo aditivo e o primeiro contrato?; Teve alguma alteração no valor do projeto ao longo dos documentos?",
            key="input_todos",
            help="Digite abaixo sua pergunta"
        )
    with col2:
        if st.button("Limpar conversa", key="limpar_todos"):
            st.session_state.chat_todos = []
            st.session_state.limpar_input_todos = True
            st.rerun()

    if pergunta_todos:
        with st.spinner("🔎 Buscando resposta..."):
            result = chain_todos({
                "question": pergunta_todos,
                "chat_history": st.session_state.chat_todos
            })
            resposta = result["answer"]
            st.session_state.chat_todos.append((pergunta_todos, resposta))
            st.session_state.limpar_input_todos = True

    mostrar_baloes(st.session_state.chat_todos)

    # -------------------------------
    # CHAT COM UM DOCUMENTO ESPECÍFICO
    # -------------------------------

    st.markdown("<div style='margin-top: 50px;'></div>")
    st.markdown("### 📄 Pergunte algo sobre um documento específico:")
    doc_escolhido = st.selectbox("", nomes, key="doc_escolhido")

    if doc_escolhido:
        key_chat = f"chat_{doc_escolhido}"
        key_input = f"input_individual_{doc_escolhido}"
        key_limpar = f"limpar_individual_{doc_escolhido}"
        key_flag_limpar = f"limpar_input_{doc_escolhido}"
        key_chain_individual = f"chain_{doc_escolhido}"

        if key_chat not in st.session_state:
            st.session_state[key_chat] = []

        if key_flag_limpar not in st.session_state:
            st.session_state[key_flag_limpar] = False

        if st.session_state[key_flag_limpar]:
            st.session_state[key_input] = ""
            st.session_state[key_flag_limpar] = False

        # Cria chain individual do documento escolhido, só uma vez e guarda na sessão
        if key_chain_individual not in st.session_state:
            file_data = next(f for f in arquivos if f["name"] == doc_escolhido)
            file_obj = BytesIO(file_data["content"])
            texto = extrair_texto(file_obj, file_data["name"])
            st.session_state[key_chain_individual] = criar_chain([texto])

        chain_individual = st.session_state[key_chain_individual]

        col1, col2 = st.columns([8, 1])
        with col1:
            pergunta_individual = st.text_input(
                "Exemplos:\n1) Quais são as atividades presentes na proposta?; Esse termo aditivo mudou o prazo do contrato?",
                key=key_input,
                help=f"Digite abaixo uma pergunta sobre {doc_escolhido}"
            )
        with col2:
            if st.button("Limpar conversa", key=key_limpar):
                st.session_state[key_chat] = []
                st.session_state[key_flag_limpar] = True
                st.rerun()

        if pergunta_individual:
            with st.spinner("🔎 Buscando resposta..."):
                result = chain_individual({
                    "question": pergunta_individual,
                    "chat_history": st.session_state[key_chat]
                })
                resposta = result["answer"]
                st.session_state[key_chat].append((pergunta_individual, resposta))
                st.session_state[key_flag_limpar] = True

        mostrar_baloes(st.session_state[key_chat])
