"""
rodar_analises.py
=================
Script orquestrador que roda o pipeline completo de análises 50k por ano:
  1. Separação dos embeddings por ano (se ainda não existirem)
  2. Geração da Matriz de Similaridade anual (matriz_similaridade_50k_{ano}.parquet)
  3. Geração da Tabela Top-3 anual (tabela_top3_pivotada_50k_{ano}.parquet + CSV + JSON em assets/)
  4. Análises com e sem limiar (0 e 0.75)
  5. Análise cruzada MapBiomas vs Embrapa
  6. Pipeline filtrado Pastagem 75%

Uso:
    python rodar_analises.py               # Processa ano padrão (2025)
    python rodar_analises.py --year 2024  # Processa ano específico
    python rodar_analises.py --year all   # Processa todos os anos (2019 a 2025)
"""

import subprocess
import sys
import argparse
from pathlib import Path

DIR_SCRIPTS = Path(__file__).resolve().parent
DIR_ROOT = DIR_SCRIPTS.parent
DIR_METRICAS = DIR_ROOT / "produto_escalar_metricas"
DIR_ARQUIVOS_BASE = DIR_METRICAS / "arquivos_base"
DIR_SAIDA = DIR_METRICAS / "arquivos_saida"
DIR_SAIDA.mkdir(parents=True, exist_ok=True)

PYTHON = sys.executable

# Limiares a processar: 0 = "sem limiar", 0.75 = limiar de 75%
LIMIARES = [0, 0.75]

# Scripts que DEPENDEM de limiar
SCRIPTS_COM_LIMIAR = [
    "filtro_dados_matriz.py",
    "analise_matriz_similaridade.py",
    "contar_pontos_sobraram.py",
    "histogramas_tipologia_prod_escalar.py",
    "analise_top3_50k.py",
]

# Scripts que NÃO dependem de limiar
SCRIPTS_SEM_LIMIAR = [
    "gerar_graficos_tipologia.py",
    "analise_cruzada_mapbiomas_embrapa.py",
    "pipeline_filtrado_pastagem_75.py",
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


def processar_ano_completo(ano: int):
    print("\n" + "#" * 70)
    print(f"  INICIANDO PIPELINE DE ANÁLISES PARA O ANO: {ano}")
    print("#" * 70)

    # 1. Gerar matriz de similaridade pivotada anual
    ok = rodar("gerar_matriz_similaridade_50k.py", ["--year", str(ano)])
    if not ok:
        print(f"\n  [ERRO FATAL] Falha ao gerar matriz para {ano}. Abortando.")
        return False

    # 2. Gerar tabela Top-3 pivotada com MD3 + CSV + JSON em assets/
    ok = rodar("gerar_top3_pivotada_50k.py", ["--year", str(ano)])
    if not ok:
        print(f"\n  [ERRO FATAL] Falha ao gerar tabela top-3 para {ano}. Abortando.")
        return False

    # Criar pastas de saída para cada limiar
    for limiar in LIMIARES:
        label = "sem_limiar" if limiar <= 0 else str(int(limiar * 100))
        pasta = DIR_SAIDA / label
        pasta.mkdir(parents=True, exist_ok=True)

    erros = []

    # 3. Scripts COM limiar (0 e 0.75)
    for limiar in LIMIARES:
        limiar_str = str(limiar)
        label = "sem limiar" if limiar <= 0 else f">= {limiar}"
        label_folder = "sem_limiar" if limiar <= 0 else str(int(limiar * 100))
        print(f"\n\n{'#' * 70}")
        print(f"  PROCESSANDO: {label} (ano: {ano}, pasta: arquivos_saida/{label_folder}/)")
        print(f"{'#' * 70}")

        for script in SCRIPTS_COM_LIMIAR:
            args = ["--limiar", limiar_str]
            if script in ["analise_top3_50k.py", "filtro_dados_matriz.py", "analise_matriz_similaridade.py", "histogramas_tipologia_prod_escalar.py"]:
                args.extend(["--year", str(ano)])
            ok = rodar(script, args)
            if not ok:
                erros.append(f"{script} --limiar {limiar_str} (ano {ano})")

    # 4. Scripts SEM limiar
    print(f"\n\n{'#' * 70}")
    print(f"  PROCESSANDO SCRIPTS SEM LIMIAR (ano: {ano})")
    print(f"{'#' * 70}")

    for script in SCRIPTS_SEM_LIMIAR:
        args = []
        if script in ["analise_cruzada_mapbiomas_embrapa.py", "pipeline_filtrado_pastagem_75.py"]:
            args.extend(["--year", str(ano)])
        ok = rodar(script, args)
        if not ok:
            erros.append(f"{script} (ano {ano})")

    return erros


def main():
    parser = argparse.ArgumentParser(description="Orquestrador de análises 50k por ano.")
    parser.add_argument("--year", default="2025", help="Ano a processar (ex: 2025, 2024, ou 'all')")
    args = parser.parse_args()

    print("=" * 70)
    print("  ORQUESTRADOR DE ANÁLISES - 50K")
    print(f"  Ano(s) selecionado(s): {args.year}")
    print(f"  Limiares: sem limiar + 0.75")
    print(f"  Pasta de saída: {DIR_SAIDA}")
    print("=" * 70)

    # Verificar se os embeddings anuais existem
    p_2025 = DIR_ARQUIVOS_BASE / "embeddings_samples_50k_cvp_s2_cerrado_2025.parquet"
    if not p_2025.exists():
        print("\nEmbeddings anuais não encontrados. Executando separação inicial...")
        rodar("separar_embeddings_por_ano.py")

    if args.year.lower() == "all":
        anos = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
    else:
        try:
            anos = [int(args.year)]
        except ValueError:
            print(f"Erro: Ano inválido '{args.year}'")
            return

    todos_erros = []
    for ano in anos:
        erros_ano = processar_ano_completo(ano)
        if erros_ano:
            todos_erros.extend(erros_ano)

    # --- Resumo ---
    print(f"\n\n{'=' * 70}")
    print("  RESUMO FINAL")
    print(f"{'=' * 70}")

    if todos_erros:
        print(f"\n  [!] {len(todos_erros)} script(s) com erro:")
        for e in todos_erros:
            print(f"      * {e}")
    else:
        print(f"\n  [OK] Todas as etapas e anos ({', '.join(map(str, anos))}) executados com sucesso!")

    print(f"\n  Arquivos gerados para o GitHub / Web:")
    print(f"    assets/tabela_top3_50k_<ano>.csv")
    print(f"    assets/tabela_top3_50k_<ano>.json")
    print(f"\nConcluído.\n")


if __name__ == "__main__":
    main()
