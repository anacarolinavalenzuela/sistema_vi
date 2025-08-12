import streamlit as st
import base64

# ----- CONTROLE DE PÁGINAS -----

def mudar_pagina(pagina):
    """
    Atualiza a página exibida no app alterando o valor
    de 'page' no session_state.
    """
    st.session_state['page'] = pagina

# Inicializa a página padrão como 'inicio' se não existir
if 'page' not in st.session_state:
    st.session_state['page'] = 'inicio'


# ----- ESTILO GLOBAL -----

def carregar_css():
    """
    Lê o arquivo style.css e aplica o CSS customizado na página.
    """
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def carregar_imagem_fundo():
    """
    Tenta carregar a imagem 'fundo.png' e retorna em base64.
    Retorna None se o arquivo não existir.
    """
    try:
        with open("fundo.png", "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

# ----- APLICA ESTILO GLOBAL E IMAGEM DE FUNDO -----

carregar_css()

img_base64 = carregar_imagem_fundo()
if img_base64:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{img_base64}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        #overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0, 0, 0, 0.4);
            z-index: 0;
        }}
        .main {{
            position: relative;
            z-index: 1;
        }}
        div.stButton > button {{
            width: 210px;
            font-size: 1.1rem;
            padding: 0.6em 1em;
            white-space: nowrap;
            font-family: 'Montserrat', sans-serif !important;
            font-weight: bold;
        }}
        </style>        
        """,
        unsafe_allow_html=True
    )





# ----- PÁGINAS -----

## Página: INÍCIO
if st.session_state['page'] == 'inicio':
    st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="
            background-color: rgba(255, 255, 255, 0.85);
            padding: 40px;
            border-radius: 12px;
            text-align: center;
            color: black;
            ">
            <h1 style="margin-bottom: 20px;">Bem Vindo ao Sistema de Análise de Documentos</h1>
            <p style="font-weight: bold;">
            Envie seus documentos e conte com o sistema para identificar prazos, 
            gerar resumos objetivos, classificar os tipos de arquivos e interagir por meio de um chat inteligente.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

    _, col1, _ = st.columns([0.7, 1, 0.3])
    with col1:
        st.button("Começar", on_click=mudar_pagina, args=('upload',))


## Página: UPLOAD
elif st.session_state['page'] == 'upload':

    st.markdown("<div style='margin-top: 45px;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="
            background-color: rgba(255, 255, 255, 0.85);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            color: black;
            ">
            <h1 style="margin-bottom: 10px;">Upload de Documentos</h1>
            <p style="font-size: 1.1rem;">Carregue seus documentos (PDF, DOCX, PPTX, XLSX, TXT) ou uma pasta comprimida (.zip). </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

    # Inicializa chave para resetar uploader e forçar atualização
    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = 0

    col_up1, col_up2, col_up3 = st.columns([0.3, 3, 0.3])
    with col_up2:
        uploaded_files = st.file_uploader(
            label="",
            type=["pdf", "docx", "pptx", "xlsx", "txt", "zip"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key=st.session_state["uploader_key"]
        )

    if uploaded_files:
        if "uploaded_files_bytes" not in st.session_state:
            st.session_state["uploaded_files_bytes"] = {}

        # Armazena os arquivos carregados em bytes no session_state para manter entre páginas
        for f in uploaded_files:
            if f.name not in st.session_state["uploaded_files_bytes"]:
                st.session_state["uploaded_files_bytes"][f.name] = f.read()

        # Cria a lista com nome e conteúdo dos arquivos para uso nas outras páginas
        st.session_state["uploaded_files"] = [
            {"name": nome, "content": conteudo}
            for nome, conteudo in st.session_state["uploaded_files_bytes"].items()
        ]

        st.session_state["uploaded_files_names"] = list(st.session_state["uploaded_files_bytes"].keys())
        st.session_state["arquivos_limpos"] = False

    # Mostra mensagem de sucesso com a quantidade de arquivos carregados
    if "uploaded_files_names" in st.session_state and st.session_state["uploaded_files_names"]:
        st.success(f"{len(st.session_state['uploaded_files_names'])} arquivo(s) carregado(s).")

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

    # Botões para limpar arquivos ou continuar para próxima página
    col_esq, col_btn1, col_espaco, col_btn2, col_dir = st.columns([1.2, 1.7, 0.1, 2, 1])

    with col_btn1:
        if st.button("Limpar Arquivos"):
            # Remove os arquivos da sessão e reinicia o uploader
            st.session_state.pop("uploaded_files", None)
            st.session_state.pop("uploaded_files_names", None)
            st.session_state.pop("uploaded_files_bytes", None)
            st.session_state["arquivos_limpos"] = True
            st.session_state["uploader_key"] += 1  # força o reset do uploader
            st.rerun()

    with col_btn2:
        # Avança para o menu principal
        st.button("Continuar", on_click=mudar_pagina, args=("menu",))

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    # Botão para voltar à página inicial
    _, col1, _ = st.columns([0.7, 1, 0.3])
    with col1:
        st.button("Voltar para o Início", on_click=mudar_pagina, args=('inicio',))


## Página: MENU
elif st.session_state['page'] == 'menu':
    st.markdown("<div style='margin-top: 130px;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="
            background-color: rgba(255, 255, 255, 0.85);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            color: black;
            ">
            <h1 style="margin-bottom: 10px;">O que deseja visualizar?</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

    # Botões para escolher a funcionalidade desejada
    col_esq, col_btn1, col_espaco, col_btn2, col_espaco2, col_btn3, col_dir = st.columns([0.01, 0.28, 0.6, 0.4, 0.5, 0.75, 0.2])
    with col_btn1:
        st.button("Resumo dos documentos", on_click=mudar_pagina, args=('resumo',))
    with col_btn2:
        st.button("Prazos Importantes", on_click=mudar_pagina, args=('prazos',))
    with col_btn3:
        st.button("Chat com os documentos", on_click=mudar_pagina, args=('chat',))

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

    # Botão para voltar ao upload
    col_left, col_center, col_right = st.columns([1.3, 1, 1.5])
    with col_center:
        st.button("Voltar ao Upload de Arquivos", on_click=mudar_pagina, args=('upload',))


## Página: RESUMO
elif st.session_state['page'] == 'resumo':
    from resumo import mostrar_resumo
    mostrar_resumo()

    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

    # Botões para navegação entre páginas
    col_esq, col_btn1, col_espaco, col_btn2, col_espaco2, col_btn3, col_dir = st.columns([0.2, 0.75, 1, 0.75, 1, 0.5, 1.4])
    with col_btn1:
        st.button("Voltar ao Início", on_click=lambda: st.session_state.update({'page': 'inicio'}))
    with col_btn2:
        st.button("Voltar ao Upload", on_click=lambda: st.session_state.update({'page': 'upload'}))
    with col_btn3:
        st.button("Voltar ao Menu", on_click=lambda: st.session_state.update({'page': 'menu'}))

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

elif st.session_state['page'] == 'resumo_tipo':
    from resumo import mostrar_resumo_tipo
    mostrar_resumo_tipo()

    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

    col_esq, col_btn1, col_espaco, col_btn2, col_espaco2, col_btn3, col_dir = st.columns([0.2, 0.75, 1, 0.75, 1, 0.5, 1.4])
    with col_btn1:
        st.button("Voltar ao Início", on_click=lambda: st.session_state.update({'page': 'inicio'}))
    with col_btn2:
        st.button("Voltar ao Upload", on_click=lambda: st.session_state.update({'page': 'upload'}))
    with col_btn3:
        st.button("Voltar ao Menu", on_click=lambda: st.session_state.update({'page': 'menu'}))

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

## Página: PRAZOS
elif st.session_state['page'] == 'prazos':
    from utils.prazos import mostrar_prazos
    mostrar_prazos()

    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

    col_esq, col_btn1, col_espaco, col_btn2, col_espaco2, col_btn3, col_dir = st.columns([0.2, 0.75, 1, 0.75, 1, 0.5, 1.4])
    with col_btn1:
        st.button("Voltar ao Início", on_click=lambda: st.session_state.update({'page': 'inicio'}))
    with col_btn2:
        st.button("Voltar ao Upload", on_click=lambda: st.session_state.update({'page': 'upload'}))
    with col_btn3:
        st.button("Voltar ao Menu", on_click=lambda: st.session_state.update({'page': 'menu'}))

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

elif st.session_state['page'] == 'prazos_tipo':
    from utils.prazos import mostrar_prazos_tipo
    mostrar_prazos_tipo()

    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

    col_esq, col_btn1, col_espaco, col_btn2, col_espaco2, col_btn3, col_dir = st.columns([0.2, 0.75, 1, 0.75, 1, 0.5, 1.4])
    with col_btn1:
        st.button("Voltar ao Início", on_click=lambda: st.session_state.update({'page': 'inicio'}))
    with col_btn2:
        st.button("Voltar ao Upload", on_click=lambda: st.session_state.update({'page': 'upload'}))
    with col_btn3:
        st.button("Voltar ao Menu", on_click=lambda: st.session_state.update({'page': 'menu'}))

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

## Página: CHAT
elif st.session_state['page'] == 'chat':
    from utils.chat import mostrar_chat
    mostrar_chat()

    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

    col_esq, col_btn1, col_espaco, col_btn2, col_espaco2, col_btn3, col_dir = st.columns([0.2, 0.75, 1, 0.75, 1, 0.5, 1.4])
    with col_btn1:
        st.button("Voltar ao Início", on_click=lambda: st.session_state.update({'page': 'inicio'}))
    with col_btn2:
        st.button("Voltar ao Upload", on_click=lambda: st.session_state.update({'page': 'upload'}))
    with col_btn3:
        st.button("Voltar ao Menu", on_click=lambda: st.session_state.update({'page': 'menu'}))

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
