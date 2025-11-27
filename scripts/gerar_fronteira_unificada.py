"""
Script para unificar as fronteiras PE e PW e gerar atributos adicionais.
"""

import numpy as np
import pandas as pd

np.random.seed(42)

# Carregar dados das fronteiras
df_pe = pd.read_csv('data/fronteira_pe.csv')
df_pw = pd.read_csv('data/fronteira_pw.csv')

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

print(f"Total de soluções: {len(df_unificado)}")
print(f"  - Epsilon-restrito: {len(df_pe)}")
print(f"  - Soma ponderada: {len(df_pw)}")

# Gerar atributos adicionais de forma correlacionada mas conflitante
# Alta_Velocidade: correlação positiva com velocidade média (dist/tempo)
# - Rotas mais rápidas tendem a ter mais trechos de alta velocidade
velocidade_media = df_unificado['distancia'] / df_unificado['tempo']
vel_norm = (velocidade_media - velocidade_media.min()) / (velocidade_media.max() - velocidade_media.min())

# Alta_Velocidade: entre 20 e 120 trechos, correlacionado com velocidade média
# Maior velocidade média -> mais trechos de alta velocidade
base_alta_vel = 20 + vel_norm * 80
ruido = np.random.normal(0, 10, len(df_unificado))
df_unificado['alta_velocidade'] = np.clip(base_alta_vel + ruido, 10, 130).astype(int)

# Balanceamento: desvio padrão das distâncias entre trechos
# Conflito: rotas mais curtas tendem a ter menos balanceamento (mais variação)
# Rotas com menor distância total -> maior desbalanceamento
dist_norm = (df_unificado['distancia'] - df_unificado['distancia'].min()) / \
            (df_unificado['distancia'].max() - df_unificado['distancia'].min())

# Balanceamento: entre 5 e 25, inversamente correlacionado com distância
# Menor distância -> maior desbalanceamento (maior desvio padrão)
base_balanceamento = 25 - dist_norm * 15
ruido_bal = np.random.normal(0, 2, len(df_unificado))
df_unificado['balanceamento'] = np.clip(base_balanceamento + ruido_bal, 5, 30)

# Arredondar valores
df_unificado['balanceamento'] = df_unificado['balanceamento'].round(2)
df_unificado['tempo'] = df_unificado['tempo'].round(2)
df_unificado['distancia'] = df_unificado['distancia'].round(2)

# Reorganizar colunas
df_unificado = df_unificado[['id', 'metodo', 'repeticao', 'tempo', 'distancia',
                             'alta_velocidade', 'balanceamento', 'parametro']]

# Salvar arquivo unificado
df_unificado.to_csv('data/fronteira_unificada.csv', index=False)

print("\nArquivo salvo: data/fronteira_unificada.csv")
print("\nEstatísticas dos atributos:")
print(df_unificado[['tempo', 'distancia', 'alta_velocidade', 'balanceamento']].describe())

print("\nVerificação de conflitos (correlações):")
print("  Tempo vs Distância:", df_unificado['tempo'].corr(df_unificado['distancia']).round(3))
print("  Tempo vs Alta_Velocidade:", df_unificado['tempo'].corr(df_unificado['alta_velocidade']).round(3))
print("  Tempo vs Balanceamento:", df_unificado['tempo'].corr(df_unificado['balanceamento']).round(3))
print("  Distância vs Alta_Velocidade:", df_unificado['distancia'].corr(df_unificado['alta_velocidade']).round(3))
print("  Distância vs Balanceamento:", df_unificado['distancia'].corr(df_unificado['balanceamento']).round(3))
print("  Alta_Velocidade vs Balanceamento:", df_unificado['alta_velocidade'].corr(df_unificado['balanceamento']).round(3))

print("\nPrimeiras linhas do arquivo:")
print(df_unificado.head(10))