# Teoria da Decisão - ENTREGA #2: Otimização Bi-objetivo

import random
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ===========================
# 1. Carregamento de Dados
# ===========================
def carregar_csv(nome_arquivo):
    base_dir = Path(__file__).resolve().parent
    candidatos = [base_dir / nome_arquivo, base_dir / "data" / nome_arquivo]
    for caminho in candidatos:
        if caminho.exists():
            return pd.read_csv(caminho, header=None)
    raise FileNotFoundError(f"Arquivo {nome_arquivo} não encontrado nas opções {candidatos}.")


def carregar_matrizes(verbose=True):
    distancia_df = carregar_csv("distancia.csv")
    tempo_df = carregar_csv("tempo.csv")
    distancia = distancia_df.values.astype(float)
    tempo = tempo_df.values.astype(float)
    if verbose:
        print(f"Matriz de distâncias carregada com sucesso. Shape: {distancia.shape}")
        print(f"Matriz de tempos carregada com sucesso. Shape: {tempo.shape}")
    return distancia, tempo

# Matrizes globais serão configuradas em tempo de execução.
distancia_matrix = None
tempo_matrix = None
tempo_matriz_norm = None
distancia_matriz_norm = None
TEMPO_MIN = None
TEMPO_MAX = None
DIST_MIN = None
DIST_MAX = None


def configurar_matrizes_globais(distancia, tempo, verbose=False):
    global distancia_matrix, tempo_matrix
    global tempo_matriz_norm, distancia_matriz_norm
    global TEMPO_MIN, TEMPO_MAX, DIST_MIN, DIST_MAX

    distancia_matrix = np.asarray(distancia, dtype=float)
    tempo_matrix = np.asarray(tempo, dtype=float)

    if verbose:
        print(f"Matriz de distâncias carregada com sucesso. Shape: {distancia_matrix.shape}")
        print(f"Matriz de tempos carregada com sucesso. Shape: {tempo_matrix.shape}")

    tempo_matriz_norm = normalizar_matriz(tempo_matrix)
    distancia_matriz_norm = normalizar_matriz(distancia_matrix)
    TEMPO_MIN, TEMPO_MAX = estimar_limites_totais(tempo_matrix)
    DIST_MIN, DIST_MAX = estimar_limites_totais(distancia_matrix)


def garantir_matrizes_carregadas(verbose=False):
    if distancia_matrix is None or tempo_matrix is None:
        distancia, tempo = carregar_matrizes(verbose=verbose)
        configurar_matrizes_globais(distancia, tempo, verbose=verbose)


def inicializar_worker(matriz_distancia, matriz_tempo):
    configurar_matrizes_globais(matriz_distancia, matriz_tempo, verbose=False)

# ## 2. Função de Custo e Representação da Solução
#
# Uma solução (ou rota) é representada por um array de inteiros que define a ordem em que as cidades são visitadas. A função de custo calcula o comprimento total de uma rota, somando os custos (distância ou tempo) de cada segmento da viagem, incluindo o retorno à cidade inicial.
def calcular_custo(rota, matriz_custo):
    custo_total = 0.0
    for i in range(len(rota) - 1):
        custo_total += matriz_custo[rota[i], rota[i + 1]]
    custo_total += matriz_custo[rota[-1], rota[0]]
    return float(custo_total)

# ## 3. Heurística Construtiva para a Solução Inicial
#
# Para gerar uma solução inicial de boa qualidade, usamos uma heurística construtiva gulosa e aleatorizada. O algoritmo começa em uma cidade aleatória e, a cada passo, adiciona a cidade mais próxima que ainda não foi visitada. Para introduzir variabilidade, a escolha da "cidade mais próxima" é feita a partir de uma lista restrita de candidatos (RCL - Restricted Candidate List), e não apenas da melhor opção.
def calcular_custos_biobjetivo(rota):
    garantir_matrizes_carregadas()
    tempo = calcular_custo(rota, tempo_matrix)
    distancia = calcular_custo(rota, distancia_matrix)
    return tempo, distancia


def heuristica_construtiva_gulosa_aleatorizada(matriz_custo, rcl_size=3):
    """Constroi rota inicial; rcl_size limita quantas melhores cidades entram na escolha aleatoria."""
    num_cidades = matriz_custo.shape[0]
    cidade_inicial = np.random.randint(num_cidades)
    rota = [cidade_inicial]
    cidades_nao_visitadas = list(range(num_cidades))
    cidades_nao_visitadas.remove(cidade_inicial)

    cidade_atual = cidade_inicial
    while cidades_nao_visitadas:
        custos = [
            (matriz_custo[cidade_atual, proxima_cidade], proxima_cidade)
            for proxima_cidade in cidades_nao_visitadas
        ]
        custos.sort()
        rcl = custos[:rcl_size]
        _, proxima_cidade = rcl[np.random.randint(len(rcl))]
        rota.append(proxima_cidade)
        cidades_nao_visitadas.remove(proxima_cidade)
        cidade_atual = proxima_cidade

    return np.array(rota, dtype=int)

# ## 4. Estruturas de Vizinhança
#
# Implementamos três estruturas de vizinhança para explorar o espaço de soluções:
# *   **2-Opt:** Uma troca simples de duas arestas para remover cruzamentos na rota.
# *   **Or-Opt:** Move um pequeno bloco de cidades para uma posição diferente na rota.
# *   **Double-Bridge:** Uma perturbação maior que corta a rota em quatro partes e as reconecta de uma maneira diferente.
def vizinhanca_2_opt(rota):
    """Gera uma nova rota trocando duas arestas."""
    num_cidades = len(rota)
    i, j = np.random.choice(num_cidades, 2, replace=False)
    if i > j:
        i, j = j, i
    nova_rota = np.copy(rota)
    nova_rota[i:j+1] = np.flip(nova_rota[i:j+1])
    return nova_rota

def vizinhanca_or_opt(rota, tamanho_bloco=3):
    """Move um bloco de cidades para outra posição."""
    num_cidades = len(rota)
    i = np.random.randint(0, num_cidades - tamanho_bloco)
    j = np.random.randint(0, num_cidades - tamanho_bloco)

    bloco = rota[i:i+tamanho_bloco]
    rota_sem_bloco = np.delete(rota, np.arange(i, i + tamanho_bloco))

    return np.insert(rota_sem_bloco, j, bloco)

def vizinhanca_double_bridge(rota):
    """Aplica o movimento double-bridge para perturbar a rota."""
    num_cidades = len(rota)
    indices = sorted(np.random.choice(num_cidades, 4, replace=False))
    i, j, k, l = indices

    parte1 = rota[:i]
    parte2 = rota[i:j]
    parte3 = rota[j:k]
    parte4 = rota[k:l]
    parte5 = rota[l:]

    return np.concatenate([parte1, parte4, parte3, parte2, parte5])

# ## 5. Busca Local e Metaheurística
#
# Versões genéricas do VND e GVNS que operam sobre uma função objetivo arbitrária.
def vnd_generico(rota_inicial, avaliar, vizinhancas):
    melhor_rota = np.copy(rota_inicial)
    melhor_valor = avaliar(melhor_rota)
    l = 0
    while l < len(vizinhancas):
        vizinhanca = vizinhancas[l]
        nova_rota = vizinhanca(melhor_rota)
        novo_valor = avaliar(nova_rota)
        if novo_valor < melhor_valor:
            melhor_rota = nova_rota
            melhor_valor = novo_valor
            l = 0
        else:
            l += 1
    return melhor_rota, melhor_valor


def gvns_generico(rota_inicial, avaliar, vizinhancas, kmax, max_iter, return_curve=False):
    melhor_rota = np.copy(rota_inicial)
    melhor_valor = avaliar(melhor_rota)
    historico = [melhor_valor]
    sem_melhora = 0

    while sem_melhora < max_iter:
        k = 0
        while k < kmax and sem_melhora < max_iter:
            rota_perturbada = vizinhancas[k](melhor_rota)
            nova_rota, novo_valor = vnd_generico(rota_perturbada, avaliar, vizinhancas)
            if novo_valor < melhor_valor:
                melhor_rota = nova_rota
                melhor_valor = novo_valor
                k = 0
                sem_melhora = 0
            else:
                k += 1
                sem_melhora += 1
            historico.append(melhor_valor)

    if return_curve:
        return melhor_rota, melhor_valor, historico
    return melhor_rota, melhor_valor

# ===========================
# 5. Normalização e Fronteiras
# ===========================
def normalizar_matriz(matriz):
    minimo = matriz.min()
    maximo = matriz.max()
    if maximo == minimo:
        return np.zeros_like(matriz)
    return (matriz - minimo) / (maximo - minimo)


def estimar_limites_totais(matriz):
    minimo = np.min(matriz, axis=1).sum()
    maximo = np.max(matriz, axis=1).sum()
    return minimo, maximo


def normalizar_valor(valor, minimo, maximo):
    if maximo == minimo:
        return 0.0
    return (valor - minimo) / (maximo - minimo)


def domina(sol_a, sol_b):
    return (
        sol_a["tempo"] <= sol_b["tempo"]
        and sol_a["distancia"] <= sol_b["distancia"]
        and (sol_a["tempo"] < sol_b["tempo"] or sol_a["distancia"] < sol_b["distancia"])
    )


def inserir_na_fronteira(fronteira, sol, origem="?"):
    for existente in fronteira:
        if domina(existente, sol):
            return fronteira, False
    fronteira = [existente for existente in fronteira if not domina(sol, existente)]
    fronteira.append(sol)
    print(
        f"[Fronteira {origem}] nova solução não-dominada adicionada: "
        f"id={sol['id']} tempo={sol['tempo']:.3f} distância={sol['distancia']:.3f}"
    )
    return fronteira, True


def calcular_hipervolume_2d(solucoes, referencia):
    if not solucoes:
        return 0.0
    pontos = sorted(((sol["tempo"], sol["distancia"]) for sol in solucoes), key=lambda x: x[0])
    hipervolume = 0.0
    limite_tempo, limite_distancia = referencia
    for i, (tempo, distancia) in enumerate(pontos):
        proximo_tempo = pontos[i + 1][0] if i + 1 < len(pontos) else limite_tempo
        largura = max(proximo_tempo - tempo, 0.0) if i + 1 < len(pontos) else max(limite_tempo - tempo, 0.0)
        altura = max(limite_distancia - distancia, 0.0)
        hipervolume += largura * altura
    return hipervolume


# ===========================
# 6. Scalarizações
# ===========================
def construir_matriz_pw(peso):
    garantir_matrizes_carregadas()
    return peso * tempo_matriz_norm + (1.0 - peso) * distancia_matriz_norm


def criar_avaliador_pw(peso):
    garantir_matrizes_carregadas()

    def avaliador(rota):
        tempo, distancia = calcular_custos_biobjetivo(rota)
        tempo_norm = normalizar_valor(tempo, TEMPO_MIN, TEMPO_MAX)
        dist_norm = normalizar_valor(distancia, DIST_MIN, DIST_MAX)
        return peso * tempo_norm + (1.0 - peso) * dist_norm

    return avaliador


# Penalidade alta para forcar cumprimento do epsilon no metodo Pε.
#PENALIDADE_PE = 1e6
PENALIDADE_PE = 1e4


def criar_avaliador_pe(modo_principal, epsilon):
    garantir_matrizes_carregadas()

    if modo_principal == "tempo":
        matriz_base = tempo_matriz_norm
        minimo_eps, maximo_eps = DIST_MIN, DIST_MAX
    else:
        matriz_base = distancia_matriz_norm
        minimo_eps, maximo_eps = TEMPO_MIN, TEMPO_MAX

    epsilon = float(np.clip(epsilon, minimo_eps, maximo_eps))

    def avaliador(rota):
        tempo, distancia = calcular_custos_biobjetivo(rota)
        if modo_principal == "tempo":
            violacao = max(distancia - epsilon, 0.0)
            return tempo + PENALIDADE_PE * violacao
        violacao = max(tempo - epsilon, 0.0)
        return distancia + PENALIDADE_PE * violacao

    return avaliador, matriz_base


# ===========================
# 7. Execuções Paralelas
# ===========================
# Numero de vizinhancas distintas exploradas na fase de shaking do GVNS.
KMAX = 3
# Limite de iteracoes sem melhora antes de interromper o GVNS.
TMAX = 5000
# Quantas vezes repetir todo o pipeline Pw e Pε para coletar 5 fronteiras.
NUM_REPETICOES = 5
# Quantas execucoes paralelas de GVNS por repeticao (maior => fronteiras mais densas).
SOLUCOES_POR_REPETICAO = 2000
# Limite maximo de solucoes nao dominadas consideradas por fronteira.
LIMITE_SOLUCOES_FRONTEIRA = 20
# Limite de processos em paralelo; respeita teto de 8 ou numero de CPUs disponiveis.
MAX_WORKERS = min(8, cpu_count())


def executar_pw(_):
    seed = int(time.time_ns() % (2**32 - 1))
    rng = np.random.default_rng(seed)
    np.random.seed(rng.integers(0, 2**32 - 1))
    random.seed(int(rng.integers(0, 2**32 - 1)))

    peso = rng.uniform(0.0, 1.0)
    matriz_pw = construir_matriz_pw(peso)
    rota_inicial = heuristica_construtiva_gulosa_aleatorizada(matriz_pw)
    avaliador = criar_avaliador_pw(peso)
    rota, _, historico = gvns_generico(
        rota_inicial,
        avaliador,
        [vizinhanca_2_opt, vizinhanca_or_opt, vizinhanca_double_bridge],
        KMAX,
        TMAX,
        return_curve=True,
    )
    tempo, distancia = calcular_custos_biobjetivo(rota)
    return {
        "id": f"pw_{seed}",
        "rota": rota.tolist(),
        "tempo": tempo,
        "distancia": distancia,
        "peso": peso,
        "historico": historico,
    }


def executar_pe(_):
    seed = int(time.time_ns() % (2**32 - 1))
    rng = np.random.default_rng(seed)
    np.random.seed(rng.integers(0, 2**32 - 1))
    random.seed(int(rng.integers(0, 2**32 - 1)))

    modo = rng.choice(["tempo", "distancia"])
    epsilon = rng.uniform(DIST_MIN, DIST_MAX) if modo == "tempo" else rng.uniform(TEMPO_MIN, TEMPO_MAX)
    avaliador, matriz_base = criar_avaliador_pe(modo, epsilon)
    rota_inicial = heuristica_construtiva_gulosa_aleatorizada(matriz_base)
    rota, _, historico = gvns_generico(
        rota_inicial,
        avaliador,
        [vizinhanca_2_opt, vizinhanca_or_opt, vizinhanca_double_bridge],
        KMAX,
        TMAX,
        return_curve=True,
    )
    tempo, distancia = calcular_custos_biobjetivo(rota)
    return {
        "id": f"pe_{seed}",
        "rota": rota.tolist(),
        "tempo": tempo,
        "distancia": distancia,
        "modo": modo,
        "epsilon": epsilon,
        "historico": historico,
    }


# ===========================
# 8. Pós-processamento
# ===========================
def construir_fronteira(resultados, limite=LIMITE_SOLUCOES_FRONTEIRA, origem="?"):
    fronteira = []
    solucoes = [
        {
            "id": item["id"],
            "tempo": item["tempo"],
            "distancia": item["distancia"],
            "dados": item,
        }
        for item in resultados
    ]
    for sol in solucoes:
        fronteira, adicionada = inserir_na_fronteira(fronteira, sol, origem)
        if adicionada and len(fronteira) >= limite:
            break
    return fronteira


def visualizar_fronteiras(todas_fronteiras, titulo, nome_arquivo):
    plt.figure(figsize=(12, 8))
    cores = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]
    for idx, fronteira in enumerate(todas_fronteiras):
        if not fronteira:
            continue
        tempos = [sol["tempo"] for sol in fronteira]
        distancias = [sol["distancia"] for sol in fronteira]
        plt.scatter(
            tempos,
            distancias,
            color=cores[idx % len(cores)],
            alpha=0.7,
            label=f"Repetição {idx + 1}",
        )
    plt.xlabel("Tempo (h)")
    plt.ylabel("Distância (km)")
    plt.title(f"Fronteiras de Pareto - {titulo}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    base_dir = Path(__file__).resolve().parent / "outputs"
    base_dir.mkdir(exist_ok=True)
    caminho = base_dir / nome_arquivo
    plt.savefig(caminho, dpi=150)
    plt.close()


def exportar_resultados_csv(fronteiras_pw, fronteiras_pe):
    base_dir = Path(__file__).resolve().parent / "outputs"
    base_dir.mkdir(exist_ok=True)

    for metodo, fronteiras in [("pw", fronteiras_pw), ("pe", fronteiras_pe)]:
        registros = []
        for repeticao, fronteira in enumerate(fronteiras, start=1):
            for sol in fronteira:
                registro = {
                    "repeticao": repeticao,
                    "tempo": sol["tempo"],
                    "distancia": sol["distancia"],
                }
                registro.update({k: v for k, v in sol["dados"].items() if k not in {"rota", "historico"}})
                registros.append(registro)
        df = pd.DataFrame(registros)
        df.to_csv(base_dir / f"fronteira_{metodo}.csv", index=False)


def calcular_hipervolumes(fronteiras_pw, fronteiras_pe):
    valores_tempo = [sol["tempo"] for fronteira in fronteiras_pw + fronteiras_pe for sol in fronteira]
    valores_dist = [sol["distancia"] for fronteira in fronteiras_pw + fronteiras_pe for sol in fronteira]
    if not valores_tempo or not valores_dist:
        return []
    referencia = (max(valores_tempo) * 1.05, max(valores_dist) * 1.05)
    hipervolumes = []
    for repeticao, (fronteira_pw, fronteira_pe) in enumerate(zip(fronteiras_pw, fronteiras_pe), start=1):
        hv_pw = calcular_hipervolume_2d(fronteira_pw, referencia)
        hv_pe = calcular_hipervolume_2d(fronteira_pe, referencia)
        hipervolumes.append({"repeticao": repeticao, "hv_pw": hv_pw, "hv_pe": hv_pe})
    return hipervolumes


def calcular_media_historico(resultados):
    """Retorna a media da melhor avaliacao por iteracao ao longo das execucoes."""
    if not resultados:
        return []
    comprimento_maximo = max(len(item.get("historico", [])) for item in resultados)
    medias = []
    for idx in range(comprimento_maximo):
        valores = []
        for item in resultados:
            historico = item.get("historico", [])
            if len(historico) > idx:
                valores.append(historico[idx])
        medias.append(float(np.mean(valores)))
    return medias


# ===========================
# 9. Execução Principal
# ===========================
def executar_otimizacao_biobjetivo():
    garantir_matrizes_carregadas(verbose=True)
    matriz_dist = distancia_matrix
    matriz_tempo = tempo_matrix

    fronteiras_pw = []
    fronteiras_pe = []
    medias_repeticao_pw = []
    medias_repeticao_pe = []
    historicos_pw = []
    historicos_pe = []

    for repeticao in range(NUM_REPETICOES):
        print(f"\nRepetição {repeticao + 1}/{NUM_REPETICOES}")

        with ProcessPoolExecutor(
            max_workers=MAX_WORKERS,
            initializer=inicializar_worker,
            initargs=(matriz_dist, matriz_tempo),
        ) as executor:
            resultados_pw = list(executor.map(executar_pw, range(SOLUCOES_POR_REPETICAO)))
        with ProcessPoolExecutor(
            max_workers=MAX_WORKERS,
            initializer=inicializar_worker,
            initargs=(matriz_dist, matriz_tempo),
        ) as executor:
            resultados_pe = list(executor.map(executar_pe, range(SOLUCOES_POR_REPETICAO)))

        historicos_pw.extend(resultados_pw)
        historicos_pe.extend(resultados_pe)
        medias_repeticao_pw.append(calcular_media_historico(resultados_pw))
        medias_repeticao_pe.append(calcular_media_historico(resultados_pe))

        fronteira_pw = construir_fronteira(resultados_pw, origem="Pw")
        fronteira_pe = construir_fronteira(resultados_pe, origem="Pe")
        fronteiras_pw.append(fronteira_pw)
        fronteiras_pe.append(fronteira_pe)

        print(f"  Fronteira Pw possui {len(fronteira_pw)} soluções não-dominadas")
        print(f"  Fronteira Pe possui {len(fronteira_pe)} soluções não-dominadas")

    visualizar_fronteiras(fronteiras_pw, "Weighted Sum (Pw)", "fronteiras_pw.png")
    visualizar_fronteiras(fronteiras_pe, "Epsilon-Constraint (Pε)", "fronteiras_pe.png")

    exportar_resultados_csv(fronteiras_pw, fronteiras_pe)

    hipervolumes = calcular_hipervolumes(fronteiras_pw, fronteiras_pe)
    if hipervolumes:
        df_hv = pd.DataFrame(hipervolumes)
        print("\nHipervolumes por repetição:")
        print(df_hv.to_string(index=False))
    else:
        print("\nNão foi possível calcular hipervolume (fronteiras vazias).")

    media_global_pw = calcular_media_historico(historicos_pw)
    media_global_pe = calcular_media_historico(historicos_pe)
    if media_global_pw or media_global_pe:
        max_iter = max(len(media_global_pw), len(media_global_pe))
        media_pw_alinhada = media_global_pw + [np.nan] * (max_iter - len(media_global_pw))
        media_pe_alinhada = media_global_pe + [np.nan] * (max_iter - len(media_global_pe))
        df_media = pd.DataFrame(
            {
                "iteracao": range(max_iter),
                "media_pw": media_pw_alinhada,
                "media_pe": media_pe_alinhada,
            }
        )
        print("\nMédia da melhor avaliação por iteração (todas as execuções):")
        print(df_media.to_string(index=False))

    return {
        "fronteiras_pw": fronteiras_pw,
        "fronteiras_pe": fronteiras_pe,
        "hipervolumes": hipervolumes,
        "medias_repeticao_pw": medias_repeticao_pw,
        "medias_repeticao_pe": medias_repeticao_pe,
        "media_global_pw": media_global_pw,
        "media_global_pe": media_global_pe,
    }


def executar_otimizacao_monoobjetivo():
    garantir_matrizes_carregadas()

    resultados = {"Tempo": [], "Distancia": [], "Historico_Tempo": [], "Historico_Distancia": []}
    vizinhancas = [vizinhanca_2_opt, vizinhanca_or_opt, vizinhanca_double_bridge]
    print("Otimizando para Tempo (referência)...")
    for idx in range(5):
        rota_inicial = heuristica_construtiva_gulosa_aleatorizada(tempo_matrix)
        rota, _, historico = gvns_generico(
            rota_inicial,
            lambda r: calcular_custo(r, tempo_matrix),
            vizinhancas,
            KMAX,
            TMAX,
            return_curve=True,
        )
        custo = calcular_custo(rota, tempo_matrix)
        resultados["Tempo"].append(custo)
        resultados["Historico_Tempo"].append(historico)
        print(f"  Execução {idx + 1}: custo tempo = {custo:.2f}")

    print("\nOtimizando para Distância (referência)...")
    for idx in range(5):
        rota_inicial = heuristica_construtiva_gulosa_aleatorizada(distancia_matrix)
        rota, _, historico = gvns_generico(
            rota_inicial,
            lambda r: calcular_custo(r, distancia_matrix),
            vizinhancas,
            KMAX,
            TMAX,
            return_curve=True,
        )
        custo = calcular_custo(rota, distancia_matrix)
        resultados["Distancia"].append(custo)
        resultados["Historico_Distancia"].append(historico)
        print(f"  Execução {idx + 1}: custo distancia = {custo:.2f}")

    resumo = pd.DataFrame(
        {
            "Função": ["Tempo", "Distancia"],
            "Mínimo": [np.min(resultados["Tempo"]), np.min(resultados["Distancia"])],
            "Máximo": [np.max(resultados["Tempo"]), np.max(resultados["Distancia"])],
            "Desvio Padrão": [np.std(resultados["Tempo"]), np.std(resultados["Distancia"])],
        }
    )
    print("\nResumo mono-objetivo de referência:")
    print(resumo.to_string(index=False))
    return resultados, resumo


if __name__ == "__main__":
    executar_otimizacao_biobjetivo()

