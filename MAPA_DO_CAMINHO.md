# Mapa do Caminho Esperado: Tomada de Decisão Multicritério no TSP

Este documento descreve o plano de implementação para a resolução do Problema do Caixeiro Viajante (TSP) Multiobjetivo, integrando a geração de soluções na fronteira de Pareto com métodos de tomada de decisão multicritério (AHP e TOPSIS).

## 1. Contextualização do Problema

O objetivo é determinar uma rota que visite 250 cidades exatamente uma vez e retorne à origem, otimizando múltiplos objetivos conflitantes.

### Atributos de Decisão
Para esta etapa, serão considerados quatro atributos para avaliar a qualidade das rotas:

1.  **Distância Total ($f_D$)**: Soma das distâncias de todos os trechos (Minimizar).
2.  **Tempo Total ($f_T$)**: Soma dos tempos de todos os trechos (Minimizar).
3.  **Alta Velocidade (Novo)**:
    *   **Definição**: Quantidade de trechos onde a velocidade média ($v_{ij} = d_{ij}/t_{ij}$) excede um limite crítico (ex: 80 km/h).
    *   **Objetivo**: Minimizar (maior segurança e conformidade).
4.  **Balanceamento de Distâncias (Novo)**:
    *   **Definição**: Desvio padrão das distâncias dos trechos da rota.
    *   **Objetivo**: Minimizar (rotas mais homogêneas e previsíveis).

---

## 2. Metodologia de Implementação

O processo será dividido em três fases principais: Geração de Soluções, Aplicação de Métodos Multicritério e Análise de Resultados.

### Fase 1: Geração da Fronteira de Pareto

Nesta fase, o algoritmo de otimização (GVNS) será executado para encontrar um conjunto de soluções eficientes (não-dominadas).

*   **Estratégia**: Executar o GVNS múltiplas vezes variando os pesos ($w_d, w_t$) da função objetivo agregada ($f = w_d \cdot f_D + w_t \cdot f_T$).
*   **Cálculo de Atributos**: Para cada solução gerada, calcular os 4 atributos definidos acima.
*   **Filtragem**: Identificar e manter apenas as soluções não-dominadas (Fronteira de Pareto), onde nenhuma outra solução é melhor em todos os critérios simultaneamente.

### Fase 2: Tomada de Decisão (AHP + TOPSIS)

Para selecionar a melhor solução dentre as opções da fronteira, será utilizado um método híbrido combinando AHP (para pesos) e TOPSIS (para ranking).

#### Passo 2.1: Determinação dos Pesos (AHP)
Utilizar o *Analytic Hierarchy Process* (AHP) para definir a importância relativa de cada critério.
1.  **Matriz de Comparação**: Definir a importância relativa entre pares de critérios (ex: Distância é mais importante que Tempo?).
2.  **Cálculo dos Pesos**: Extrair o autovetor principal da matriz para obter os pesos normalizados ($w_{AHP}$).
3.  **Verificação**: Calcular a Razão de Consistência (CR) para validar os julgamentos.

#### Passo 2.2: Ranking das Alternativas (TOPSIS)
Utilizar o *Technique for Order of Preference by Similarity to Ideal Solution* (TOPSIS) para ordenar as soluções.
1.  **Normalização**: Normalizar a matriz de decisão (valores dos atributos das soluções da fronteira) para tornar as escalas comparáveis (normalização vetorial).
2.  **Ponderação**: Multiplicar a matriz normalizada pelos pesos obtidos no AHP ($v_{ij} = w_j \cdot r_{ij}$).
3.  **Soluções de Referência**:
    *   **Ideal ($A^+$)**: Melhor valor encontrado para cada critério (Mínimo para todos).
    *   **Anti-Ideal ($A^-$)**: Pior valor encontrado para cada critério (Máximo para todos).
4.  **Cálculo de Distâncias**: Calcular a distância Euclidiana de cada solução para $A^+$ e $A^-$.
5.  **Score TOPSIS**: Calcular o índice de proximidade:
    $$C_i = \frac{D_i^-}{D_i^+ + D_i^-}$$
    Onde $D_i^+$ é a distância para o ideal e $D_i^-$ é a distância para o anti-ideal.

### Fase 3: Seleção e Visualização

*   **Seleção Final**: Escolher a solução com maior Score TOPSIS (ou uma solução de consenso entre AHP e TOPSIS).
*   **Visualização 1 (Fronteira)**: Plotar a fronteira de Pareto (ex: Distância x Tempo) destacando a solução escolhida.
*   **Visualização 2 (Perfil)**: Criar gráficos (Radar ou Barras) comparando os atributos da solução escolhida com a média das outras soluções, ilustrando suas vantagens e trade-offs.

---

## 3. Estrutura do Código (Notebook)

O notebook `TD_TC3_Decisao_Multicriterio.ipynb` deve seguir esta estrutura lógica:

1.  **Setup**: Importação de bibliotecas e carregamento dos dados (`distancia.csv`, `tempo.csv`).
2.  **Funções de Atributos**: Implementação de `calcular_alta_velocidade` e `calcular_balanceamento`.
3.  **Loop de Otimização**: Geração de soluções variando pesos e coleta de dados.
4.  **Processamento da Fronteira**: Filtragem de não-dominadas.
5.  **Implementação AHP**: Definição da matriz de preferências e cálculo de pesos.
6.  **Implementação TOPSIS**: Cálculo dos scores e ranking.
7.  **Análise**: Comparação de rankings e escolha da solução final.
8.  **Plots**: Geração das figuras solicitadas para o relatório.
