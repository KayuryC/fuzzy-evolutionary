# Base de Regras e Funcoes de Pertinencia

Sistema fuzzy **Mamdani** de manutencao preditiva (dataset AI4I 2020).

Operadores: AND = min · implicacao = min · agregacao = max · defuzzificacao = centroide.

## Variaveis, universos e termos

| Variavel | Papel | Universo | Unidade | Termos |
|---|---|---|---|---|
| desgaste | entrada | [0, 260] | min | Novo, Moderado, Desgastado |
| torque | entrada | [0, 80] | Nm | Baixo, Normal, Alto |
| rotacao | entrada | [1100, 2900] | rpm | Baixa, Media, Alta |
| risco | **saida** | [0, 100] | indice 0-100 | Baixa, Moderada, Alta, Critica |

## Parametros das funcoes de pertinencia

`tri[a,b,c]` = triangular · `trap[a,b,c,d]` = trapezoidal.

| Variavel | Termo | Tipo | Parametros |
|---|---|---|---|
| desgaste | Novo | trap | [0, 0, 40, 90] |
| desgaste | Moderado | tri | [60, 130, 200] |
| desgaste | Desgastado | trap | [170, 220, 260, 260] |
| torque | Baixo | trap | [0, 0, 20, 35] |
| torque | Normal | tri | [25, 40, 55] |
| torque | Alto | trap | [45, 60, 80, 80] |
| rotacao | Baixa | trap | [1100, 1100, 1300, 1500] |
| rotacao | Media | tri | [1350, 1600, 2100] |
| rotacao | Alta | trap | [1850, 2300, 2900, 2900] |
| risco | Baixa | trap | [0, 0, 15, 35] |
| risco | Moderada | tri | [25, 45, 65] |
| risco | Alta | tri | [55, 72, 88] |
| risco | Critica | trap | [80, 92, 100, 100] |

## Base de regras (20 regras)

Cada regra e justificada por um modo de falha documentado: 
**TWF** (desgaste), **OSF** (desgaste x torque), **PWF** (potencia ~ torque x rotacao), **HDF** (rotacao baixa).

| # | SE | ENTAO risco e | Justificativa |
|---|---|---|---|
| 1 | desgaste *Novo* e torque *Normal* e rotacao *Media* | **Baixa** | regime nominal |
| 2 | desgaste *Novo* e torque *Baixo* e rotacao *Media* | **Baixa** | carga leve, ferramenta nova |
| 3 | desgaste *Novo* e torque *Normal* e rotacao *Alta* | **Baixa** | alta rotacao mas potencia ok |
| 4 | desgaste *Moderado* e torque *Baixo* e rotacao *Media* | **Baixa** | desgaste medio, carga leve |
| 5 | desgaste *Moderado* e torque *Normal* e rotacao *Media* | **Moderada** | envelhecimento normal |
| 6 | desgaste *Desgastado* e torque *Baixo* e rotacao *Media* | **Moderada** | TWF emergente, baixa carga |
| 7 | desgaste *Desgastado* e torque *Normal* e rotacao *Media* | **Alta** | TWF + carga nominal |
| 8 | desgaste *Desgastado* e torque *Baixo* e rotacao *Alta* | **Alta** | ferramenta gasta domina o risco |
| 9 | desgaste *Moderado* e torque *Alto* | **Alta** | OSF incipiente |
| 10 | desgaste *Desgastado* e torque *Normal* | **Alta** | OSF: desgaste alto + torque |
| 11 | desgaste *Desgastado* e torque *Alto* | **Critica** | OSF severo |
| 12 | torque *Baixo* e rotacao *Baixa* | **Alta** | PWF por baixa potencia |
| 13 | desgaste *Novo* e torque *Baixo* e rotacao *Baixa* | **Moderada** | baixa potencia mitigada por ferramenta nova |
| 14 | torque *Alto* e rotacao *Alta* | **Alta** | PWF por alta potencia |
| 15 | desgaste *Moderado* e torque *Alto* e rotacao *Alta* | **Critica** | PWF alto + desgaste |
| 16 | torque *Normal* e rotacao *Baixa* | **Moderada** | HDF: baixa dissipacao |
| 17 | desgaste *Moderado* e rotacao *Baixa* | **Alta** | HDF + desgaste |
| 18 | desgaste *Novo* e torque *Alto* e rotacao *Alta* | **Moderada** | alta potencia, mas ferramenta nova |
| 19 | desgaste *Novo* e torque *Alto* e rotacao *Baixa* | **Moderada** | torque alto compensado por baixa rotacao |
| 20 | desgaste *Moderado* e torque *Normal* e rotacao *Alta* | **Moderada** | rotacao alta, desgaste medio |
