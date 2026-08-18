"""
rodar_analises.py
=================
Script orquestrador que roda todos os scripts de análise para os limiares
de 0.95 e 0.75, salvando os resultados nas pastas saida/95/ e saida/75/
respectivamente.

Os scripts que NÃO dependem de limiar (analise_embeddings.py,
gerar_graficos_tipologia.py) são executados apenas uma vez, com saída na
pasta saida/ raiz.

Uso:
    python rodar_analises.py
"""

import subprocess
import sys
from pathlib import Path

DIR_SCRIPTS = Path(__file__).resolve().parent
DIR_BASE = DIR_SCRIPTS.parent
DIR_SAIDA = DIR_BASE / "saida"

PYTHON = sys.executable

# Limiares a processar
LIMIARES = [0.95, 0.75]

# ================================================================
# Scripts que DEPENDEM de limiar (rodam 1x para cada limiar)
# ================================================================
SCRIPTS_COM_LIMIAR = [
    "filtro_dados_matriz.py",
    "analise_matriz_similaridade.py",
    "contar_pontos_sobraram.py",
    "histogramas_tipologia_prod_escalar.py",
]

# ================================================================
# Scripts que NÃO dependem de limiar (rodam 1x, saída na raiz)
# ================================================================
SCRIPTS_SEM_LIMIAR = [
    "analise_embeddings.py",
    "gerar_graficos_tipologia.py",
]


def rodar(script: str, args: list[str] = None):
    """Executa um script Python como subprocesso."""
    cmd = [PYTHON, str(DIR_SCRIPTS / script)]
    if args:
        cmd.extend(args)

    print(f"\n{'=' * 70}")
    print(f"  EXECUTANDO: {script} {' '.join(args or [])}")
    print(f"{'=' * 70}\n")

    result = subprocess.run(cmd, cwd=str(DIR_BASE))
    if result.returncode != 0:
        print(f"\n  [ERRO] {script} retornou código {result.returncode}")
        return False
    return True


def main():
    print("=" * 70)
    print("  ORQUESTRADOR DE ANÁLISES")
    print(f"  Limiares: {LIMIARES}")
    print(f"  Pasta de saída: {DIR_SAIDA}")
    print("=" * 70)

    # Criar pastas de saída
    for limiar in LIMIARES:
        pasta = DIR_SAIDA / str(int(limiar * 100))
        pasta.mkdir(parents=True, exist_ok=True)
        print(f"  [ok] Pasta criada/verificada: {pasta}")

    erros = []

    # --- 1. Scripts COM limiar (rodar para cada limiar) ---
    for limiar in LIMIARES:
        limiar_str = str(limiar)
        limiar_int = int(limiar * 100)
        print(f"\n\n{'#' * 70}")
        print(f"  PROCESSANDO LIMIAR >= {limiar} (pasta: saida/{limiar_int}/)")
        print(f"{'#' * 70}")

        for script in SCRIPTS_COM_LIMIAR:
            ok = rodar(script, ["--limiar", limiar_str])
            if not ok:
                erros.append(f"{script} --limiar {limiar_str}")

    # --- 2. Scripts SEM limiar (rodar 1x) ---
    print(f"\n\n{'#' * 70}")
    print(f"  PROCESSANDO SCRIPTS SEM LIMIAR (pasta: saida/)")
    print(f"{'#' * 70}")

    for script in SCRIPTS_SEM_LIMIAR:
        ok = rodar(script)
        if not ok:
            erros.append(script)

    # --- Resumo ---
    print(f"\n\n{'=' * 70}")
    print("  RESUMO FINAL")
    print(f"{'=' * 70}")

    if erros:
        print(f"\n  [!] {len(erros)} script(s) com erro:")
        for e in erros:
            print(f"      * {e}")
    else:
        print(f"\n  [OK] Todos os scripts executados com sucesso!")

    print(f"\n  Estrutura de saída:")
    print(f"    saida/")
    print(f"    ├── 95/   (resultados com limiar >= 0.95)")
    print(f"    ├── 75/   (resultados com limiar >= 0.75)")
    print(f"    └── (gráficos exploratórios sem limiar)")
    print(f"\nConcluído.\n")


if __name__ == "__main__":
    main()
