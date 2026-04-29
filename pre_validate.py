"""
pre_validate.py — Filtragem de repositórios antes do clone.

Uso standalone:
    from pre_validate import filter_repos_by_name

    repos_filtrados = filter_repos_by_name(repos, r".*chargeback")

Integração automática via .env:
    REPO_FILTER=.*chargeback
"""

import re


def filter_repos_by_name(repos: list[dict], pattern: str) -> list[dict]:
    """
    Filtra uma lista de repositórios GitHub pelo nome usando uma expressão regular.

    Args:
        repos:   Lista de dicts retornada pela API do GitHub
                 (cada dict contém ao menos a chave "name").
        pattern: Expressão regular aplicada ao campo "name" do repositório.
                 Exemplos:
                   ".*chargeback"   → repos cujo nome termina com 'chargeback'
                   "^api-"          → repos cujo nome começa com 'api-'
                   "payment|billing"→ repos com 'payment' ou 'billing' no nome

    Returns:
        Lista filtrada de repositórios cujo nome dá match com o padrão.
        Retorna a lista original intacta se o padrão for vazio ou None.
    """
    if not pattern:
        return repos

    try:
        compiled = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        print(f"[ERROR] pre_validate: padrão de regex inválido '{pattern}': {e}")
        return repos

    matched = [r for r in repos if compiled.search(r.get("name", ""))]

    print(f"[INFO] pre_validate: filtro '{pattern}' aplicado → "
          f"{len(matched)}/{len(repos)} repositório(s) selecionado(s).")

    if matched:
        for r in matched:
            print(f"  ✔  {r['name']}")

    return matched
