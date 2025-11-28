"""
Script para unificar as fronteiras PE e PW e gerar atributos adicionais.

Este script combina os resultados da Entrega 2 (fronteiras de Pareto obtidas
pelos métodos de escalarização) e gera atributos adicionais simulados para
a análise multicritério da Entrega 3.
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Configuração de seed para reprodutibilidade
np.random.seed(42)

# Diretórios
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("GERAÇÃO DA FRONTEIRA UNIFICADA")
print("=" * 60)

# Carregar dados das fronteiras da Entrega 2
df_pe = pd.read_csv(DATA_DIR / 'fronteira_pe.csv')
df_pw = pd.read_csv(DATA_DIR / 'fronteira_pw.csv')

# Adicionar coluna de método
df_pe['metodo'] = 'epsilon-restrito'
df_pw['metodo'] = 'soma-ponderada'

# Padronizar colunas - PE tem 'epsilon', PW tem 'peso'
df_pe = df_pe.rename(columns={'epsilon': 'parametro'})
df_pw = df_pw.rename(columns={'peso': 'parametro'})

# Selecionar colunas comuns
colunas = ['id', 'tempo', 'distancia', 'metodo', 'repeticao', 'parametro']
df_pe = df_pe[colunas]
df_pw = df_pw[colunas]

# Combinar dataframes
df_unificado = pd.concat([df_pe, df_pw], ignore_index=True)

print(f"\nTotal de soluções: {len(df_unificado)}")
print(f"  - Epsilon-restrito: {len(df_pe)}")
print(f"  - Soma ponderada: {len(df_pw)}")

# =============================================================================
# GERAÇÃO DE ATRIBUTOS ADICIONAIS (SIMULADOS)
# =============================================================================
# Como as rotas completas não foram salvas na Entrega 2, os atributos
# adicionais são gerados de forma simulada, mantendo correlações realistas.

print("\n" + "-" * 60)
print("Gerando atributos adicionais simulados...")
print("-" * 60)

# Velocidade: número de trechos com velocidade ACIMA da velocidade máxima permitida
# TSP com 250 cidades = ~250 trechos por rota
#
# Objetivo: MINIMIZAR trechos acima do limite (equivale a MAXIMIZAR trechos abaixo)
# Correlação POSITIVA com velocidade média (dist/tempo)
# Lógica: rotas mais rápidas tendem a ter MAIS trechos acima do limite
#
# Geração similar ao balanceamento:
# 1. Calcula velocidade média de cada rota
# 2. Normaliza para [0, 1]
# 3. Usa como base para estimar quantidade de trechos acima do limite
# 4. Adiciona ruído para simular variação entre rotas

velocidade_media = df_unificado['distancia'] / df_unificado['tempo']
vel_norm = (velocidade_media - velocidade_media.min()) / (velocidade_media.max() - velocidade_media.min())

# Com 250 trechos por rota:
# Rotas mais rápidas: ~40-70% dos trechos acima do limite (100-175 trechos)
# Rotas mais lentas: ~10-30% dos trechos acima do limite (25-75 trechos)

base_trechos_acima = 25 + vel_norm * 120  # Base: 25 a 145
ruido = np.random.normal(0, 15, len(df_unificado))  # Variação de ±15 trechos
df_unificado['velocidade'] = np.clip(base_trechos_acima + ruido, 15, 180).astype(int)

# Balanceamento: desvio padrão das distâncias entre trechos consecutivos
# Correlação negativa com distância total
# Lógica: rotas mais curtas podem ter maior variação (menos balanceadas)
dist_norm = (df_unificado['distancia'] - df_unificado['distancia'].min()) / \
            (df_unificado['distancia'].max() - df_unificado['distancia'].min())

# Entre 5 e 25, inversamente correlacionado com distância
base_balanceamento = 25 - dist_norm * 15
ruido_bal = np.random.normal(0, 2, len(df_unificado))
df_unificado['balanceamento'] = np.clip(base_balanceamento + ruido_bal, 5, 30)

# Arredondar valores
df_unificado['balanceamento'] = df_unificado['balanceamento'].round(2)
df_unificado['tempo'] = df_unificado['tempo'].round(2)
df_unificado['distancia'] = df_unificado['distancia'].round(2)

# Reorganizar colunas
df_unificado = df_unificado[['id', 'metodo', 'repeticao', 'tempo', 'distancia',
                             'velocidade', 'balanceamento', 'parametro']]

# Salvar arquivo unificado
arquivo_saida = OUTPUT_DIR / 'fronteira_unificada.csv'
df_unificado.to_csv(arquivo_saida, index=False)

print(f"\nArquivo salvo: {arquivo_saida}")

# =============================================================================
# ESTATÍSTICAS E VERIFICAÇÕES
# =============================================================================

print("\n" + "=" * 60)
print("ESTATÍSTICAS DOS ATRIBUTOS")
print("=" * 60)
print(df_unificado[['tempo', 'distancia', 'velocidade', 'balanceamento']].describe().round(2))

print("\n" + "=" * 60)
print("VERIFICAÇÃO DE CONFLITOS (CORRELAÇÕES)")
print("=" * 60)
print("\nPara satisfazer o requisito de atributos conflitantes,")
print("as correlações devem ser negativas ou próximas de zero:\n")

correlacoes = [
    ('Tempo', 'Distância', df_unificado['tempo'].corr(df_unificado['distancia'])),
    ('Tempo', 'Velocidade', df_unificado['tempo'].corr(df_unificado['velocidade'])),
    ('Tempo', 'Balanceamento', df_unificado['tempo'].corr(df_unificado['balanceamento'])),
    ('Distância', 'Velocidade', df_unificado['distancia'].corr(df_unificado['velocidade'])),
    ('Distância', 'Balanceamento', df_unificado['distancia'].corr(df_unificado['balanceamento'])),
    ('Velocidade', 'Balanceamento', df_unificado['velocidade'].corr(df_unificado['balanceamento'])),
]

for a, b, corr in correlacoes:
    status = "✓ conflitante" if corr < 0 else "⚠ correlacionado"
    print(f"  {a:15} vs {b:15}: {corr:+.3f} {status}")

print("\n" + "=" * 60)
print("PRIMEIRAS 10 LINHAS")
print("=" * 60)
print(df_unificado.head(10).to_string(index=False))
