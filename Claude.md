# Documentação de Continuidade: Projeto Repo Scanner

## Contexto do Projeto
Este projeto é uma ferramenta de segurança/auditoria destinada a escanear repositórios Git em busca de padrões de texto sensíveis ou variáveis específicas (como CNPJ, CPF, senhas, etc.).

## Arquitetura
O projeto segue uma estrutura modular:
- `main.py`: Orquestrador do fluxo (Download -> Scan -> Report).
- `config.py`: **Ponto central de manutenção**. Contém as URLs, as Regex e os caminhos de saída.
- `downloader.py`: Responsável pela interação com o Git (clone dos repos).
- `scanner.py`: Lógica de busca via Regex e escrita de arquivos CSV.

## Como expandir o projeto (Instruções para Agentes/Devs)

### 1. Adicionar novos padrões de busca
Não altere o motor de busca. Vá até `config.py` e adicione a nova expressão regular à lista `SEARCH_PATTER	ERNTS`. 
*Exemplo:* Para buscar emails, adicione `r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'`.

### 2. Adicionar novos repositórios
Adicione a URL completa do repositório na lista `REPOSITORIES` dentro de `config.py`.

### 3. Adicionar novos formatos de saída
Se precisar de JSON ou HTML, modifique a função `save_to_csv` em `scanner.py` ou crie um novo módulo de reporting.

### 4. Melhorias Sugeridas (Backlog)
- [ ] **Multithreading**: Implementar `concurrent.futures` no `downloader.py` para clonar vários repos simultaneamente.
- [ ] **Suporte a GitLab/Bitbucket**: Criar um módulo de download específico para APIs desses serviços.
- [ ] **Filtro de extensões**: Adicionar em `config.py` uma lista de extensões para ignorar (ex: `.png`, `.jpg`, `.exe`) para aumentar a performance.
- [ ] **Integração de Alerta**: Enviar o CSV resultante para um webhook do Slack ou Microsoft Teams.

## Dependências
- `GitPython`: Necessário para operações de clone.
