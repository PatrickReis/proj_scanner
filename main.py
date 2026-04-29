import os
import shutil
import downloader
import scanner
import config
from downloader import _robust_rmtree


def main():
    print("=== INICIANDO PROCESSO DE VARREDURA DE REPOSITÓRIOS ===")

    # 0. Limpeza condicional: controlada pela flag CLEAN_RUN
    if config.CLEAN_RUN:
        if os.path.exists(config.DOWNLOAD_DIR):
            print(f"\n[INFO] CLEAN_RUN=true → Limpando pasta: {config.DOWNLOAD_DIR}")
            _robust_rmtree(config.DOWNLOAD_DIR)
        else:
            print(f"\n[INFO] CLEAN_RUN=true → Pasta '{config.DOWNLOAD_DIR}' não existe, nada a limpar.")
    else:
        print(f"\n[INFO] CLEAN_RUN=false → Reutilizando downloads existentes em '{config.DOWNLOAD_DIR}'.")

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
