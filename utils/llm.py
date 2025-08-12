from openai import OpenAI
import tiktoken
from prompts import PROMPTS_PADRONIZADOS
from utils.classificar import criar_cliente_openai

client = criar_cliente_openai()

def contar_tokens(texto, modelo="gpt-3.5-turbo"):
    """Conta a quantidade de tokens de um texto dado um modelo."""
    enc = tiktoken.encoding_for_model(modelo)
    return len(enc.encode(texto))

def dividir_em_chunks(texto, max_tokens=3000, modelo="gpt-3.5-turbo"):
    """
    Divide o texto em pedaços (chunks) que não ultrapassem max_tokens.
    Útil para textos grandes que precisam ser processados em partes.
    """
    enc = tiktoken.encoding_for_model(modelo)
    tokens = enc.encode(texto)
    chunks = [enc.decode(tokens[i:i+max_tokens]) for i in range(0, len(tokens), max_tokens)]
    return chunks

def gerar_resumo_padronizado(texto, tipo_documento, modelo="gpt-3.5-turbo"):
    """
    Gera um resumo detalhado e estruturado de um texto, adaptado ao tipo do documento.
    Usa prompts padronizados por tipo para direcionar a geração.
    Divide textos muito grandes em partes e gera resumos parciais antes do resumo final.
    """
    tipo = tipo_documento.strip()
    prompt_base = PROMPTS_PADRONIZADOS.get(tipo, PROMPTS_PADRONIZADOS["default"])

    if contar_tokens(texto, modelo) <= 3000:
        partes = [texto]
    else:
        partes = dividir_em_chunks(texto, max_tokens=3000, modelo=modelo)

    resumos_parciais = []
    for parte in partes:
        prompt_resumo_parcial = f"""
Você é um assistente técnico especializado em análise detalhada de documentos. Faça um resumo completo e detalhado do conteúdo abaixo, destacando todas as informações relevantes, sem omitir pontos importantes. Estruture o texto em tópicos claros.

Texto:
\"\"\"\n{parte}\n\"\"\"
"""
        resposta = client.chat.completions.create(
            model=modelo,
            messages=[{"role": "user", "content": prompt_resumo_parcial}],
            temperature=0.2,
            max_tokens=1000
        )
        resumos_parciais.append(resposta.choices[0].message.content.strip())

    if len(resumos_parciais) == 1:
        prompt_final = f"""
{prompt_base}

Conteúdo resumido:
\"\"\"\n{resumos_parciais[0]}\n\"\"\"

Gere um resumo final detalhado e estruturado, seguindo o modelo acima, com ao menos 20 linhas.
"""
    else:
        prompt_final = f"""
Você é um assistente técnico. Com base nos resumos parciais abaixo, gere um **resumo final detalhado e padronizado**, estruturado, sem repetições, seguindo este modelo:

{prompt_base}

Resumos parciais:
\"\"\"\n{chr(10).join(resumos_parciais)}\n\"\"\"

Gere um resumo final detalhado e estruturado, com ao menos 20 linhas.
"""

    resposta_final = client.chat.completions.create(
        model=modelo,
        messages=[{"role": "user", "content": prompt_final}],
        temperature=0.1,
        max_tokens=1500
    )

    return resposta_final.choices[0].message.content.strip()
