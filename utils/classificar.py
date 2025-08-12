from openai import OpenAI
import streamlit as st
import unicodedata
import re

def criar_cliente_openai(api_key=None):
    if api_key is None:
        import streamlit as st
        api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    return OpenAI(api_key=api_key)

client = criar_cliente_openai()

def normalizar_texto(texto: str) -> str:
    """
    Remove acentos, espaços extras e converte texto para minúsculas.
    Util para padronizar strings para comparações.
    """
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto = re.sub(r'\s+', ' ', texto)  # normaliza múltiplos espaços para um só
    return texto.lower().strip()

def extrair_tipo_da_resposta(texto_resposta: str) -> str:
    """
    Extrai o tipo do documento a partir da resposta do modelo,
    buscando palavras-chave na resposta normalizada e mapeando para nomes com acento e capitalização corretos.
    """
    texto_normalizado = normalizar_texto(texto_resposta)
    tipos_validos = [
        "contrato", "termo aditivo", "relatorio", "oficio", "ata", "proposta",
        "minuta", "termo de apostilamento", "edital de licitacao", "termo de referencia", "outro"
    ]

    for tipo in tipos_validos:
        if tipo in texto_normalizado:
            # Mapeamento para forma corrigida de exibição
            mapeamento = {
                "relatorio": "Relatório",
                "oficio": "Ofício",
                "edital de licitacao": "Edital de Licitação",
                "termo de referencia": "Termo de Referência",
            }
            return mapeamento.get(tipo, tipo.title())

    return "Outro"

def eh_parte_de_edital(nome_arquivo: str) -> bool:
    """
    Verifica se o nome do arquivo contém palavras-chave típicas de documentos que fazem parte de um edital de licitação.
    """
    nome_norm = normalizar_texto(nome_arquivo)
    palavras_chave = [
        "edital", "licit", "instrucoes", "instruc", "lista de requerimentos",
        "criterio", "formulario", "modelo de acordo", "secao", "condicoes gerais",
        "questionario"
    ]
    return any(palavra in nome_norm for palavra in palavras_chave)

def normalizar_tipo_documento(tipo: str, nome_arquivo: str = None) -> str:
    """
    Normaliza o nome do tipo de documento para uma forma padronizada.
    Dá prioridade a "Edital de Licitação" se detectado no tipo ou nome do arquivo.
    """
    tipo_lower = normalizar_texto(tipo)
    
    if "edital de licitacao" in tipo_lower or (nome_arquivo and eh_parte_de_edital(nome_arquivo)):
        return "Edital de Licitação"
    
    mapeamento = {
        "contrato": "Contrato",
        "termo aditivo": "Termo Aditivo",
        "relatório": "Relatório",
        "ofício": "Ofício",
        "ata": "Ata",
        "proposta": "Proposta",
        "minuta": "Minuta",
        "termo de apostilamento": "Termo de Apostilamento",
        "termo de referência": "Termo de Referência",
    }
    
    for chave, valor in mapeamento.items():
        if chave in tipo_lower:
            return valor

    return "Outro"

@st.cache_data(show_spinner="Classificando documentos...")
def classificar_documento(nome_arquivo: str, conteudo_texto: str = None) -> str:
    """
    Classifica o tipo do documento utilizando o nome do arquivo e/ou o conteúdo do texto.
    Prioriza detectar se é parte de edital antes de usar o modelo da OpenAI para classificação.
    """
    if eh_parte_de_edital(nome_arquivo):
        return "Edital de Licitação"
    
    if conteudo_texto and conteudo_texto.strip():
        prompt = f"""
Classifique o tipo do documento com base no conteúdo abaixo:

{conteudo_texto[:4000]}  # Limitamos para evitar estourar o token

Escolha apenas UMA destas opções:
Contrato, Termo Aditivo, Relatório, Ofício, Ata, Proposta, Minuta,
Termo de Apostilamento, Edital de Licitação, Termo de Referência, Outro.
"""
    else:
        prompt = f"""
Classifique o tipo do documento com base no nome abaixo:

"{nome_arquivo}"

Escolha apenas UMA destas opções:
Contrato, Termo Aditivo, Relatório, Ofício, Ata, Proposta, Minuta,
Termo de Apostilamento, Edital de Licitação, Termo de Referência, Outro.
"""

    # Chamada à API OpenAI para obter a classificação
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20
    )

    tipo_cru_raw = response.choices[0].message.content.strip()
    tipo_cru = extrair_tipo_da_resposta(tipo_cru_raw)
    tipo_normalizado = normalizar_tipo_documento(tipo_cru, nome_arquivo)

    return tipo_normalizado
