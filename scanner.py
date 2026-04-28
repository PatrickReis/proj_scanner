import os
import re
import csv
import config

def scan_files(base_path):
    """Varre os arquivos em busca dos padrões definidos."""
    results = []
    patterns = [re.compile(p, re.IGNORECASE) for p in config.SEARCH_PATTERNS]

    if not os.path.exists(base_path):
        print(f"[ERROR] Caminho {base_path} não encontrado.")
        return []

    print(f"[INFO] Iniciando varredura em: {base_path}")

    for root, dirs, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Identifica o nome do repo baseado na pasta raiz de downloads
            parts = os.path.relpath(file_path, base_path).split(os.sep)
            repo_name = parts[0] if parts else "unknown"
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern in patterns:
                            if pattern.search(line):
                                results.append({
                                    'repositorio': repo_name,
                                    'arquivo': file,
                                    'linha': line_num,
                                    'padrao_encontrado': pattern.pattern,
                                    'conteudo_linha': line.strip()
                                })
            except Exception as e:
                print(f"[ERROR] Erro ao ler arquivo {file_path}: {e}")

    return results

def save_to_csv(data, output_path):
    """Salva os resultados em CSV delimitado por Pipe."""
    if not data:
        print("[INFO] Nenhum padrão encontrado. Arquivo de saída não gerado.")
        return

    keys = ['repositorio', 'arquivo', 'linha', 'padrao_encontrado', 'conteudo_linha']
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys, delimiter='|')
            writer.writeheader()
            writer.writerows(data)
        print(f"[SUCCESS] Resultados salvos em: {output_path}")
    except Exception as e:
        print(f"[ERROR] Falha ao salvar CSV: {e}")
