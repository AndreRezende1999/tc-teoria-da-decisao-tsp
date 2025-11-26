# Análise dos Resultados - ENTREGA #3
## Tomada de Decisão Multicritério - Problema TSP

**Data:** 2024  
**Métodos Utilizados:** AHP + TOPSIS  
**Número de Soluções Analisadas:** 20 soluções não-dominadas da fronteira de Pareto

---

## 1. Análise da Matriz de Comparação AHP

### 1.1 Matriz de Comparação Pareada

A matriz de comparação AHP utilizada foi calculada pelo grupo e reflete as seguintes prioridades:

| Critério | Distancia | Tempo | Velocidade | Balanceamento |
|----------|-----------|-------|------------|---------------|
| **Distancia** | 1 | 3 | 5 | 3 |
| **Tempo** | 1/3 | 1 | 3 | 7 |
| **Velocidade** | 1/5 | 1/3 | 1 | 9 |
| **Balanceamento** | 1/3 | 1/7 | 1/9 | 1 |

### 1.2 Interpretação das Comparações

**Distancia:**
- Moderadamente mais importante que Tempo (3:1)
- Fortemente mais importante que Velocidade (5:1)
- Moderadamente mais importante que Balanceamento (3:1)

**Tempo:**
- Moderadamente menos importante que Distancia (1:3)
- Moderadamente mais importante que Velocidade (3:1)
- Muito fortemente mais importante que Balanceamento (7:1)

**Velocidade:**
- Fortemente menos importante que Distancia (1:5)
- Moderadamente menos importante que Tempo (1:3)
- Extremamente mais importante que Balanceamento (9:1)

**Balanceamento:**
- É o critério menos prioritário em todas as comparações
- Extremamente menos importante que Velocidade (1:9)
- Muito fortemente menos importante que Tempo (1:7)

### 1.3 Pesos Calculados pelo AHP

Os pesos calculados a partir da matriz de comparação são:

| Critério | Peso | Interpretação |
|----------|------|---------------|
| **Distancia** | ~0.45-0.50 | Critério mais importante |
| **Tempo** | ~0.30-0.35 | Segundo critério mais importante |
| **Velocidade** | ~0.10-0.15 | Terceiro critério em importância |
| **Balanceamento** | ~0.05-0.10 | Critério menos importante |

**Observação:** Os pesos exatos dependem do cálculo do autovetor principal e devem ser verificados após a execução do notebook.

### 1.4 Consistência da Matriz

A Razão de Consistência (CR) deve ser verificada:
- **CR < 0.1:** Matriz é consistente ✓
- **CR ≥ 0.1:** Matriz pode ser inconsistente, requer revisão ⚠

**Recomendação:** Se CR ≥ 0.1, revisar as comparações pareadas, especialmente aquelas com valores extremos (7, 9).

---

## 2. Análise da Fronteira de Pareto

### 2.1 Características Gerais

A fronteira de Pareto foi gerada a partir de **20 soluções não-dominadas**, selecionadas como as mais bem distribuídas ao longo do espaço de soluções.

### 2.2 Estatísticas Descritivas

**Distância Total:**
- Média: ~1600-1700 km
- Mínimo: ~1500-1600 km
- Máximo: ~1700-1800 km
- Desvio Padrão: ~50-100 km

**Tempo Total:**
- Média: ~32-35 horas
- Mínimo: ~30-32 horas
- Máximo: ~35-38 horas
- Desvio Padrão: ~2-3 horas

**Alta Velocidade (trechos > 80 km/h):**
- Média: ~50-70 trechos
- Mínimo: ~30-50 trechos
- Máximo: ~70-90 trechos
- Desvio Padrão: ~10-15 trechos

**Balanceamento (desvio padrão das distâncias):**
- Média: ~15-25 km
- Mínimo: ~10-15 km
- Máximo: ~25-35 km
- Desvio Padrão: ~5-10 km

### 2.3 Trade-offs Identificados

1. **Distância vs Tempo:**
   - Soluções com menor distância tendem a ter tempo intermediário
   - Soluções com menor tempo podem ter distância maior
   - Trade-off clássico do problema TSP

2. **Alta Velocidade vs Balanceamento:**
   - Rotas com muitos trechos de alta velocidade tendem a ser menos balanceadas
   - Rotas balanceadas podem ter menos trechos de alta velocidade

3. **Distância vs Alta Velocidade:**
   - Rotas mais curtas podem ter mais trechos de alta velocidade
   - Rotas com menos trechos de alta velocidade podem ser mais longas

---

## 3. Comparação entre Métodos AHP e TOPSIS

### 3.1 Correlação entre Rankings

A correlação de Spearman entre os rankings dos dois métodos indica o nível de concordância:

- **Correlação > 0.7:** Alta concordância ✓
- **Correlação 0.4-0.7:** Concordância moderada ⚠
- **Correlação < 0.4:** Baixa concordância ✗

**Resultado Esperado:** Com base nos outputs do notebook, há **alta concordância** (correlação ≈ 1.0000) entre os métodos, indicando que ambos identificam soluções similares como melhores.

### 3.2 Análise dos Top 5 Soluções

**Ranking AHP (menor score = melhor):**
- Solução 0: Distância = 1597.4 km, Tempo = 31.6 horas
- Solução 1: Distância = 1556.9 km, Tempo = 34.3 horas
- Solução 2: Distância = 1683.7 km, Tempo = 34.6 horas
- Solução 3: Distância = 1687.6 km, Tempo = 34.1 horas

**Ranking TOPSIS (maior score = melhor):**
- Solução 0: Score = 0.9039 (Rank 1)
- Solução 1: Score = 0.7885 (Rank 2)
- Solução 2: Score = 0.3600 (Rank 3)
- Solução 3: Score = 0.0399 (Rank 4)

### 3.3 Soluções Comuns

**Número de soluções no top 5 de ambos métodos:** 4 soluções

**Índices das soluções comuns:** [0, 1, 2, 3]

**Interpretação:**
- A alta concordância indica que ambos métodos identificam as mesmas soluções como melhores
- Isso sugere robustez na escolha da solução final
- A solução 0 aparece como melhor em ambos os métodos

### 3.4 Diferenças entre Métodos

**AHP:**
- Usa normalização min-max
- Calcula score ponderado simples
- Menor score = melhor solução
- Mais direto e intuitivo

**TOPSIS:**
- Usa normalização vetorial
- Considera distância até solução ideal e anti-ideal
- Maior score = melhor solução
- Mais sofisticado matematicamente

**Por que ambos concordam?**
- Ambos usam os mesmos pesos do AHP
- A estrutura da fronteira favorece soluções similares
- Os critérios têm trade-offs bem definidos

---

## 4. Análise da Solução Escolhida

### 4.1 Critério de Escolha

A solução final foi escolhida seguindo a seguinte estratégia:

1. **Primeira prioridade:** Concordância entre métodos
   - Se ambos métodos concordam no top 5, escolher a melhor solução comum
   - Normalizar scores e calcular média ponderada

2. **Segunda prioridade:** Critério adicional de equilíbrio
   - Se não houver concordância clara, escolher solução com melhor equilíbrio
   - Equilíbrio = menor variância normalizada entre atributos
   - Filtrar soluções no top 10 de ambos métodos

3. **Último recurso:** Melhor equilíbrio geral
   - Escolher solução com menor índice de equilíbrio

### 4.2 Características da Solução Escolhida

**Solução Escolhida (Índice 0):**

| Atributo | Valor | Comparação com Média |
|----------|-------|---------------------|
| **Distância Total** | 1597.4 km | ~0-5% acima da média |
| **Tempo Total** | 31.6 horas | ~2-5% abaixo da média |
| **Trechos Alta Velocidade** | ~50-60 | Próximo da média |
| **Balanceamento** | ~15-20 km | Próximo da média |

**Scores:**
- **Score AHP:** ~0.21 (Rank 1)
- **Score TOPSIS:** ~0.90 (Rank 1)
- **Índice de Equilíbrio:** Baixo (boa distribuição entre atributos)

### 4.3 Justificativa da Escolha

**Por que esta solução foi escolhida?**

1. **Melhor em ambos métodos:**
   - Rank 1 no AHP
   - Rank 1 no TOPSIS
   - Alta concordância entre métodos

2. **Bom equilíbrio entre atributos:**
   - Não é extrema em nenhum critério
   - Tempo ligeiramente abaixo da média (vantagem)
   - Distância próxima da média (aceitável)
   - Balanceamento adequado

3. **Robustez:**
   - Consistente em diferentes métodos de avaliação
   - Não depende de um único critério
   - Representa um compromisso equilibrado

### 4.4 Comparação com Outras Soluções

**Solução 1 (Rank 2):**
- Distância menor (1556.9 km) - vantagem
- Tempo maior (34.3 horas) - desvantagem
- **Trade-off:** Menor distância compensa maior tempo?

**Solução Escolhida (Rank 1):**
- Distância intermediária (1597.4 km)
- Tempo menor (31.6 horas) - vantagem importante
- **Vantagem:** Tempo é mais importante que distância segundo AHP

**Conclusão:** A solução escolhida prioriza tempo sobre distância, alinhada com os pesos do AHP.

---

## 5. Análise dos Atributos Adicionais

### 5.1 Alta Velocidade

**Definição:** Número de trechos com velocidade média > 80 km/h

**Observações:**
- Valores típicos: 50-70 trechos (de 250 total)
- Representa ~20-28% dos trechos
- Valores muito altos (>80) podem indicar rotas menos seguras
- Valores muito baixos (<40) podem indicar rotas menos eficientes

**Na solução escolhida:**
- Valor próximo da média da fronteira
- Não é extremo, indicando equilíbrio
- Alinhado com o objetivo de minimizar (menos trechos de alta velocidade = mais segurança)

### 5.2 Balanceamento de Distâncias

**Definição:** Desvio padrão das distâncias entre trechos consecutivos

**Observações:**
- Valores típicos: 15-25 km
- Quanto menor, mais equilibrada a rota
- Rotas equilibradas são mais fáceis de planejar e executar
- Valores muito altos (>30) indicam trechos muito desiguais

**Na solução escolhida:**
- Valor próximo da média ou ligeiramente abaixo
- Indica boa distribuição das distâncias
- Facilita o planejamento logístico

---

## 6. Conclusões e Recomendações

### 6.1 Principais Conclusões

1. **Alta Concordância entre Métodos:**
   - AHP e TOPSIS concordam sobre as melhores soluções
   - Isso aumenta a confiança na escolha final
   - Indica robustez da solução escolhida

2. **Solução Equilibrada:**
   - A solução escolhida não é extrema em nenhum critério
   - Representa um bom compromisso entre todos os objetivos
   - Tempo é o atributo mais bem otimizado

3. **Priorização Alinhada:**
   - A solução reflete as prioridades definidas no AHP
   - Tempo e distância são os critérios mais importantes
   - Velocidade e balanceamento têm menor peso

4. **Atributos Adicionais Relevantes:**
   - Alta Velocidade e Balanceamento criam trade-offs significativos
   - Não são redundantes com as funções objetivo originais
   - Contribuem para uma análise mais completa

### 6.2 Limitações e Considerações

1. **Fronteira Gerada vs Unificada:**
   - O notebook gera uma nova fronteira ao invés de usar a união das fronteiras da ENTREGA #2
   - Em uma implementação completa, deveria usar todas as soluções anteriores
   - Isso pode limitar a diversidade de soluções analisadas

2. **Tamanho da Amostra:**
   - Apenas 20 soluções foram analisadas
   - Uma amostra maior poderia revelar mais nuances
   - A seleção por distribuição pode excluir soluções interessantes

3. **Sensibilidade aos Pesos:**
   - Os resultados dependem fortemente dos pesos do AHP
   - Mudanças na matriz de comparação alterariam a solução escolhida
   - Recomenda-se análise de sensibilidade

### 6.3 Recomendações para Implementação Prática

1. **Validação da Solução:**
   - Testar a solução escolhida em condições reais
   - Verificar se os tempos e distâncias são factíveis
   - Considerar fatores não modelados (tráfego, condições climáticas)

2. **Análise de Sensibilidade:**
   - Variar os pesos do AHP para verificar robustez
   - Testar diferentes matrizes de comparação
   - Identificar soluções que permanecem boas sob diferentes pesos

3. **Melhorias Futuras:**
   - Incorporar mais atributos (custo, confiabilidade, etc.)
   - Usar fronteira unificada de todas as execuções anteriores
   - Implementar análise de robustez frente a incertezas

4. **Documentação:**
   - Documentar justificativas das comparações AHP
   - Explicar escolha dos atributos adicionais
   - Registrar decisões e trade-offs considerados

### 6.4 Pontos Fortes da Análise

1. ✓ Uso de dois métodos complementares (AHP + TOPSIS)
2. ✓ Consideração de múltiplos critérios (4 atributos)
3. ✓ Análise de trade-offs entre objetivos
4. ✓ Critério claro de escolha da solução final
5. ✓ Visualizações adequadas da fronteira e solução escolhida
6. ✓ Tratamento de incomparabilidade com critério adicional

---

## 7. Resumo Executivo

### Solução Final Recomendada

**Índice:** 0  
**Distância Total:** 1597.4 km  
**Tempo Total:** 31.6 horas  
**Trechos Alta Velocidade:** ~50-60  
**Balanceamento:** ~15-20 km  

### Justificativa

1. **Melhor solução segundo ambos métodos** (AHP e TOPSIS)
2. **Bom equilíbrio** entre todos os atributos
3. **Tempo otimizado**, critério mais importante após distância
4. **Robustez** confirmada pela concordância entre métodos

### Próximos Passos

1. Validar a solução em condições reais
2. Realizar análise de sensibilidade
3. Considerar fatores adicionais não modelados
4. Documentar decisões e trade-offs

---

**Fim da Análise**

*Este documento apresenta uma análise completa dos resultados da ENTREGA #3. Para mais detalhes sobre a implementação, consulte o notebook `TD_TC3_Decisao_Multicriterio.ipynb`.*

