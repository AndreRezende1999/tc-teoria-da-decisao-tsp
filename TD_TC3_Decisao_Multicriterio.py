"""
Entrega 3: Tomada de Decisão Multicritério
Teoria da Decisão - Travelling Salesman Problem (TSP)

Este script implementa métodos de auxílio à tomada de decisão (AHP e TOPSIS)
para selecionar a melhor solução da fronteira de Pareto obtida na Entrega 2.
"""

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from math import pi
import warnings

warnings.filterwarnings('ignore')

# %%
# =============================================================================
# 1. CARREGAMENTO DOS DADOS DA FRONTEIRA UNIFICADA
# =============================================================================

print("=" * 60)
print("CARREGAMENTO DOS DADOS")
print("=" * 60)

# Carregar fronteira unificada (união das fronteiras PE e PW da Entrega 2)
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
df_fronteira = pd.read_csv(BASE_DIR / 'outputs' / 'fronteira_unificada.csv')

print(f"\nTotal de soluções carregadas: {len(df_fronteira)}")
print(f"  - Epsilon-restrito: {len(df_fronteira[df_fronteira['metodo'] == 'epsilon-restrito'])}")
print(f"  - Soma ponderada: {len(df_fronteira[df_fronteira['metodo'] == 'soma-ponderada'])}")

print("\nAtributos disponíveis:")
print("  - Tempo (horas): objetivo original - MINIMIZAR")
print("  - Distância (km): objetivo original - MINIMIZAR")
print("  - Alta Velocidade (trechos >80 km/h): MINIMIZAR (segurança)")
print("  - Balanceamento (desvio padrão): MINIMIZAR (regularidade)")

print("\nEstatísticas dos atributos:")
print(df_fronteira[['tempo', 'distancia', 'alta_velocidade', 'balanceamento']].describe())

# %%
# =============================================================================
# 2. FILTRAGEM DAS SOLUÇÕES NÃO-DOMINADAS
# =============================================================================

print("\n" + "=" * 60)
print("FILTRAGEM DE SOLUÇÕES NÃO-DOMINADAS")
print("=" * 60)

criterios_minimizacao = ['tempo', 'distancia', 'alta_velocidade', 'balanceamento']


def eh_dominada(idx, df, criterios):
    """Verifica se a solução no índice idx é dominada por alguma outra."""
    solucao = df.loc[idx]
    for outro_idx in df.index:
        if outro_idx == idx:
            continue
        outra = df.loc[outro_idx]

        # Verifica se 'outra' domina 'solucao'
        melhor_em_todos = True
        melhor_em_algum = False

        for crit in criterios:
            if outra[crit] < solucao[crit]:
                melhor_em_algum = True
            elif outra[crit] > solucao[crit]:
                melhor_em_todos = False
                break

        if melhor_em_todos and melhor_em_algum:
            return True
    return False


def filtrar_nao_dominadas(df, criterios):
    """Retorna apenas as soluções não-dominadas."""
    indices_nao_dominadas = []
    for idx in df.index:
        if not eh_dominada(idx, df, criterios):
            indices_nao_dominadas.append(idx)
    return df.loc[indices_nao_dominadas].reset_index(drop=True)


# Filtrar soluções não-dominadas
df_nao_dominadas = filtrar_nao_dominadas(df_fronteira, criterios_minimizacao)

print(f"\nSoluções não-dominadas: {len(df_nao_dominadas)} de {len(df_fronteira)}")


def selecionar_bem_distribuidas(df, criterios, num_solucoes=20):
    """Seleciona soluções bem distribuídas ao longo da fronteira."""
    if len(df) <= num_solucoes:
        return df

    # Normalizar atributos
    X = df[criterios].values
    X_norm = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0) + 1e-10)

    # Seleção por máxima dispersão
    selecionadas = [0]

    for _ in range(num_solucoes - 1):
        melhor_idx = -1
        maior_dist_min = -1

        for i in range(len(df)):
            if i in selecionadas:
                continue

            dist_min = min(np.linalg.norm(X_norm[i] - X_norm[j]) for j in selecionadas)

            if dist_min > maior_dist_min:
                maior_dist_min = dist_min
                melhor_idx = i

        if melhor_idx >= 0:
            selecionadas.append(melhor_idx)

    return df.iloc[selecionadas].reset_index(drop=True)


# Selecionar até 20 soluções bem distribuídas
df_analise = selecionar_bem_distribuidas(df_nao_dominadas, criterios_minimizacao, num_solucoes=20)

print(f"Soluções selecionadas para análise: {len(df_analise)}")

print("\nSoluções selecionadas:")
print(df_analise[['id', 'metodo', 'tempo', 'distancia', 'alta_velocidade', 'balanceamento']])

# %%
# =============================================================================
# 3. MÉTODO AHP (Analytic Hierarchy Process)
# =============================================================================

print("\n" + "=" * 60)
print("MÉTODO AHP - Analytic Hierarchy Process")
print("=" * 60)


def calcular_pesos_ahp(matriz_comparacao):
    """
    Calcula os pesos dos critérios usando o método AHP.

    O AHP utiliza comparações par-a-par entre critérios para derivar
    pesos relativos. A matriz de comparação deve ser recíproca positiva.
    """
    # Calcular autovalores e autovetores
    autovalores, autovetores = np.linalg.eig(matriz_comparacao)

    # Encontrar o maior autovalor (lambda_max)
    idx_max = np.argmax(np.real(autovalores))
    autovetor_principal = np.real(autovetores[:, idx_max])

    # Normalizar para obter os pesos
    pesos = autovetor_principal / autovetor_principal.sum()

    # Calcular índice de consistência
    lambda_max = np.real(autovalores[idx_max])
    n = len(matriz_comparacao)
    CI = (lambda_max - n) / (n - 1)

    # Índice randômico (RI) para matrizes de tamanho n
    RI_dict = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45}
    RI = RI_dict.get(n, 1.45)

    # Razão de consistência
    CR = CI / RI if RI > 0 else 0

    return pesos, CR, lambda_max


# Matriz de comparação par-a-par dos critérios
# Escala Saaty: 1 = igual importância, 3 = moderada, 5 = forte, 7 = muito forte, 9 = extrema
#
# Hierarquia: Tempo > Distância > Alta Velocidade > Balanceamento
# Razão de ~2x entre níveis adjacentes para garantir consistência (CR < 0.1)
#
# Interpretação:
#   - Tempo vs Distância: 2 (tempo é levemente mais importante)
#   - Tempo vs Alta_Velocidade: 4 (tempo é moderadamente mais importante)
#   - Tempo vs Balanceamento: 8 (tempo é muito mais importante)
#   - Distância vs Alta_Velocidade: 2 (distância é levemente mais importante)
#   - Distância vs Balanceamento: 4 (distância é moderadamente mais importante)
#   - Alta_Velocidade vs Balanceamento: 2 (alta velocidade é levemente mais importante)

matriz_comparacao_ahp = np.array([
    #    Tempo  Dist   AltaVel  Balanc
    [1,     2,     4,       8],      # Tempo
    [1/2,   1,     2,       4],      # Distância
    [1/4,   1/2,   1,       2],      # Alta Velocidade
    [1/8,   1/4,   1/2,     1],      # Balanceamento
])

pesos_ahp, CR, lambda_max = calcular_pesos_ahp(matriz_comparacao_ahp)

print("\nMatriz de Comparação Par-a-Par (Escala Saaty):")
criterios_nomes = ['Tempo', 'Distância', 'Alta Veloc.', 'Balanc.']
df_matriz = pd.DataFrame(matriz_comparacao_ahp, index=criterios_nomes, columns=criterios_nomes)
print(df_matriz.round(3))

print("\nPesos calculados pelo AHP:")
for i, (nome, peso) in enumerate(zip(criterios_nomes, pesos_ahp)):
    print(f"  {nome}: {peso:.4f} ({peso*100:.1f}%)")

print(f"\nÍndices de Consistência:")
print(f"  Lambda máximo: {lambda_max:.4f}")
print(f"  Razão de Consistência (CR): {CR:.4f}")
if CR < 0.1:
    print("  ✓ Matriz é consistente (CR < 0.1)")
else:
    print("  ⚠ Matriz pode ser inconsistente (CR >= 0.1)")


def aplicar_ahp_ranking(df, pesos, criterios):
    """
    Aplica ranking baseado nos pesos do AHP.
    Normaliza os valores e calcula score ponderado.
    """
    matriz = df[criterios].values

    # Normalização min-max (todos são critérios de minimização)
    matriz_norm = np.zeros_like(matriz, dtype=float)
    for j in range(len(criterios)):
        col_min = matriz[:, j].min()
        col_max = matriz[:, j].max()
        if col_max > col_min:
            # Inverter para minimização: menor valor = melhor = 0
            matriz_norm[:, j] = (matriz[:, j] - col_min) / (col_max - col_min)
        else:
            matriz_norm[:, j] = 0

    # Score ponderado (menor = melhor)
    scores = (matriz_norm * pesos).sum(axis=1)

    return scores


scores_ahp = aplicar_ahp_ranking(df_analise, pesos_ahp, criterios_minimizacao)
df_analise['Score_AHP'] = scores_ahp
df_analise['Rank_AHP'] = df_analise['Score_AHP'].rank(ascending=True)

print("\nTop 10 soluções pelo AHP (menor score = melhor):")
print(df_analise.nsmallest(10, 'Score_AHP')[['id', 'tempo', 'distancia', 'Score_AHP', 'Rank_AHP']])

# %%
# =============================================================================
# 4. MÉTODO TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)
# =============================================================================

print("\n" + "=" * 60)
print("MÉTODO TOPSIS")
print("=" * 60)


def topsis(df, pesos, criterios):
    """
    Aplica o método TOPSIS para ranking de alternativas.

    TOPSIS seleciona a alternativa mais próxima da solução ideal
    e mais distante da solução anti-ideal.

    Etapas:
    1. Normalização vetorial da matriz de decisão
    2. Ponderação pelos pesos dos critérios
    3. Identificação das soluções ideal e anti-ideal
    4. Cálculo das distâncias euclidianas
    5. Cálculo do coeficiente de proximidade relativa
    """
    matriz = df[criterios].values

    # 1. Normalização vetorial
    soma_quadrados = np.sqrt((matriz ** 2).sum(axis=0))
    matriz_norm = matriz / (soma_quadrados + 1e-10)

    # 2. Ponderação
    matriz_pond = matriz_norm * pesos

    # 3. Soluções ideal (mínimo, pois todos são de minimização) e anti-ideal (máximo)
    ideal = matriz_pond.min(axis=0)
    anti_ideal = matriz_pond.max(axis=0)

    # 4. Distâncias euclidianas
    dist_ideal = np.sqrt(((matriz_pond - ideal) ** 2).sum(axis=1))
    dist_anti_ideal = np.sqrt(((matriz_pond - anti_ideal) ** 2).sum(axis=1))

    # 5. Coeficiente de proximidade relativa (maior = melhor)
    scores = dist_anti_ideal / (dist_ideal + dist_anti_ideal + 1e-10)

    return scores


scores_topsis = topsis(df_analise, pesos_ahp, criterios_minimizacao)
df_analise['Score_TOPSIS'] = scores_topsis
df_analise['Rank_TOPSIS'] = df_analise['Score_TOPSIS'].rank(ascending=False)

print("\nTop 10 soluções pelo TOPSIS (maior score = melhor):")
print(df_analise.nlargest(10, 'Score_TOPSIS')[['id', 'tempo', 'distancia', 'Score_TOPSIS', 'Rank_TOPSIS']])

# %%
# =============================================================================
# 5. COMPARAÇÃO DOS MÉTODOS
# =============================================================================

print("\n" + "=" * 60)
print("COMPARAÇÃO ENTRE MÉTODOS AHP E TOPSIS")
print("=" * 60)

# Correlação de Spearman entre rankings
correlacao, p_value = spearmanr(df_analise['Rank_AHP'], df_analise['Rank_TOPSIS'])

print(f"\nCorrelação de Spearman entre rankings: {correlacao:.4f}")
print(f"P-valor: {p_value:.6f}")

if correlacao > 0.7:
    print("✓ Alta concordância entre os métodos")
elif correlacao > 0.4:
    print("⚠ Concordância moderada entre os métodos")
else:
    print("✗ Baixa concordância entre os métodos")

# Comparar Top 5
top5_ahp = set(df_analise.nsmallest(5, 'Score_AHP').index)
top5_topsis = set(df_analise.nlargest(5, 'Score_TOPSIS').index)
solucoes_comuns = top5_ahp.intersection(top5_topsis)

print(f"\nSoluções no Top 5 de ambos os métodos: {len(solucoes_comuns)}")
if solucoes_comuns:
    print(f"Índices: {sorted(solucoes_comuns)}")

print("\n--- Top 5 AHP (menor score = melhor) ---")
print(df_analise.nsmallest(5, 'Score_AHP')[['id', 'tempo', 'distancia', 'alta_velocidade', 'balanceamento', 'Score_AHP', 'Rank_AHP']])

print("\n--- Top 5 TOPSIS (maior score = melhor) ---")
print(df_analise.nlargest(5, 'Score_TOPSIS')[['id', 'tempo', 'distancia', 'alta_velocidade', 'balanceamento', 'Score_TOPSIS', 'Rank_TOPSIS']])

# %%
# =============================================================================
# 6. CRITÉRIO ADICIONAL PARA DESEMPATE/INCOMPARABILIDADE
# =============================================================================

print("\n" + "=" * 60)
print("CRITÉRIO ADICIONAL PARA DESEMPATE")
print("=" * 60)


def calcular_equilibrio(row, criterios):
    """
    Calcula um índice de equilíbrio baseado na variância normalizada.
    Soluções com melhor equilíbrio têm desempenho mais uniforme em todos os critérios.
    """
    valores = [row[crit] for crit in criterios]
    valores_norm = (np.array(valores) - np.min(valores)) / (np.max(valores) - np.min(valores) + 1e-10)
    return np.std(valores_norm)


df_analise['Equilibrio'] = df_analise.apply(lambda row: calcular_equilibrio(row, criterios_minimizacao), axis=1)

# Decisão final
if len(solucoes_comuns) > 0:
    print("\n✓ Concordância encontrada entre métodos!")
    print(f"  Selecionando entre {len(solucoes_comuns)} soluções comuns ao Top 5...")

    candidatas = df_analise.loc[list(solucoes_comuns)]

    # Normalizar scores para comparação
    score_ahp_norm = 1 - (candidatas['Score_AHP'] - candidatas['Score_AHP'].min()) / \
                        (candidatas['Score_AHP'].max() - candidatas['Score_AHP'].min() + 1e-10)
    score_topsis_norm = (candidatas['Score_TOPSIS'] - candidatas['Score_TOPSIS'].min()) / \
                        (candidatas['Score_TOPSIS'].max() - candidatas['Score_TOPSIS'].min() + 1e-10)

    # Score médio combinado
    score_combinado = (score_ahp_norm + score_topsis_norm) / 2
    idx_escolhido = score_combinado.idxmax()

else:
    print("\n⚠ Sem concordância clara entre métodos")
    print("  Aplicando critério adicional: melhor equilíbrio entre Top 10...")

    # Expandir para Top 10
    top10_ahp = set(df_analise.nsmallest(10, 'Score_AHP').index)
    top10_topsis = set(df_analise.nlargest(10, 'Score_TOPSIS').index)
    candidatas_idx = top10_ahp.intersection(top10_topsis)

    if len(candidatas_idx) > 0:
        candidatas = df_analise.loc[list(candidatas_idx)]
        idx_escolhido = candidatas['Equilibrio'].idxmin()
    else:
        # Usar melhor equilíbrio geral
        idx_escolhido = df_analise['Equilibrio'].idxmin()

solucao_final = df_analise.loc[idx_escolhido]

print("\n" + "=" * 60)
print("SOLUÇÃO FINAL ESCOLHIDA")
print("=" * 60)
print(f"\nID: {solucao_final['id']}")
print(f"Método de origem: {solucao_final['metodo']}")
print(f"\nAtributos:")
print(f"  Tempo Total: {solucao_final['tempo']:.2f} horas")
print(f"  Distância Total: {solucao_final['distancia']:.2f} km")
print(f"  Trechos Alta Velocidade (>80 km/h): {solucao_final['alta_velocidade']:.0f}")
print(f"  Balanceamento (desvio padrão): {solucao_final['balanceamento']:.2f}")
print(f"\nScores:")
print(f"  Score AHP: {solucao_final['Score_AHP']:.4f} (Rank: {solucao_final['Rank_AHP']:.0f})")
print(f"  Score TOPSIS: {solucao_final['Score_TOPSIS']:.4f} (Rank: {solucao_final['Rank_TOPSIS']:.0f})")
print(f"  Índice de Equilíbrio: {solucao_final['Equilibrio']:.4f}")

# %%
# =============================================================================
# 7. VISUALIZAÇÕES
# =============================================================================

print("\n" + "=" * 60)
print("GERANDO VISUALIZAÇÕES")
print("=" * 60)

# Criar diretório de saída
from pathlib import Path
output_dir = Path(__file__).resolve().parent / "outputs"
output_dir.mkdir(exist_ok=True)

# =============================================================================
# Estilo similar ao TD_ENTREGA2.py - Fronteira por método de origem
# =============================================================================

plt.figure(figsize=(12, 8))
cores = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]

# Separar por método de origem
metodos = df_analise['metodo'].unique()
for idx, metodo in enumerate(metodos):
    subset = df_analise[df_analise['metodo'] == metodo]
    plt.scatter(
        subset['tempo'],
        subset['distancia'],
        color=cores[idx % len(cores)],
        alpha=0.7,
        s=100,
        label=metodo.replace('-', ' ').title(),
        edgecolors='black',
        linewidth=0.5,
    )

# Destacar solução escolhida
plt.scatter(
    solucao_final['tempo'],
    solucao_final['distancia'],
    color='red',
    s=400,
    marker='*',
    edgecolors='darkred',
    linewidth=2,
    label='Solução Escolhida',
    zorder=10,
)

plt.xlabel("Tempo (h)", fontsize=12)
plt.ylabel("Distância (km)", fontsize=12)
plt.title("Fronteira de Pareto - Soluções por Método de Escalarização", fontsize=14, fontweight='bold')
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(output_dir / "fronteira_metodos.png", dpi=150)
plt.close()

# Fronteira com ranking por cores (estilo TD_ENTREGA2)
plt.figure(figsize=(12, 8))
scatter = plt.scatter(
    df_analise['tempo'],
    df_analise['distancia'],
    c=df_analise['Rank_TOPSIS'],
    cmap='RdYlGn',
    alpha=0.8,
    s=100,
    edgecolors='black',
    linewidth=0.5,
)
plt.scatter(
    solucao_final['tempo'],
    solucao_final['distancia'],
    color='blue',
    s=400,
    marker='*',
    edgecolors='darkblue',
    linewidth=2,
    label='Solução Escolhida',
    zorder=10,
)
plt.colorbar(scatter, label='Rank TOPSIS (menor = melhor)')
plt.xlabel("Tempo (h)", fontsize=12)
plt.ylabel("Distância (km)", fontsize=12)
plt.title("Fronteira de Pareto - Ranking TOPSIS", fontsize=14, fontweight='bold')
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(output_dir / "fronteira_ranking_topsis.png", dpi=150)
plt.close()

print("Figuras estilo TD_ENTREGA2 salvas em outputs/")

# =============================================================================
# Figuras originais do script
# =============================================================================

# Figura 1: Fronteira de Pareto com solução escolhida (requisito f)
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Gráfico 1: Tempo vs Distância
ax1 = axes[0]
ax1.scatter(
    df_analise['distancia'],
    df_analise['tempo'],
    alpha=0.6,
    s=80,
    c='lightblue',
    edgecolors='black',
    linewidth=0.5,
    label='Soluções da Fronteira',
)
ax1.scatter(
    solucao_final['distancia'],
    solucao_final['tempo'],
    color='red',
    s=300,
    marker='*',
    edgecolors='darkred',
    linewidth=2,
    label='Solução Escolhida',
    zorder=5,
)
ax1.set_xlabel('Distância Total (km)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Tempo Total (horas)', fontsize=12, fontweight='bold')
ax1.set_title('Fronteira de Pareto - Distância vs Tempo', fontsize=14, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# Gráfico 2: Alta Velocidade vs Balanceamento
ax2 = axes[1]
ax2.scatter(
    df_analise['alta_velocidade'],
    df_analise['balanceamento'],
    alpha=0.6,
    s=80,
    c='lightgreen',
    edgecolors='black',
    linewidth=0.5,
    label='Soluções da Fronteira',
)
ax2.scatter(
    solucao_final['alta_velocidade'],
    solucao_final['balanceamento'],
    color='red',
    s=300,
    marker='*',
    edgecolors='darkred',
    linewidth=2,
    label='Solução Escolhida',
    zorder=5,
)
ax2.set_xlabel('Trechos com Alta Velocidade (>80 km/h)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Balanceamento (Desvio Padrão)', fontsize=12, fontweight='bold')
ax2.set_title('Fronteira de Pareto - Alta Velocidade vs Balanceamento', fontsize=14, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / "figura_fronteira_solucao.png", dpi=150, bbox_inches='tight')
plt.close()

# Figura 2: Visualização 3D da fronteira
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')

scatter = ax.scatter(
    df_analise['distancia'],
    df_analise['tempo'],
    df_analise['alta_velocidade'],
    alpha=0.6,
    s=60,
    c=df_analise['balanceamento'],
    cmap='viridis',
    edgecolors='black',
    linewidth=0.3,
)

ax.scatter(
    solucao_final['distancia'],
    solucao_final['tempo'],
    solucao_final['alta_velocidade'],
    color='red',
    s=400,
    marker='*',
    edgecolors='darkred',
    linewidth=2,
    label='Solução Escolhida',
)

ax.set_xlabel('Distância (km)', fontsize=11, fontweight='bold')
ax.set_ylabel('Tempo (horas)', fontsize=11, fontweight='bold')
ax.set_zlabel('Alta Velocidade', fontsize=11, fontweight='bold')
ax.set_title('Fronteira de Pareto - Visualização 3D\n(Cor = Balanceamento)', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)

plt.colorbar(scatter, ax=ax, label='Balanceamento', shrink=0.8)
plt.savefig(output_dir / "figura_fronteira_3d.png", dpi=150, bbox_inches='tight')
plt.close()

# Figura 3: Características da solução final (requisito g)
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Gráfico 1: Valores dos atributos
ax1 = axes[0, 0]
atributos_nomes = ['Tempo\n(horas)', 'Distância\n(km)', 'Alta Veloc.\n(trechos)', 'Balanc.\n(desv. pad.)']
valores = [
    solucao_final['tempo'],
    solucao_final['distancia'],
    solucao_final['alta_velocidade'],
    solucao_final['balanceamento'],
]

cores = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71']
barras = ax1.bar(atributos_nomes, valores, color=cores, alpha=0.7, edgecolor='black', linewidth=1.5)
ax1.set_ylabel('Valor', fontsize=12, fontweight='bold')
ax1.set_title('Valores dos Atributos da Solução Escolhida', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='y')

for barra, valor in zip(barras, valores):
    altura = barra.get_height()
    ax1.text(
        barra.get_x() + barra.get_width() / 2.0,
        altura,
        f'{valor:.2f}' if valor < 100 else f'{valor:.0f}',
        ha='center',
        va='bottom',
        fontsize=10,
        fontweight='bold',
    )

# Gráfico 2: Radar chart (perfil normalizado)
ax2 = plt.subplot(2, 2, 2, projection='polar')

valores_max = [df_analise[c].max() for c in criterios_minimizacao]
valores_min = [df_analise[c].min() for c in criterios_minimizacao]

valores_norm = []
for valor, vmax, vmin in zip(valores, valores_max, valores_min):
    if vmax > vmin:
        norm = 1 - (valor - vmin) / (vmax - vmin)  # Inverter: menor = melhor = 1
    else:
        norm = 0.5
    valores_norm.append(norm)

valores_norm += valores_norm[:1]
angulos = [n / float(len(atributos_nomes)) * 2 * pi for n in range(len(atributos_nomes))]
angulos += angulos[:1]

ax2.plot(angulos, valores_norm, 'o-', linewidth=2, color='red', label='Solução Escolhida')
ax2.fill(angulos, valores_norm, alpha=0.25, color='red')
ax2.set_xticks(angulos[:-1])
ax2.set_xticklabels(atributos_nomes, fontsize=10)
ax2.set_ylim(0, 1)
ax2.set_title('Perfil Normalizado\n(1 = melhor, 0 = pior)', fontsize=12, fontweight='bold', pad=20)
ax2.grid(True)

# Gráfico 3: Comparação com média da fronteira
ax3 = axes[1, 0]
valores_media = [
    df_analise['tempo'].mean(),
    df_analise['distancia'].mean(),
    df_analise['alta_velocidade'].mean(),
    df_analise['balanceamento'].mean(),
]

x = np.arange(len(atributos_nomes))
width = 0.35

barras1 = ax3.bar(x - width/2, valores, width, label='Solução Escolhida', color='red', alpha=0.7, edgecolor='black')
barras2 = ax3.bar(x + width/2, valores_media, width, label='Média da Fronteira', color='lightblue', alpha=0.7, edgecolor='black')

ax3.set_ylabel('Valor', fontsize=12, fontweight='bold')
ax3.set_title('Comparação: Solução Escolhida vs Média', fontsize=13, fontweight='bold')
ax3.set_xticks(x)
ax3.set_xticklabels(atributos_nomes, fontsize=9)
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3, axis='y')

# Gráfico 4: Distribuição dos scores
ax4 = axes[1, 1]
ax4.scatter(
    df_analise['Score_AHP'],
    df_analise['Score_TOPSIS'],
    alpha=0.6,
    s=80,
    c='lightblue',
    edgecolors='black',
    linewidth=0.5,
    label='Soluções da Fronteira',
)
ax4.scatter(
    solucao_final['Score_AHP'],
    solucao_final['Score_TOPSIS'],
    color='red',
    s=300,
    marker='*',
    edgecolors='darkred',
    linewidth=2,
    label='Solução Escolhida',
    zorder=5,
)
ax4.set_xlabel('Score AHP (menor = melhor)', fontsize=11, fontweight='bold')
ax4.set_ylabel('Score TOPSIS (maior = melhor)', fontsize=11, fontweight='bold')
ax4.set_title('Distribuição dos Scores', fontsize=13, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / "figura_solucao_final.png", dpi=150, bbox_inches='tight')
plt.close()

# %%
# =============================================================================
# 8. RESUMO FINAL
# =============================================================================

print("\n" + "=" * 80)
print("RESUMO FINAL DA ANÁLISE")
print("=" * 80)

print(f"\n{'Atributo':<30} {'Solução':<15} {'Média':<15} {'Comparação':<20}")
print("-" * 80)

atributos_print = ['Tempo (horas)', 'Distância (km)', 'Alta Velocidade', 'Balanceamento']
for attr, valor, media in zip(atributos_print, valores, valores_media):
    diff = valor - media
    diff_pct = (diff / media * 100) if media > 0 else 0
    comparacao = f"{diff:+.2f} ({diff_pct:+.1f}%)"
    print(f"{attr:<30} {valor:<15.2f} {media:<15.2f} {comparacao:<20}")

print("=" * 80)

print("\nFiguras salvas em outputs/:")
print("  - fronteira_metodos.png (estilo TD_ENTREGA2)")
print("  - fronteira_ranking_topsis.png (estilo TD_ENTREGA2)")
print("  - figura_fronteira_solucao.png")
print("  - figura_fronteira_3d.png")
print("  - figura_solucao_final.png")

# Salvar resultados em CSV
df_analise.to_csv(output_dir / 'resultados_decisao.csv', index=False)
print("\nResultados salvos em: outputs/resultados_decisao.csv")