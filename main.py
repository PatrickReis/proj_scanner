import shutil
import downloader
import scanner
import config
import os

def main():
    print("=== INICIANDO PROCESSO DE VARREDURA DE REPOSITÓRIOS ===")

    # 0. Limpeza: remove downloads anteriores e garante pasta de saída
    if os.path.exists(config.DOWNLOAD_DIR):
        print(f"\n[INFO] Limpando pasta de downloads: {config.DOWNLOAD_DIR}")
        shutil.rmtree(config.DOWNLOAD_DIR)

    os.makedirs(config.DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(config.OUT_DIR, exist_ok=True)
    print(f"[INFO] Pasta de saída: {config.OUT_DIR}")

    # 1. Executa o Job de Download
    print("\n--- Passo 1: Download de Repositórios ---")
    downloaded_path = downloader.download_repositories()

    # 2. Executa a Varredura
    print("\n--- Passo 2: Analisando Arquivos ---")
    findings = scanner.scan_files(downloaded_path)

    # 3. Gera o Relatório
    print("\n--- Passo 3: Gerando Relatório ---")
    scanner.save_to_csv(findings, config.OUTPUT_FILE)

    print("\n=== PROCESSO FINALIZADO ===")
    print(f"Total de ocorrências encontradas: {len(findings)}")

if __name__ == "__main__":
    main()
