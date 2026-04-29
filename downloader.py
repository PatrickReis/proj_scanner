import os
import csv
import requests
from git import Repo, GitCommandError
import config
from pre_validate import filter_repos_by_name


# ── Cabeçalhos padrão para todas as chamadas à API ──────────────────────────────
def _headers():
    return {
        "Authorization": f"token {config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }


# ── Cache de listagem da API ────────────────────────────────────────────────────

def _save_repos_cache(repos: list[dict]) -> None:
    """Persiste a lista de repos (nome|clone_url) no arquivo de cache."""
    try:
        os.makedirs(os.path.dirname(config.REPOS_CACHE_FILE), exist_ok=True)
        with open(config.REPOS_CACHE_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["nome", "clone_url"], delimiter="|")
            writer.writeheader()
            for r in repos:
                writer.writerow({"nome": r["name"], "clone_url": r["clone_url"]})
        print(f"[INFO] Cache de repos salvo em: {config.REPOS_CACHE_FILE} ({len(repos)} repos)")
    except Exception as e:
        print(f"[WARN] Não foi possível salvar o cache de repos: {e}")


def _load_repos_cache() -> list[dict] | None:
    """
    Lê o cache local de repos.
    Retorna lista de dicts com chaves 'name' e 'clone_url', ou None se não existir.
    """
    if not os.path.exists(config.REPOS_CACHE_FILE):
        return None

    repos = []
    try:
        with open(config.REPOS_CACHE_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="|")
            for row in reader:
                # Normaliza para o mesmo formato retornado pela API
                repos.append({"name": row["nome"], "clone_url": row["clone_url"]})
        print(f"[INFO] Cache de repos carregado: {config.REPOS_CACHE_FILE} ({len(repos)} repos) — pulando chamada à API.")
        return repos
    except Exception as e:
        print(f"[WARN] Falha ao ler cache de repos, consultando API: {e}")
        return None


# ── Funções de listagem de repositórios ─────────────────────────────────────────

def _paginate(url, params=None):
    """Itera sobre todas as páginas de uma URL da API do GitHub."""
    headers = _headers()
    page = 1
    items = []

    while True:
        paged_params = {"per_page": 100, "page": page, **(params or {})}
        response = requests.get(url, headers=headers, params=paged_params, timeout=30, verify=False)

        if response.status_code == 401:
            raise PermissionError(
                "[ERROR] Token inválido ou sem permissão. "
                "Verifique GITHUB_TOKEN em config.py."
            )
        if response.status_code == 404:
            raise ValueError(
                f"[ERROR] Recurso não encontrado: {url}\n"
                "Verifique GITHUB_ORG / GITHUB_USER em config.py."
            )
        response.raise_for_status()

        page_data = response.json()
        if not page_data:
            break

        items.extend(page_data)
        print(f"[INFO]   Página {page}: {len(page_data)} repositório(s).")
        page += 1

    return items


def _list_org_repos():
    """Lista todos os repos de uma organização (SOURCE_TYPE = 'org')."""
    org = config.GITHUB_ORG
    print(f"[INFO] Modo: ORGANIZAÇÃO  →  '{org}'")
    url = f"https://api.github.com/orgs/{org}/repos"
    return _paginate(url, params={"type": "all"})


def _list_user_repos():
    """
    Lista todos os repos do usuário (SOURCE_TYPE = 'user').
    - Se GITHUB_USER estiver vazio → usa /user/repos (repos do dono do token,
      inclui privados).
    - Se GITHUB_USER estiver preenchido → usa /users/{user}/repos (repos públicos
      de outro usuário).
    """
    user = config.GITHUB_USER.strip()

    if not user:
        # Workspace próprio (token owner) – inclui repos privados
        print("[INFO] Modo: WORKSPACE PESSOAL  →  (dono do token)")
        url = "https://api.github.com/user/repos"
        return _paginate(url, params={"type": "owner"})
    else:
        # Workspace de outro usuário (apenas repos públicos)
        print(f"[INFO] Modo: WORKSPACE PESSOAL  →  '{user}'")
        url = f"https://api.github.com/users/{user}/repos"
        return _paginate(url)


def _fetch_repos_from_api() -> list[dict]:
    """Consulta a API do GitHub e salva o resultado em cache."""
    source = config.SOURCE_TYPE.strip().lower()

    if source == "org":
        repos = _list_org_repos()
    elif source == "user":
        repos = _list_user_repos()
    else:
        raise ValueError(
            f"[ERROR] SOURCE_TYPE inválido: '{config.SOURCE_TYPE}'. "
            "Use 'org' ou 'user'."
        )

    print(f"[INFO] Total de repositórios encontrados via API: {len(repos)}")
    _save_repos_cache(repos)
    return repos


def _get_all_repositories() -> list[dict]:
    """
    Despacha para API ou cache conforme CLEAN_RUN.

    - CLEAN_RUN=true  → sempre consulta a API (cache é regenerado).
    - CLEAN_RUN=false → usa o cache local se existir; só vai à API se não houver cache.
    """
    if not config.CLEAN_RUN:
        cached = _load_repos_cache()
        if cached is not None:
            return cached

    # CLEAN_RUN=true OU cache inexistente → consulta a API
    return _fetch_repos_from_api()


# ── DLQ ────────────────────────────────────────────────────────────────────────

def _write_dlq(dlq_entries):
    """Grava os repositórios sem a branch alvo no arquivo DLQ (CSV com |)."""
    if not dlq_entries:
        return

    keys = ["repositorio", "clone_url", "motivo"]
    try:
        with open(config.DLQ_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys, delimiter="|")
            writer.writeheader()
            writer.writerows(dlq_entries)
        print(
            f"[INFO] {len(dlq_entries)} repositório(s) sem branch "
            f"'{config.TARGET_BRANCH}' registrados em: {config.DLQ_FILE}"
        )
    except Exception as e:
        print(f"[ERROR] Falha ao gravar DLQ: {e}")


# ── Entrada principal ────────────────────────────────────────────────────────────

def download_repositories():
    """
    1. Obtém lista de repos (API ou cache, conforme CLEAN_RUN).
    2. Aplica REPO_FILTER por nome.
    3. Tenta clonar a branch TARGET_BRANCH de cada repo não existente localmente.
    4. Repos sem a branch são gravados em dlq_release.csv.
    """
    repos = _get_all_repositories()

    # Aplica filtro por nome (se REPO_FILTER estiver definido no .env)
    if config.REPO_FILTER:
        repos = filter_repos_by_name(repos, config.REPO_FILTER)

    dlq_entries = []

    for repo_info in repos:
        repo_name = repo_info["name"]
        clone_url = repo_info["clone_url"]
        target_path = os.path.join(config.DOWNLOAD_DIR, repo_name)

        if os.path.exists(target_path):
            print(f"[INFO] '{repo_name}' já existe localmente. Pulando clone...")
            continue

        print(f"[INFO] Clonando '{repo_name}' (branch: {config.TARGET_BRANCH})...")

        # Injeta token na URL para autenticar repos privados
        auth_url = clone_url.replace("https://", f"https://{config.GITHUB_TOKEN}@")

        try:
            Repo.clone_from(
                auth_url,
                target_path,
                branch=config.TARGET_BRANCH,
            )
            print(f"[SUCCESS] '{repo_name}' clonado com sucesso.")

        except GitCommandError as e:
            error_msg = str(e)
            if "Remote branch" in error_msg or "not found" in error_msg.lower():
                motivo = f"Branch '{config.TARGET_BRANCH}' não encontrada"
            else:
                motivo = f"GitCommandError: {error_msg[:200]}"

            print(f"[WARN] '{repo_name}': {motivo}")
            dlq_entries.append({
                "repositorio": repo_name,
                "clone_url": clone_url,
                "motivo": motivo,
            })

            # Remove pasta vazia deixada pelo git antes de falhar
            if os.path.exists(target_path) and not os.listdir(target_path):
                os.rmdir(target_path)

        except Exception as e:
            motivo = f"Erro inesperado: {str(e)[:200]}"
            print(f"[ERROR] '{repo_name}': {motivo}")
            dlq_entries.append({
                "repositorio": repo_name,
                "clone_url": clone_url,
                "motivo": motivo,
            })

    _write_dlq(dlq_entries)
    return config.DOWNLOAD_DIR
