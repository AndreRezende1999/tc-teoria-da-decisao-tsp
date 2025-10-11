# Teoria da Decisão - Trabalho Computacional: Travelling Salesman Problem (TSP)

Este trabalho tem por intuito abordar, de forma conjunta, os principais conceitos vistos na disciplina ELE088 - Teoria da Decisão. O aluno deverá compreender o problema, discutir e apresentar algoritmos para a sua solução, realizar experimentos computacionais e analisar os resultados obtidos. Ao final, o aluno deverá indicar qual ação (solução) final seria implementada na prática, usando métodos de auxílio a tomada de decisão multiatributo.

## Especificação do Problema: Travelling Salesman Problem (TSP)

O Problema do Caixeiro Viajante (PCV) tem por objetivo determinar a rota que percorre uma série de cidades (visitando uma única vez cada uma delas), retornando à cidade de origem, com o menor custo possível.

No caso específico deste trabalho, considera-se uma variante multiobjetivo do problema: deseja-se minimizar o tempo (em horas) e a distância (em km) para, saindo da cidade 1, visitar outras 249 cidades e retornar à cidade 1 para concluir a rota.

### Apresentação da Instância:

A instância considerada possui 250 cidades:
* **Tempos entre cidades:** Podem ser encontrados no arquivo `tempo.csv`. O arquivo possui 250 linhas e 250 colunas, onde o valor na linha `i`/coluna `j` é o tempo (em horas) necessário para alcançar a cidade `j` a partir da cidade `i`.
* **Distâncias entre cidades:** Podem ser encontradas no arquivo `distancia.csv`. O arquivo possui 250 linhas e 250 colunas, onde o valor na linha `i`/coluna `j` é a distância (em km) entre a cidade `i` e a cidade `j`.

---

## ENTREGA #1: MODELAGEM MATEMÁTICA E OTIMIZAÇÃO MONO-OBJETIVO

### i. Formulação

**(a) Parâmetros do problema:**

* **n:** número de cidades (n=250)
* **Índices i, j:** i, j ∈ {1, ..., n}, i, j ∈ N
* **$t_{ij}$:** tempo (em horas) para ir da cidade i para a cidade j
* **$d_{ij}$:** distância (em km) para ir da cidade i para a cidade j

**(b) Variáveis do problema:**

Deve-se encontrar:
* **$x_{ij}$** para todo i, j, sendo $x_{ij} \in \{0,1\}$:
    * $x_{ij} = 1$ se a rota utiliza a aresta $i \rightarrow j$
    * $x_{ij} = 0$, caso contrário
* **Variáveis auxiliares $u_{i}$** para a restrição que garante a eliminação de subciclos: $u_{i}$ para i=1,...,n, sendo $u_{1}=1$ e $2 \le u_{i} \le n$ para $i \ge 2$.

**(c) Modelo da função objetivo $f1(\cdot)$:**

A primeira função objetivo é $f_{T}$ que determina o tempo total gasto na rota:
$f_{T} = \sum_{i=1}^{n} \sum_{j=1}^{n} t_{ij} \cdot x_{ij}$

**(d) Modelo da função objetivo $f2(\cdot)$:**

A segunda função objetivo é $f_{D}$ que determina a distância total gasta na rota:
$f_{D} = \sum_{i=1}^{n} \sum_{j=1}^{n} d_{ij} \cdot x_{ij}$

**(e) Modelo das restrições:**

1.  **Deve-se entrar em cada cidade exatamente 1 vez:**
    $\\sum_{i=1}^{n} x_{ij} = 1, \\forall j \\in \\{1, ..., n\}$
2.  **Deve-se sair de cada cidade exatamente 1 vez:**
    $\\sum_{j=1}^{n} x_{ij} = 1, \\forall i \\in \\{1, ..., n\}$
3.  **A rota encontrada na solução deve ser uma única rota fechada que visita todas as cidades, ou seja, a solução não deve conter subciclos.**
    Definindo $u_{1}=1$ e $2 \le u_{i} \le n$ para $i \in \{2, ..., n\}$, então:
    $u_{i} - u_{j} + n \cdot x_{ij} \le n-1, \\forall i, j \\in \\{2, ..., n\}$

### ii. Algoritmo de solução

A metaheurística utilizada é uma adaptação do **GVNS (General Variable Neighborhood Search)**, muito utilizada para o Problema do Caixeiro Viajante. A ideia é simples: começa-se criando uma rota razoável. Então, faz-se uma perturbação pequena e evolui-se para a média e a grande quando não se obtém resultados satisfatórios. Depois da perturbação, usa-se o VND para refinar a solução encontrada. Se o método não evoluir a solução por muito tempo, faz-se uma perturbação grande e recomeça-se. A adaptação utilizada reconhece a vizinhança que traz os melhores resultados e prioriza a busca nela.

**Algoritmo GVNS-TSP**
```
1: procedimento AM-GVNS (C, N, kmax, Tmax)
2:   S ← Construtivo-Guloso-Aleatorizado (C, N)  ▷ solução inicial
3:   S ← VND(S) ▷ refina a solução inicial
4:   S* ← S ▷ melhor solução até agora
5:   tempo ← 0
6:   enquanto tempo < Tmax fazer
7:     k ← 1
8:     enquanto k ≤ kmax fazer
9:       S' ← Shaking(S, k) ▷ perturba a solução em vizinhança k
10:      S' ← VND(S') ▷ aplica busca local em S'
11:      se f(S') < f(S*) então
12:        S* ← S'
13:        S ← S'
14:        k ← 1 ▷ reinicia vizinhança
15:      senão
16:        k ← k + 1 ▷ tenta vizinhança mais forte
17:      fim se
18:    fim enquanto
19:    tempo ← tempo + 1
20:  fim enquanto
21:  retornar S*
22: fim procedimento
```

**Algoritmo VND**
```
1: procedimento VND (S)
2:   l ← 1
3:   enquanto l ≤ lmax fazer
4:     selecione o caso (l)
5:       caso (1): S' ← 2-Opt(S) ▷ vizinhança fraca
6:       caso (2): S' ← Or-Opt(S) ▷ vizinhança média
7:       caso (3): S' ← Double-Bridge(S) ▷ vizinhança forte
8:     fim selecionar
9:     se f(S') < f(S) então
10:      S ← S'
11:      l ← 1 ▷ volta para primeira vizinhança
12:    senão
13:      l ← l + 1
14:    fim se
15:  fim enquanto
16:  retornar S
17: fim procedimento
```

**Algoritmo Construtivo-Guloso-Aleatorizado**
```
1: procedimento CONSTRUTIVO (C, N)
2:   escolha uma cidade inicial aleatória
3:   S ← [cidade_inicial]
4:   não_visitadas ← {todas as outras cidades}
5:   enquanto não_visitadas ≠ ø fazer
6:     calcule custos de inserção para cada cidade em não_visitadas
7:     RCL ← top r melhores opções
8:     escolha uma cidade c ∈ RCL aleatoriamente
9:     insira c em S na melhor posição
10:    remova c de não_visitadas
11:  fim enquanto
12:  retornar S
13: fim procedimento
```

**(a) Variação da metaheurística:**

A metaheurística utilizada é uma adaptação do **GVNS (General Variable Neighborhood Search)**, muito utilizada para o Problema do Caixeiro Viajante. A ideia é simples: começa-se criando uma rota razoável. Então, faz-se uma perturbação pequena e evolui-se para a média e a grande quando não se obtém resultados satisfatórios. Depois da perturbação, usa-se o VND para refinar a solução encontrada. Se o método não evoluir a solução por muito tempo, faz-se uma perturbação grande e recomeça-se. A adaptação utilizada reconhece a vizinhança que traz os melhores resultados e prioriza a busca nela.

**(b) Modelagem computacional da solução:**

* O tour (rota escolhida) será representado como uma lista ou array de n-1 posições, onde o índice `i` mostra qual é a i-ésima cidade a ser visitada.
* O custo será representado em uma matriz $n \times n$ onde o valor da linha `i` coluna `j` é o custo, em tempo ou distância, da cidade `i` para a cidade `j`.

**(c) Estruturas de vizinhança:**

* **Vizinhança fraca: 2-opt.** Faz a troca de arestas, por exemplo (a, b) e (c, d) viram (a, c) e (b, d). É uma pequena mudança, ideal para refinamentos finais.
* **Vizinhança média: Or-opt.** Remove um bloco pequeno de arestas e o coloca em outra posição.
* **Vizinhança forte: double-bridge.** Corta a rota em quatro pedaços e os reconecta em uma ordem diferente. Ideal para grandes mudanças, quando a busca local não oferece melhora.

**(d) Heurística construtiva:**

Para encontrar a solução inicial, começa-se escolhendo uma cidade aleatória. Então, acrescentam-se cidades na rota usando opções que, a princípio, parecem boas, como as cidades mais próximas. A escolha da próxima cidade é feita a partir de uma lista de melhores candidatas com poucas opções, dando um toque de aleatoriedade na construção inicial. Geram-se M soluções iniciais e escolhe-se a melhor.

**(e) Estratégia de refinamento:**

Será utilizado o **VND** como refinador para cada vizinhança. As vizinhanças podem ser ordenadas a partir da taxa de sucesso delas (melhoras/tentativas), passando mais tempo nas vizinhanças mais promissoras.

### iii. Resultados da otimização mono-objetivo

O algoritmo foi executado 5 vezes para cada uma das funções e os resultados obtidos são apresentados abaixo.

| Função | Mínimo | Máximo | Desvio Padrão |
| :--- | :--- | :--- | :--- |
| Tempo | 79.5 | 98.9 | 7.59 |
| Distancia | 5083.7 | 7113.2 | 864.9 |

* **Resultados para Tempo:** A melhor execução (run 3) apresentou custo **79.5**.
* **Resultados para Distância:** A melhor execução (run 1) apresentou custo **5083.7**.

---

## ENTREGA #2: OTIMIZAÇÃO MULTIOBJETIVO

**(a) Apresente a modelagem matemática do problema considerando as abordagens escalares Soma Ponderada (Pw) e e-restrito (PE).**
**(b) Para cada uma das abordagens escalares, utilize o algoritmo apresentado no item (ii) para resolver o problema biobjetivo construído.**
**(c) Como o método é estocástico, ele deve ser executado 05 vezes considerando cada uma das abordagens escalares. Para cada uma das técnicas empregadas, as 05 fronteiras obtidas devem ser apresentadas sobrepostas em uma mesma figura.**
**(d) Cada fronteira estimada deve conter no máximo 20 soluções não-dominadas. Caso seja encontrado um maior número de soluções, escolha apenas as 20 soluções mais bem distribuídas ao longo da fronteira.**

---

## ENTREGA #3: TOMADA DE DECISÃO MULTICRITÉRIO

**(a) Empregue 02 métodos de auxílio à tomada de decisão para escolher a ação final a ser implementada (as opções são Abordagem Clássica, AHP, ELECTRE, PROMETHEE e TOPSIS).**
**(b) Compare os métodos escolhidos. Considere a fronteira não-dominada obtida a partir da união de todas as fronteiras estimadas. Caso essa fronteira tenha muitas soluções, selecione apenas as 20 soluções não-dominadas mais representativas.**
**(c) Assuma como critérios de decisão pelo menos quatro (04) atributos de interesse, i.e., as duas funções objetivo definidas no problema e pelo menos mais duas funções adicionais que considerar relevantes (e.g., confiabilidade da solução, robustez, etc.). Todos os atributos de decisão devem ser conflitantes.**
**(d) Os métodos de decisão utilizados devem ser apropriadamente definidos e apresentados.**
**(e) No caso de incomparabilidade entre alternativas no final do processo, estabeleça um critério adicional e tome sua decisão.**
**(f) Plote uma figura contendo a fronteira de soluções avaliadas na tomada de decisão e indique, nesta figura, qual(is) solução(ões) foi(foram) escolhida(s).**
**(g) Plote uma figura que represente a(s) solução(ões) final(is) escolhida(s), ilustrando suas principais características.**