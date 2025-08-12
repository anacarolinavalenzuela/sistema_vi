from bs4 import BeautifulSoup  

def force_all_to_ol(html: str) -> str:
    """
    Converte qualquer <p> + <ul> para <ol> numerado
    e mantém o estilo idêntico ao já usado para <ol>.
    """
    soup = BeautifulSoup(html, "html.parser")

    for p in list(soup.find_all("p")):
        nxt = p.find_next_sibling("ul")
        if nxt and not p.find_parent("li"):
            # Troca ul por ol
            nxt.name = "ol"

            # Cria nova lista principal
            new_ol = soup.new_tag("ol")
            new_li = soup.new_tag("li")

            # Insere a nova estrutura
            p.insert_before(new_ol)
            new_ol.append(new_li)
            new_li.append(p.extract())
            new_li.append(nxt.extract())

    return str(soup)


