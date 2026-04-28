import re

# ── Modo de operação ───────────────────────────────────────────────────────────
# "org"  → lista todos os repos de uma organização (requer GITHUB_ORG)
# "user" → lista todos os repos do seu workspace pessoal (requer GITHUB_USER)
SOURCE_TYPE = "org"   # <- altere para "user" quando quiser seu workspace pessoal

# ── GitHub Config ──────────────────────────────────────────────────────────────
# Token de acesso pessoal (PAT)
# Permissões necessárias:
#   modo "org"  → repo + read:org
#   modo "user" → repo
GITHUB_TOKEN = "SEU_TOKEN_AQUI"

# Nome da organização (usado somente quando SOURCE_TYPE = "org")
GITHUB_ORG = "SUA_ORGANIZATION_AQUI"

# Usuário GitHub (usado somente quando SOURCE_TYPE = "user")
# Deixe vazio ("") para usar o próprio dono do token
GITHUB_USER = ""

# Branch alvo para o clone
TARGET_BRANCH = "release"

# ── Padrões de Busca ───────────────────────────────────────────────────────────
# Lista de expressões regulares para busca
# Adicione novos padrões aqui seguindo o padrão Regex
SEARCH_PATTERNS = [
    r'cnpj',
    r'documento',
    r'cgc_.*',
    r'cpf',
    r'password',
    r'senha'
]

# ── Paths ──────────────────────────────────────────────────────────────────────
# Pasta onde os repositórios serão baixados localmente
DOWNLOAD_DIR = "./downloads"

# Nome do arquivo de saída da varredura
OUTPUT_FILE = "resultado_varredura.csv"

# Nome do arquivo DLQ para repos sem a branch alvo
DLQ_FILE = "dlq_release.csv"
