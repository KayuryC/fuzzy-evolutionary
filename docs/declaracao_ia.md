# Declaracao de Uso de Inteligencia Artificial

Conforme exigido pela atividade, declaramos de forma transparente o uso de
ferramentas de IA no desenvolvimento deste trabalho, bem como a revisao humana
realizada pela equipe. **O uso de IA nao substituiu o entendimento da equipe:**
todo o material foi lido, executado, testado e validado pelos integrantes.

## Ferramentas utilizadas

| Ferramenta | Finalidade | Prompt/comando resumido | Revisao critica da equipe |
|---|---|---|---|
| Claude Code (Claude Opus) | Estruturar o repositorio, implementar o motor Mamdani vetorizado, AG/PSO, notebooks e relatorios | "Modelar um sistema fuzzy de manutencao preditiva sobre o AI4I 2020 e otimizar as MFs com AG/PSO" | Revisamos cada modulo, conferimos as formulas das MFs e dos operadores, e validamos os resultados executando os notebooks |
| Claude Code | Depurar e validar a funcao objetivo e o decode genoma->sistema | "Verificar o roundtrip de codificacao e o calculo de F1 com classe desbalanceada" | Conferimos manualmente o roundtrip (diferenca 0) e a matriz de confusao no teste |
| Assistente de busca | Localizar o dataset AI4I 2020 e seus modos de falha documentados (TWF/HDF/PWF/OSF) | "Quais variaveis e limiares fisicos definem cada modo de falha do AI4I 2020?" | Confrontamos os limiares com as estatisticas reais do CSV (quantis) antes de definir as regras |

## O que foi aceito, corrigido e validado

- **Aceito:** a arquitetura modular (`src/fuzzy`, `src/optim`), o motor vetorizado
  e a estrutura dos notebooks. Conferimos que os operadores (min/min/max/centroide)
  correspondem ao Mamdani classico.
- **Corrigido/ajustado:** os parametros das funcoes de pertinencia foram ancorados
  por nos nos quantis reais do dataset e nos limiares fisicos dos modos de falha;
  a base de regras foi revisada regra a regra para refletir o dominio.
- **Validado:** executamos os dois notebooks de ponta a ponta, conferimos os
  numeros (baseline F1 ~ 0,35; AG ~ 0,58) e a coerencia das superficies de controle
  e curvas de convergencia. As metricas foram reimplementadas (sem usar
  `sklearn.metrics`) para garantir que entendemos o que esta sendo medido.

## Responsabilidade

A equipe assume integral responsabilidade pelo conteudo final, pelo codigo
publicado no GitHub e pela defesa tecnica do trabalho. Nenhum resultado foi
inventado: todas as tabelas e figuras sao reproduziveis executando os notebooks
e os scripts descritos no `README.md`.
