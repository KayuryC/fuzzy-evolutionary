"""Base de regras do sistema de manutencao preditiva (Mamdani).

Cada regra e justificada pelos modos de falha documentados do dataset AI4I 2020
(Matzka, 2020), capturaveis pelas 3 entradas (desgaste, torque, rotacao):

  * TWF  (Tool Wear Failure)  -> desgaste alto.
  * OSF  (OverStrain Failure) -> desgaste * torque elevados (esforco mecanico).
  * PWF  (Power Failure)      -> potencia ~ torque * rotacao fora da faixa util:
                                 baixa (torque baixo + rotacao baixa) ou
                                 alta  (torque alto  + rotacao alta).
  * HDF  (Heat Dissipation)   -> rotacao baixa favorece falha por calor.

Saida = indice de risco / urgencia de manutencao em {Baixa, Moderada, Alta, Critica}.

Notacao das regras: (antecedentes, consequente, justificativa). O peso e 1.0 por
padrao e pode ser ajustado pelo otimizador evolutivo (Parte 2).
"""
from __future__ import annotations

from .engine import Rule

# (antecedente {var: termo}, termo_saida, comentario)
RULE_TABLE = [
    # --- Operacao segura / baixo risco --------------------------------------
    ({"desgaste": "Novo", "torque": "Normal", "rotacao": "Media"}, "Baixa", "regime nominal"),
    ({"desgaste": "Novo", "torque": "Baixo", "rotacao": "Media"}, "Baixa", "carga leve, ferramenta nova"),
    ({"desgaste": "Novo", "torque": "Normal", "rotacao": "Alta"}, "Baixa", "alta rotacao mas potencia ok"),
    ({"desgaste": "Moderado", "torque": "Baixo", "rotacao": "Media"}, "Baixa", "desgaste medio, carga leve"),
    # --- Desgaste / TWF ------------------------------------------------------
    ({"desgaste": "Moderado", "torque": "Normal", "rotacao": "Media"}, "Moderada", "envelhecimento normal"),
    ({"desgaste": "Desgastado", "torque": "Baixo", "rotacao": "Media"}, "Moderada", "TWF emergente, baixa carga"),
    ({"desgaste": "Desgastado", "torque": "Normal", "rotacao": "Media"}, "Alta", "TWF + carga nominal"),
    ({"desgaste": "Desgastado", "torque": "Baixo", "rotacao": "Alta"}, "Alta", "ferramenta gasta domina o risco"),
    # --- Sobre-esforco / OSF (desgaste x torque) -----------------------------
    ({"desgaste": "Moderado", "torque": "Alto"}, "Alta", "OSF incipiente"),
    ({"desgaste": "Desgastado", "torque": "Normal"}, "Alta", "OSF: desgaste alto + torque"),
    ({"desgaste": "Desgastado", "torque": "Alto"}, "Critica", "OSF severo"),
    # --- Falha de potencia / PWF (potencia ~ torque x rotacao) ---------------
    ({"torque": "Baixo", "rotacao": "Baixa"}, "Alta", "PWF por baixa potencia"),
    ({"desgaste": "Novo", "torque": "Baixo", "rotacao": "Baixa"}, "Moderada", "baixa potencia mitigada por ferramenta nova"),
    ({"torque": "Alto", "rotacao": "Alta"}, "Alta", "PWF por alta potencia"),
    ({"desgaste": "Moderado", "torque": "Alto", "rotacao": "Alta"}, "Critica", "PWF alto + desgaste"),
    # --- Calor / HDF (rotacao baixa) -----------------------------------------
    ({"torque": "Normal", "rotacao": "Baixa"}, "Moderada", "HDF: baixa dissipacao"),
    ({"desgaste": "Moderado", "rotacao": "Baixa"}, "Alta", "HDF + desgaste"),
    # --- Casos conflitantes / fronteiricos -----------------------------------
    ({"desgaste": "Novo", "torque": "Alto", "rotacao": "Alta"}, "Moderada", "alta potencia, mas ferramenta nova"),
    ({"desgaste": "Novo", "torque": "Alto", "rotacao": "Baixa"}, "Moderada", "torque alto compensado por baixa rotacao"),
    ({"desgaste": "Moderado", "torque": "Normal", "rotacao": "Alta"}, "Moderada", "rotacao alta, desgaste medio"),
]


def default_rules() -> list[Rule]:
    """Constroi a lista de objetos ``Rule`` a partir da tabela acima."""
    return [Rule(antecedent=ant, consequent=cons) for ant, cons, _ in RULE_TABLE]
