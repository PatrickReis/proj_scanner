# 🔍 Repo Scanner

Ferramenta de segurança e auditoria que varre automaticamente repositórios GitHub em busca de padrões sensíveis de texto — como CPF, CNPJ e outros dados — e gera relatórios em CSV.

---

## 📋 Sumário

- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração via .env](#configuração-via-env)
- [Modos de Operação](#modos-de-operação)
  - [Modo Organização](#modo-organização-org)
  - [Modo Workspace Pessoal](#modo-workspace-pessoal-user)
- [Executando o Projeto](#executando-o-projeto)
- [Saídas Geradas](#saídas-geradas)
- [Adicionando Novos Padrões de Busca](#adicionando-novos-padrões-de-busca)
- [Dependências](#dependências)

---

## Arquitetura

```
proj_scanner/
├── main.py            # Orquestrador: Limpeza → Download → Scan → Relatório
├── config.py          # ⚙️  Ponto central de configuração (lê do .env)
├── downloader.py      # Integração com a API do GitHub + git clone autenticado
├── scanner.py         # Varredura por Regex + geração de CSV
├── requirements.txt   # Dependências Python
├── .env               # Variáveis de configuração (NÃO commitar)
├── .env.example       # Modelo de referência para o .env
├── downloads/         # Criada e limpa automaticamente a cada execução
└── out/               # Relatórios gerados (ignorada pelo git)
    ├── resultado_varredura.csv
    └── dlq_release.csv
```

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Orquestra o fluxo completo, limpa downloads e cria `out/` |
| `config.py` | Lê todas as configurações do `.env` via `python-dotenv` |
| `downloader.py` | Lista repos via API do GitHub e realiza `git clone` autenticado |
| `scanner.py` | Varre os arquivos clonados por padrões Regex e salva em CSV |

---

## Pré-requisitos

- Python **3.8+**
- Git instalado e acessível no `PATH`
- Uma conta no GitHub com acesso aos repositórios desejados

---

## Instalação

```bash
# Clone este projeto
git clone https://github.com/seu-usuario/proj_scanner.git
cd proj_scanner

# Crie e ative o ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

---

## Configuração via .env

Todas as configurações são feitas através de um arquivo `.env` na raiz do projeto. **Nunca commite este arquivo** — ele já está no `.gitignore`.

Crie o arquivo `.env` com base no modelo abaixo:

```env
# ── Modo de operação ──────────────────────────────────────────────────────────
# "org"  → lista todos os repos de uma organização
# "user" → lista todos os repos do workspace pessoal
SOURCE_TYPE=org

# ── GitHub Config ─────────────────────────────────────────────────────────────
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_ORG=nome-da-sua-organizacao   # obrigatório se SOURCE_TYPE=org
GITHUB_USER=                         # deixe vazio para usar o dono do token

# ── Branch alvo para o clone ──────────────────────────────────────────────────
TARGET_BRANCH=release

# ── Paths (opcionais — os valores abaixo são os padrões) ─────────────────────
DOWNLOAD_DIR=./downloads
OUT_DIR=./out
OUTPUT_FILE=./out/resultado_varredura.csv
DLQ_FILE=./out/dlq_release.csv
```

### Criando o Token do GitHub (PAT)

1. Acesse **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**  
   Link: [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. Clique em **"Generate new token (classic)"**
3. Selecione os escopos conforme o modo:

   | Modo | Escopos necessários |
   |---|---|
   | `org` (organização) | ✅ `repo` + ✅ `read:org` |
   | `user` (workspace pessoal) | ✅ `repo` |

4. Copie o token gerado e cole em `GITHUB_TOKEN` no `.env`

> **⚠️ Segurança:** O token concede acesso aos seus repositórios privados. Nunca o commite ou compartilhe.

---

## Modos de Operação

A chave `SOURCE_TYPE` no `.env` controla qual fonte de repositórios será usada.

### Modo Organização (`org`)

Usa `GET /orgs/{org}/repos` — lista **todos os repositórios** (públicos e privados) de uma organização.

```env
SOURCE_TYPE=org
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_ORG=minha-empresa
TARGET_BRANCH=release
```

**Saída esperada:**
```
[INFO] Modo: ORGANIZAÇÃO  →  'minha-empresa'
[INFO]   Página 1: 100 repositório(s).
[INFO] Total de repositórios encontrados: 142
[INFO] Clonando 'api-pagamentos' (branch: release)...
[SUCCESS] 'api-pagamentos' clonado com sucesso.
[WARN] 'legacy-monolito': Branch 'release' não encontrada
```

---

### Modo Workspace Pessoal (`user`)

#### Opção A — Seus próprios repositórios (públicos + privados)

Usa `GET /user/repos?type=owner` — lista **todos os seus repos**, incluindo privados.

```env
SOURCE_TYPE=user
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_USER=          # ← deixe vazio para usar o dono do token
TARGET_BRANCH=main
```

**Saída esperada:**
```
[INFO] Modo: WORKSPACE PESSOAL  →  (dono do token)
[INFO]   Página 1: 24 repositório(s).
[INFO] Total de repositórios encontrados: 24
```

#### Opção B — Repositórios públicos de outro usuário

Usa `GET /users/{user}/repos` — lista apenas repos **públicos** do usuário informado.

```env
SOURCE_TYPE=user
GITHUB_USER=nome-do-outro-usuario
TARGET_BRANCH=main
```

---

## Executando o Projeto

Com o `.env` configurado e o venv ativo:

```bash
python main.py
```

O processo ocorre em **4 etapas automáticas**:

```
=== INICIANDO PROCESSO DE VARREDURA DE REPOSITÓRIOS ===

[INFO] Limpando pasta de downloads: ./downloads
[INFO] Pasta de saída: ./out

--- Passo 1: Download de Repositórios ---
[INFO] Modo: WORKSPACE PESSOAL  →  (dono do token)
[INFO]   Página 1: 24 repositório(s).
[INFO] Total de repositórios encontrados: 24
[INFO] Clonando 'meu-repo' (branch: main)...
[SUCCESS] 'meu-repo' clonado com sucesso.

--- Passo 2: Analisando Arquivos ---
[INFO] Iniciando varredura em: ./downloads

--- Passo 3: Gerando Relatório ---
[SUCCESS] Resultados salvos em: ./out/resultado_varredura.csv

=== PROCESSO FINALIZADO ===
Total de ocorrências encontradas: 300
```

> **ℹ️ Nota:** A pasta `downloads/` é **apagada e recriada a cada execução** para garantir dados sempre atualizados.

---

## Saídas Geradas

Todos os relatórios são gravados na pasta `out/` (ignorada pelo git).

### `out/resultado_varredura.csv`
Contém todas as ocorrências dos padrões encontrados nos arquivos dos repositórios.

| Coluna | Descrição |
|---|---|
| `repositorio` | Nome do repositório |
| `arquivo` | Nome do arquivo onde o padrão foi encontrado |
| `linha` | Número da linha |
| `padrao_encontrado` | Expressão regular que gerou o match |
| `conteudo_linha` | Conteúdo da linha (texto completo) |

Exemplo:
```
repositorio|arquivo|linha|padrao_encontrado|conteudo_linha
api-pagamentos|pagamento_service.py|42|cpf|    cpf_cliente = request.get('cpf')
cadastro-api|models.py|17|cnpj|    cnpj = models.CharField(max_length=18)
```

---

### `out/dlq_release.csv`
Repositórios que **não possuem a branch alvo** (`TARGET_BRANCH`).

| Coluna | Descrição |
|---|---|
| `repositorio` | Nome do repositório |
| `clone_url` | URL de clone |
| `motivo` | Motivo da falha |

Exemplo:
```
repositorio|clone_url|motivo
legacy-monolito|https://github.com/org/legacy-monolito.git|Branch 'release' não encontrada
```

---

## Adicionando Novos Padrões de Busca

Edite a lista `SEARCH_PATTERNS` em `config.py`:

```python
SEARCH_PATTERNS = [
    r'cnpj',
    r'documento',
    r'cgc_.*',
    r'cpf',
    # Exemplos de novos padrões:
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # e-mails
    r'(?:api[_-]?key|apikey)\s*=',                         # API keys
    r'secret',                                              # secrets genéricos
]
```

> Todos os padrões são tratados como expressões regulares com flag `IGNORECASE`.

---

## Dependências

| Pacote | Uso |
|---|---|
| `GitPython` | Operações de `git clone` autenticado |
| `requests` | Chamadas à API REST do GitHub (com `verify=False` para ambientes corporativos) |
| `python-dotenv` | Carrega variáveis do arquivo `.env` |

Instale tudo com:
```bash
pip install -r requirements.txt
```
