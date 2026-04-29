import os
import re

from dotenv import load_dotenv

load_dotenv()

# ── Comportamento da execução ──────────────────────────────────────────────────
# CLEAN_RUN=true  → apaga a pasta DOWNLOAD_DIR antes de começar (padrão)
# CLEAN_RUN=false → reutiliza downloads anteriores (útil para re-rodar a varredura
#                   sem precisar baixar os repos de novo)
_clean_run_raw = os.getenv("CLEAN_RUN", "true")
CLEAN_RUN: bool = _clean_run_raw.strip().lower() in ("true", "1", "yes")

# ── Modo de operação ───────────────────────────────────────────────────────────
# "org"  → lista todos os repos de uma organização (requer GITHUB_ORG)
# "user" → lista todos os repos do seu workspace pessoal (requer GITHUB_USER)
SOURCE_TYPE = os.getenv("SOURCE_TYPE", "org")

# ── GitHub Config ──────────────────────────────────────────────────────────────
# Token de acesso pessoal (PAT)
# Permissões necessárias:
#   modo "org"  → repo + read:org
#   modo "user" → repo
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Nome da organização (usado somente quando SOURCE_TYPE = "org")
GITHUB_ORG = os.getenv("GITHUB_ORG", "")

# Usuário GitHub (usado somente quando SOURCE_TYPE = "user")
# Deixe vazio ("") para usar o próprio dono do token
GITHUB_USER = os.getenv("GITHUB_USER", "")

# Branch alvo para o clone
TARGET_BRANCH = os.getenv("TARGET_BRANCH", "release")

# ── Padrões de Busca ───────────────────────────────────────────────────────────
# Lista de expressões regulares para busca
# Adicione novos padrões aqui seguindo o padrão Regex
SEARCH_PATTERNS = [
    r'cnpj',
    r'documento',
    r'cgc_.*',
    r'cpf',
]

# ── Filtro de Repositórios (opcional) ────────────────────────────────────────
# Lista de expressões regulares separadas por vírgula, aplicadas ao nome do repo.
# Um repo é incluído se der match com QUALQUER um dos padrões.
# Deixe vazio para processar todos os repositórios.
# Exemplos:
#   REPO_FILTER=.*chargeback
#   REPO_FILTER=spo_.* , .*chargeback
#   REPO_FILTER=^api- , ^svc- , .*-core$
_repo_filter_raw = os.getenv("REPO_FILTER", "")
REPO_FILTER: list[str] = [
    p.strip() for p in _repo_filter_raw.split(",") if p.strip()
]

# ── Paths ──────────────────────────────────────────────────────────────────────
# Pasta onde os repositórios serão baixados localmente
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "./downloads")

# Pasta de saída dos relatórios
OUT_DIR = os.getenv("OUT_DIR", "./out")

# Nome do arquivo de saída da varredura
OUTPUT_FILE = os.getenv("OUTPUT_FILE", os.path.join(OUT_DIR, "resultado_varredura.csv"))

# Nome do arquivo DLQ para repos sem a branch alvo
DLQ_FILE = os.getenv("DLQ_FILE", os.path.join(OUT_DIR, "dlq_release.csv"))

# Cache da listagem da API (nome|clone_url) — evita re-consultar o GitHub a cada run
# Ignorado quando CLEAN_RUN=true (força nova consulta)
REPOS_CACHE_FILE = os.getenv("REPOS_CACHE_FILE", os.path.join(OUT_DIR, "repos_cache.csv"))

# Registro incremental dos repos já varridos com sucesso (nome|clone_url)
# Se um repo constar aqui, o scanner o pula na próxima execução
SCANNED_REPOS_FILE = os.getenv("SCANNED_REPOS_FILE", os.path.join(OUT_DIR, "repos_scanneados.csv"))
