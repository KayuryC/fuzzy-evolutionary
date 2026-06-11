# Manutencao Preditiva Fuzzy otimizada por Computacao Evolutiva

Projeto integrado das **Partes 1 (Sistemas de Controle Fuzzy)** e **2 (IA Evolutiva
e Computacao Bioinspirada)** da disciplina **Inteligencia Artificial e Computacional
(0700M8)** — CESUPA, 2026/01. Prof. Daniel Leal Souza.

- **Turma:** _(CC5MA)_
- **Integrantes:** _(Kayury carneiro e vitor bismarck)_
- **Modalidade Parte 1:** Opcao B (produto) · motor **Mamdani**
- **Abordagem Parte 2:** otimizacao automatica de parametros fuzzy com **AG** e **PSO**
- **Repositorio GitHub:** https://github.com/KayuryC/fuzzy-evolutionary.git

## Resumo

Um **sistema fuzzy Mamdani** estima o **risco de falha / urgencia de manutencao**
de uma maquina industrial a partir de tres grandezas de operacao (desgaste da
ferramenta, torque e rotacao), usando o dataset publico **AI4I 2020 Predictive
Maintenance** (UCI, 10.000 amostras).

As duas partes do trabalho se integram: a **Parte 2** trata a sintonia das funcoes
de pertinencia como um **problema de otimizacao** e o resolve com **Algoritmo
Genetico** e **PSO**, comparando contra dois baselines (fuzzy manual e busca
aleatoria). O F1 da classe falha sobe de **~0,35 (manual)** para **~0,58 (AG)**,
preservando a interpretabilidade do sistema.

| Metodo | F1 teste (media) | Recall | Avaliacoes | Tempo |
|---|---|---|---|---|
| Fuzzy manual (baseline) | 0,346 | 0,265 | 1 | - |
| Busca aleatoria | 0,477 | 0,416 | 2040 | ~18 s |
| PSO | 0,544 | 0,475 | 1530 | ~13 s |
| **Algoritmo Genetico** | **0,576** | **0,488** | 2040 | ~32 s |

## Tecnologias

Python 3.9 · NumPy · pandas · Matplotlib · scikit-learn (apenas split) · Jupyter.
O **motor de inferencia Mamdani**, o **AG** e o **PSO** sao **implementados pela
equipe** (em `src/`), nao bibliotecas prontas.

## Estrutura do repositorio

```
fuzzy-evolutionary/
├── data/                       dataset AI4I 2020 (ai4i2020.csv)
├── src/
│   ├── fuzzy/                  motor fuzzy
│   │   ├── membership.py       MFs triangular/trapezoidal (vetorizadas)
│   │   ├── engine.py           inferencia Mamdani vetorizada + explain_one()
│   │   ├── rules.py            base de 20 regras (justificadas por modo de falha)
│   │   └── system.py           variaveis/universos + codificacao genoma<->sistema
│   ├── optim/                  computacao evolutiva
│   │   ├── fitness.py          funcao objetivo (F1 da classe falha)
│   │   ├── ga.py               Algoritmo Genetico real-coded
│   │   ├── pso.py              Otimizacao por Enxame de Particulas
│   │   └── random_search.py    baseline de busca aleatoria
│   ├── data_loader.py          carga + split estratificado
│   ├── metrics.py              metricas (F1, recall, Youden, confusao)
│   ├── plotting.py             figuras (MFs, superficies, convergencia)
│   └── cli.py                  PRODUTO: interface de linha de comando
├── notebooks/
│   ├── 01_modelagem_e_validacao_fuzzy.ipynb    Parte 1 (celula a celula)
│   └── 02_otimizacao_evolutiva.ipynb           Parte 2 (celula a celula)
├── results/figures/ · results/tables/          evidencias geradas
├── docs/                       relatorios, base de regras, declaracao de IA
├── slides/                     slides em PDF
├── tools/build_pdfs.py         gera os PDFs a partir dos .md
└── requirements.txt
```

## Instalacao

```bash
python3 -m pip install -r requirements.txt
```

O dataset ja acompanha o repositorio em `data/ai4i2020.csv`. Para reobte-lo:
baixar de <https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset>
e salvar como `data/ai4i2020.csv`.

## Execucao

### Notebooks (recomendado — acompanha o fluxo por celula)

```bash
jupyter notebook notebooks/01_modelagem_e_validacao_fuzzy.ipynb   # Parte 1
jupyter notebook notebooks/02_otimizacao_evolutiva.ipynb          # Parte 2
```

Os notebooks ja vem **executados** (figuras e tabelas embutidas). Para reproduzir,
basta "Run All". O notebook 02 leva alguns minutos (5 sementes x 3 metodos).

### Produto (CLI)

```bash
python -m src.cli --desgaste 230 --torque 70 --rotacao 1500 --explain
python -m src.cli --desgaste 20  --torque 38 --rotacao 1550
python -m src.cli --desgaste 230 --torque 70 --rotacao 1500 --optimized
```

`--explain` mostra as pertinencias ativas e as regras mais disparadas (transparencia).
`--optimized` usa o modelo ajustado pelo AG (gerado pelo notebook 02).

### Reproduzir as figuras/PDFs

As figuras sao salvas em `results/figures/` ao executar os notebooks. Os PDFs dos
relatorios e slides sao gerados por:

```bash
python tools/build_pdfs.py
```

## Cenarios de teste e resultados

- **Parte 1:** 6 cenarios (baixo, medio, alto, fronteirico, conflitante, critico),
  superficies de controle, curvas de sensibilidade e validacao quantitativa contra
  os rotulos reais (ver notebook 01 e `docs/relatorio_parte1_fuzzy.pdf`).
- **Parte 2:** 5 execucoes independentes por metodo, curvas de convergencia,
  comparacao por orcamento de avaliacoes e analise antes/depois (ver notebook 02 e
  `docs/relatorio_parte2_evolutiva.pdf`).

## Documentos

- [Relatorio Parte 1 — Fuzzy](docs/relatorio_parte1_fuzzy.md)
- [Relatorio Parte 2 — Evolutiva](docs/relatorio_parte2_evolutiva.md)
- [Base de regras e funcoes de pertinencia](docs/base_de_regras.md)
- [Declaracao de uso de IA](docs/declaracao_ia.md)

## Referencias

- Matzka, S. (2020). *Explainable Artificial Intelligence for Predictive Maintenance
  Applications.* AI4I 2020 Dataset, UCI Machine Learning Repository.
- Jang, J.-S. R.; Sun, C.-T.; Mizutani, E. (1997). *Neuro-Fuzzy and Soft Computing.*
- Mamdani, E. H.; Assilian, S. (1975). *An experiment in linguistic synthesis with a
  fuzzy logic controller.*
- Kennedy, J.; Eberhart, R. (1995). *Particle Swarm Optimization.* ICNN.
- Holland, J. H. (1975). *Adaptation in Natural and Artificial Systems.*
