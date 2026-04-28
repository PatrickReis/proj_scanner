# 🔍 Repo Scanner

Ferramenta de segurança e auditoria que varre automaticamente repositórios GitHub em busca de padrões sensíveis de texto — como CPF, CNPJ, senhas e outros dados — e gera um relatório em CSV.

---

## 📋 Sumário

- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configurando o Token do GitHub](#configurando-o-token-do-github)
- [Modos de Operação](#modos-de-operação)
  - [Modo Organização](#modo-organização-org)
  - [Modo Workspace Pessoal](#modo-workspace-pessoal-user)
- [Executando o Projeto](#executando-o-projeto)
- [Saídas Geradas](#saídas-geradas)
- [Adicionando Novos Padrões de Busca](#adicionando-novos-padrões-de-busca)

---

## Arquitetura

```
projeto_scanner/
├── main.py            # Orquestrador: Download → Scan → Relatório
├── config.py          # ⚙️  Ponto central de configuração
├── downloader.py      # Integração com a API do GitHub + git clone
├── scanner.py         # Varredura por Regex + geração de CSV
├── requirements.txt   # Dependências Python
├── downloads/         # Pasta criada automaticamente com os repos clonados
├── resultado_varredura.csv   # Relatório de ocorrências (gerado ao rodar)
└── dlq_release.csv           # Repos sem a branch release (gerado ao rodar)
```

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Orquestra o fluxo completo |
| `config.py` | **Único arquivo que você precisa editar** para configurar o projeto |
| `downloader.py` | Lista repos via API do GitHub e realiza o `git clone` da branch `release` |
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
git clone https://github.com/seu-usuario/projeto_scanner.git
cd projeto_scanner

# Crie e ative o ambiente virtual (recomendado)
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

---

## Configurando o Token do GitHub

O projeto usa a **API REST do GitHub** para listar repositórios, portanto é necessário um **Personal Access Token (PAT)**.

### Passo a passo para criar o token

1. Acesse **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**  
   Link direto: [https://github.com/settings/tokens](https://github.com/settings/tokens)

2. Clique em **"Generate new token (classic)"**

3. Dê um nome descritivo, ex: `repo-scanner`

4. Selecione a validade (recomendado: 30 ou 90 dias)

5. Marque os escopos conforme o modo de uso:

   | Modo | Escopos necessários |
   |---|---|
   | `org` (organização) | ✅ `repo` &nbsp;+&nbsp; ✅ `read:org` |
   | `user` (workspace pessoal) | ✅ `repo` |

6. Clique em **"Generate token"** e **copie o valor imediatamente** (ele não será exibido novamente)

7. Cole o token em `config.py`:
   ```python
   GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```

> **⚠️ Segurança:** Nunca commite o token no repositório. Considere usar variável de ambiente:
> ```python
> import os
> GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
> ```

---

## Modos de Operação

A chave `SOURCE_TYPE` em `config.py` controla qual fonte de repositórios será usada.

### Modo Organização (`org`)

Usa a API `GET /orgs/{org}/repos` — lista **todos os repositórios** (públicos e privados) de uma organização GitHub.

**Configuração em `config.py`:**
```python
SOURCE_TYPE  = "org"

GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"   # token com repo + read:org
GITHUB_ORG   = "nome-da-sua-organizacao"            # ex: "minha-empresa"

TARGET_BRANCH = "release"
```

**Resultado esperado no terminal:**
```
[INFO] Modo: ORGANIZAÇÃO  →  'minha-empresa'
[INFO]   Página 1: 100 repositório(s).
[INFO]   Página 2: 42 repositório(s).
[INFO] Total de repositórios encontrados: 142
[INFO] Clonando 'api-pagamentos' (branch: release)...
[SUCCESS] 'api-pagamentos' clonado com sucesso.
[WARN] 'legacy-monolito': Branch 'release' não encontrada
...
```

---

### Modo Workspace Pessoal (`user`)

#### Opção A — Seus próprios repositórios (públicos + privados)

Usa a API `GET /user/repos?affiliation=owner` — lista **todos os seus repos**, incluindo privados.

```python
SOURCE_TYPE  = "user"

GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"   # token com repo
GITHUB_USER  = ""    # ← deixe vazio para usar o dono do token

TARGET_BRANCH = "release"
```

**Resultado esperado no terminal:**
```
[INFO] Modo: WORKSPACE PESSOAL  →  (dono do token)
[INFO]   Página 1: 78 repositório(s).
[INFO] Total de repositórios encontrados: 78
...
```

#### Opção B — Repositórios públicos de outro usuário

Usa a API `GET /users/{user}/repos` — lista apenas os repos **públicos** do usuário informado.

```python
SOURCE_TYPE  = "user"

GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
GITHUB_USER  = "nome-do-outro-usuario"   # ← username do GitHub

TARGET_BRANCH = "release"
```

---

## Executando o Projeto

Após configurar o `config.py`:

```bash
python main.py
```

O processo ocorre em três etapas automáticas:

```
=== INICIANDO PROCESSO DE VARREDURA DE REPOSITÓRIOS ===

--- Passo 1: Download de Repositórios ---
[INFO] Modo: ORGANIZAÇÃO  →  'minha-empresa'
...

--- Passo 2: Analisando Arquivos ---
[INFO] Iniciando varredura em: ./downloads
...

--- Passo 3: Gerando Relatório ---
[SUCCESS] Resultados salvos em: resultado_varredura.csv

=== PROCESSO FINALIZADO ===
Total de ocorrências encontradas: 37
```

---

## Saídas Geradas

### `resultado_varredura.csv`
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

### `dlq_release.csv`
Gerado automaticamente com os repositórios que **não possuem a branch `release`**.

| Coluna | Descrição |
|---|---|
| `repositorio` | Nome do repositório |
| `clone_url` | URL de clone do repositório |
| `motivo` | Motivo da falha (branch não encontrada ou erro) |

Exemplo:
```
repositorio|clone_url|motivo
legacy-monolito|https://github.com/org/legacy-monolito.git|Branch 'release' não encontrada
front-deprecated|https://github.com/org/front-deprecated.git|Branch 'release' não encontrada
```

---

## Adicionando Novos Padrões de Busca

Edite a lista `SEARCH_PATTERNS` em `config.py`:

```python
SEARCH_PATTERNS = [
    r'cnpj',
    r'cpf',
    r'password',
    r'senha',
    # Exemplos de novos padrões:
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # e-mails
    r'(?:api[_-]?key|apikey)\s*=',                         # API keys
    r'secret',                                             # secrets genéricos
]
```

> Todos os padrões são tratados como expressões regulares com flag `IGNORECASE`.

---

## Dependências

| Pacote | Uso |
|---|---|
| `GitPython` | Operações de `git clone` |
| `requests` | Chamadas à API REST do GitHub |
