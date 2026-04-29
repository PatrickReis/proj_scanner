import os
import re

from dotenv import load_dotenv

load_dotenv()

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
# Expressão regular aplicada ao nome do repo antes do clone.
# Deixe vazio para processar todos os repositórios.
# Exemplos:
#   REPO_FILTER=.*chargeback   → apenas repos cujo nome contenha 'chargeback'
#   REPO_FILTER=^api-          → apenas repos cujo nome comece com 'api-'
REPO_FILTER = os.getenv("REPO_FILTER", "")

# ── Paths ──────────────────────────────────────────────────────────────────────
# Pasta onde os repositórios serão baixados localmente
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "./downloads")

# Pasta de saída dos relatórios
OUT_DIR = os.getenv("OUT_DIR", "./out")

# Nome do arquivo de saída da varredura
OUTPUT_FILE = os.getenv("OUTPUT_FILE", os.path.join(OUT_DIR, "resultado_varredura.csv"))

# Nome do arquivo DLQ para repos sem a branch alvo
DLQ_FILE = os.getenv("DLQ_FILE", os.path.join(OUT_DIR, "dlq_release.csv"))
