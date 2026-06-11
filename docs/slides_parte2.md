# Otimizacao Evolutiva do Sistema Fuzzy
## Algoritmo Genetico e PSO — Parte 2

Inteligencia Artificial e Computacional (0700M8) — CESUPA 2026/01

**Abordagem:** otimizacao automatica de parametros fuzzy (integra a Parte 1)

Equipe: _(preencher)_ · Turma: _(preencher)_

---

## Motivacao

- O fuzzy manual e interpretavel, mas detecta poucas falhas (recall 0,27).
- Em vez de ajustar "no olho", **buscamos os melhores parametros automaticamente**.
- Metaheuristica = algoritmo principal; o sistema fuzzy = **funcao de aptidao**.

---

## Formulacao da otimizacao

| Elemento | Definicao |
|---|---|
| Variaveis de decisao | 31 breakpoints das MFs |
| Representacao | vetor real; bounds = universo de cada variavel |
| Funcao objetivo | **F1 da classe falha** (treino), maximizar |
| Restricoes | ordenacao dos breakpoints (reparo por sort) |
| Baselines | fuzzy manual + busca aleatoria |

---

## Algoritmos

- **AG (real-coded):** torneio + crossover BLX-alpha + mutacao gaussiana + elitismo.
  Pop 40, 50 geracoes (2040 avaliacoes). Inicializacao informada pelo manual.
- **PSO (global-best):** w=0,72, c1=c2=1,49, clamp de velocidade, reflexao nos limites.
  Enxame 30, 50 iteracoes (1530 avaliacoes).
- **Busca aleatoria:** mesmo orcamento do AG (comparacao justa).

---

## Protocolo experimental

- **5 sementes independentes** por metodo (metodo estocastico).
- Split estratificado 70/30 fixo (semente 42).
- Metricas: F1 (melhor/pior/media/desvio), recall, convergencia, custo.
- Motor fuzzy **vetorizado**: ~8 ms por avaliacao (7000 amostras).

---

## Resultados (5 sementes)

| Metodo | F1 media | Recall | Avaliacoes |
|---|---|---|---|
| Manual | 0,346 | 0,265 | 1 |
| Aleatoria | 0,477 | 0,416 | 2040 |
| PSO | 0,544 | 0,475 | 1530 |
| **AG** | **0,576** | **0,488** | 2040 |

Ordem **AG > PSO > aleatoria > manual** consistente em todas as sementes.

---

## Convergencia e eficiencia

![Convergencia](../results/figures/02_convergencia.png)

PSO mais rapido no inicio; AG ultrapassa e termina mais estavel; **aleatoria estagna**.

---

## Antes x Depois

![Confusao antes/depois](../results/figures/02_confusao_antes_depois.png)

Menos falsos negativos. O termo "Novo" do desgaste foi **estreitado** -> mesmo desgaste
leve ja carrega risco. Interpretabilidade preservada.

---

## Conclusao — Parte 2

- AG/PSO elevam o F1 de ~0,35 para ~0,58 e quase dobram o recall.
- Ganho vem da **busca dirigida** (aleatoria fica para tras com mesmo orcamento).
- **Interpretabilidade mantida** (so deslocou breakpoints).
- Futuro: pesos de regra, fitness multiobjetivo, validacao cruzada, DE.
