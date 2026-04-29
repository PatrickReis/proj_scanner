import os
import re
import csv
import config


# ── Registro de repos já varridos ──────────────────────────────────────────────

def load_scanned_repos() -> set[str]:
    """
    Lê o SCANNED_REPOS_FILE e retorna um set com os nomes dos repos já varridos.
    Retorna set vazio se o arquivo não existir.
    """
    if not os.path.exists(config.SCANNED_REPOS_FILE):
        return set()

    scanned = set()
    try:
        with open(config.SCANNED_REPOS_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="|")
            for row in reader:
                name = row.get("nome", "").strip()
                if name:
                    scanned.add(name)
        print(f"[INFO] Repos já varridos: {len(scanned)} (carregado de {config.SCANNED_REPOS_FILE})")
    except Exception as e:
        print(f"[WARN] Não foi possível ler o registro de repos varridos: {e}")

    return scanned


def mark_repo_as_scanned(repo_name: str, clone_url: str = "") -> None:
    """
    Adiciona um repo ao SCANNED_REPOS_FILE (append).
    Cria o arquivo com cabeçalho se ainda não existir.
    """
    file_exists = os.path.exists(config.SCANNED_REPOS_FILE)
    try:
        os.makedirs(os.path.dirname(config.SCANNED_REPOS_FILE), exist_ok=True)
        with open(config.SCANNED_REPOS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["nome", "clone_url"], delimiter="|")
            if not file_exists:
                writer.writeheader()
            writer.writerow({"nome": repo_name, "clone_url": clone_url})
    except Exception as e:
        print(f"[WARN] Não foi possível registrar '{repo_name}' como varrido: {e}")


# ── Varredura de arquivos ───────────────────────────────────────────────────────

def scan_files(base_path: str, already_scanned: set[str] | None = None) -> list[dict]:
    """
    Varre os arquivos em busca dos padrões definidos.

    Args:
        base_path:       Pasta raiz dos repos clonados (DOWNLOAD_DIR).
        already_scanned: Set de nomes de repos a pular (já varridos antes).
                         Se None, carrega automaticamente do SCANNED_REPOS_FILE.

    Returns:
        Lista de dicts com as ocorrências encontradas nos repos novos.
    """
    if already_scanned is None:
        already_scanned = load_scanned_repos()

    results = []
    patterns = [re.compile(p, re.IGNORECASE) for p in config.SEARCH_PATTERNS]

    if not os.path.exists(base_path):
        print(f"[ERROR] Caminho {base_path} não encontrado.")
        return []

    # Descobre quais repos existem localmente
    try:
        repo_dirs = [
            d for d in os.listdir(base_path)
            if os.path.isdir(os.path.join(base_path, d))
        ]
    except Exception as e:
        print(f"[ERROR] Não foi possível listar '{base_path}': {e}")
        return []

    to_scan = [r for r in repo_dirs if r not in already_scanned]
    skipped  = [r for r in repo_dirs if r in already_scanned]

    if skipped:
        print(f"[INFO] Pulando {len(skipped)} repo(s) já varrido(s): {', '.join(skipped)}")
    if not to_scan:
        print("[INFO] Todos os repos já foram varridos anteriormente. Nada a fazer.")
        return []

    print(f"[INFO] Iniciando varredura em: {base_path}  ({len(to_scan)} repo(s) a varrer)")

    for repo_name in to_scan:
        repo_path = os.path.join(base_path, repo_name)
        repo_hits = 0

        for root, dirs, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            for pattern in patterns:
                                if pattern.search(line):
                                    results.append({
                                        "repositorio": repo_name,
                                        "arquivo": file,
                                        "linha": line_num,
                                        "padrao_encontrado": pattern.pattern,
                                        "conteudo_linha": line.strip(),
                                    })
                                    repo_hits += 1
                except Exception as e:
                    print(f"[ERROR] Erro ao ler arquivo {file_path}: {e}")

        print(f"[INFO]   '{repo_name}' → {repo_hits} ocorrência(s) encontrada(s).")

        # Registra o repo como varrido (mesmo que não tenha hits)
        # clone_url não está disponível aqui; downloader já o salvou no cache
        mark_repo_as_scanned(repo_name)

    return results


# ── Persistência de resultados ──────────────────────────────────────────────────

def save_to_csv(data: list[dict], output_path: str) -> None:
    """
    Salva os resultados em CSV delimitado por Pipe.
    Se o arquivo já existir (de runs anteriores), faz APPEND.
    """
    if not data:
        print("[INFO] Nenhum padrão novo encontrado.")
        return

    keys = ["repositorio", "arquivo", "linha", "padrao_encontrado", "conteudo_linha"]
    file_exists = os.path.exists(output_path)

    try:
        with open(output_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys, delimiter="|")
            if not file_exists:
                writer.writeheader()
            writer.writerows(data)
        print(f"[SUCCESS] {len(data)} ocorrência(s) {'acrescentada(s) a' if file_exists else 'salva(s) em'}: {output_path}")
    except Exception as e:
        print(f"[ERROR] Falha ao salvar CSV: {e}")
