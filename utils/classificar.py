from openai import OpenAI
import streamlit as st
import unicodedata
import re
import os

def criar_cliente_openai():
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY não está configurada no ambiente")
    return OpenAI(api_key=api_key)

def normalizar_texto(texto: str) -> str:
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto = re.sub(r'\s+', ' ', texto)
    return texto.lower().strip()

def extrair_tipo_da_resposta(texto_resposta: str) -> str:
    texto_normalizado = normalizar_texto(texto_resposta)
    tipos_validos = [
        "contrato", "termo aditivo", "relatorio", "oficio", "ata", "proposta",
        "minuta", "termo de apostilamento", "edital de licitacao", "termo de referencia", "outro"
    ]

    for tipo in tipos_validos:
        if tipo in texto_normalizado:
            mapeamento = {
                "relatorio": "Relatório",
                "oficio": "Ofício",
                "edital de licitacao": "Edital de Licitação",
                "termo de referencia": "Termo de Referência",
            }
            return mapeamento.get(tipo, tipo.title())

    return "Outro"

def eh_parte_de_edital(nome_arquivo: str) -> bool:
    nome_norm = normalizar_texto(nome_arquivo)
    palavras_chave = [
        "edital", "licit", "instrucoes", "instruc", "lista de requerimentos",
        "criterio", "formulario", "modelo de acordo", "secao", "condicoes gerais",
        "questionario"
    ]
    return any(palavra in nome_norm for palavra in palavras_chave)

def normalizar_tipo_documento(tipo: str, nome_arquivo: str = None) -> str:
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

def classificar_documento(nome_arquivo: str, conteudo_texto: str = None, client=None) -> str:
    if client is None:
        raise ValueError("Client OpenAI deve ser passado para classificar_documento")
    
    if eh_parte_de_edital(nome_arquivo):
        return "Edital de Licitação"
    
    if conteudo_texto and conteudo_texto.strip():
        prompt = f"""
Classifique o tipo do documento com base no conteúdo abaixo:

{conteudo_texto[:4000]}

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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20
    )

    tipo_cru_raw = response.choices[0].message.content.strip()
    tipo_cru = extrair_tipo_da_resposta(tipo_cru_raw)
    tipo_normalizado = normalizar_tipo_documento(tipo_cru, nome_arquivo)

    return tipo_normalizado


@st.cache_data(show_spinner="Classificando os documentos...")
def classificar_com_cache(nome_arquivo: str, conteudo_texto: str = None) -> str:
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    return classificar_documento(nome_arquivo, conteudo_texto, client=client)
