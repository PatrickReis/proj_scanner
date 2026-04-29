"""
pre_validate.py — Filtragem de repositórios antes do clone.

Uso standalone:
    from pre_validate import filter_repos_by_name

    # Um único padrão
    repos_filtrados = filter_repos_by_name(repos, [".*chargeback"])

    # Múltiplos padrões — retorna repos que derem match em QUALQUER um
    repos_filtrados = filter_repos_by_name(repos, ["spo_.*", ".*chargeback"])

Integração automática via .env:
    REPO_FILTER=spo_.* , .*chargeback
"""

import re


def filter_repos_by_name(repos: list[dict], patterns: list[str]) -> list[dict]:
    """
    Filtra repositórios GitHub pelo nome usando uma lista de expressões regulares.

    Um repositório é incluído no resultado se o nome der match com
    QUALQUER um dos padrões fornecidos (lógica OR).

    Args:
        repos:    Lista de dicts retornada pela API do GitHub
                  (cada dict contém ao menos a chave "name").
        patterns: Lista de expressões regulares aplicadas ao campo "name".
                  Exemplos:
                    [".*chargeback"]           → nome contém 'chargeback'
                    ["spo_.*", ".*chargeback"] → começa com 'spo_' OU contém 'chargeback'
                    ["^api-", "^svc-"]         → começa com 'api-' OU 'svc-'

    Returns:
        Lista filtrada. Retorna a lista original se `patterns` for vazia.
    """
    if not patterns:
        return repos

    # Compila todos os padrões, ignorando os inválidos
    compiled = []
    for p in patterns:
        try:
            compiled.append((p, re.compile(p, re.IGNORECASE)))
        except re.error as e:
            print(f"[WARN] pre_validate: padrão inválido ignorado '{p}': {e}")

    if not compiled:
        return repos

    def _matches_any(name: str) -> bool:
        return any(rx.search(name) for _, rx in compiled)

    matched = [r for r in repos if _matches_any(r.get("name", ""))]

    patterns_str = " | ".join(p for p, _ in compiled)
    print(f"[INFO] pre_validate: {len(compiled)} padrão(ões) aplicado(s) [{patterns_str}] → "
          f"{len(matched)}/{len(repos)} repositório(s) selecionado(s).")

    for r in matched:
        # Indica qual padrão gerou o match
        hit = next((p for p, rx in compiled if rx.search(r["name"])), "?")
        print(f"  ✔  {r['name']}  (match: '{hit}')")

    return matched
