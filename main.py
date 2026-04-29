import os
import stat
import shutil
import downloader
import scanner
import config


def _robust_rmtree(path: str) -> None:
    """
    Remove uma árvore de diretórios de forma robusta em qualquer SO.

    No Windows, arquivos dentro de pastas .git são marcados como read-only,
    o que faz shutil.rmtree() falhar com PermissionError.
    O onerror handler abaixo remove o flag read-only e tenta deletar novamente.
    """
    def _fix_readonly(func, fpath, excinfo):
        # Remove o atributo read-only e tenta a operação novamente
        os.chmod(fpath, stat.S_IWRITE)
        func(fpath)

    shutil.rmtree(path, onerror=_fix_readonly)


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
