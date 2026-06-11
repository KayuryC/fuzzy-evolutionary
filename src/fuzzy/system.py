"""Definicao do sistema fuzzy de manutencao preditiva e codificacao p/ otimizador.

Universos e parametros das MFs sao ancorados nos quantis reais do dataset AI4I
2020 (ver `data/ai4i2020.csv`):
  * Desgaste (Tool wear) : 0-253 min  (q05=10, mediana=108, q95=206)
  * Torque               : 3.8-76.6 Nm (q05=23.5, mediana=40, q95=56)
  * Rotacao              : 1168-2886 rpm (q05=1332, mediana=1503, q95=1868)

Tambem expomos a codificacao genoma<->sistema usada pela Parte 2: apenas os
breakpoints internos das MFs sao ajustaveis; os "ombros" presos ao limite do
universo (lo ou hi) permanecem fixos. Isso mantem cada MF valida e reduz a
dimensionalidade do problema de otimizacao para 31 variaveis.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Dict, List, Tuple

import numpy as np

from .engine import FuzzyVariable, MamdaniSystem
from .rules import default_rules

# --------------------------------------------------------------------------- #
# Parametros padrao (sintonia "manual/especialista" = baseline da Parte 2).
# --------------------------------------------------------------------------- #
DESGASTE = FuzzyVariable(
    name="desgaste", lo=0.0, hi=260.0,
    mfs={
        "Novo": ("trap", [0, 0, 40, 90]),
        "Moderado": ("tri", [60, 130, 200]),
        "Desgastado": ("trap", [170, 220, 260, 260]),
    },
)
TORQUE = FuzzyVariable(
    name="torque", lo=0.0, hi=80.0,
    mfs={
        "Baixo": ("trap", [0, 0, 20, 35]),
        "Normal": ("tri", [25, 40, 55]),
        "Alto": ("trap", [45, 60, 80, 80]),
    },
)
ROTACAO = FuzzyVariable(
    name="rotacao", lo=1100.0, hi=2900.0,
    mfs={
        "Baixa": ("trap", [1100, 1100, 1300, 1500]),
        "Media": ("tri", [1350, 1600, 2100]),
        "Alta": ("trap", [1850, 2300, 2900, 2900]),
    },
)
RISCO = FuzzyVariable(
    name="risco", lo=0.0, hi=100.0,
    mfs={
        "Baixa": ("trap", [0, 0, 15, 35]),
        "Moderada": ("tri", [25, 45, 65]),
        "Alta": ("tri", [55, 72, 88]),
        "Critica": ("trap", [80, 92, 100, 100]),
    },
)


def build_default_system() -> MamdaniSystem:
    """Sistema Mamdani com a sintonia manual (baseline)."""
    return MamdaniSystem(
        inputs=[deepcopy(DESGASTE), deepcopy(TORQUE), deepcopy(ROTACAO)],
        output=deepcopy(RISCO),
        rules=default_rules(),
    )


# --------------------------------------------------------------------------- #
# Codificacao genoma <-> sistema (usada pelo AG/PSO da Parte 2).
# --------------------------------------------------------------------------- #
# Um "slot" e um parametro ajustavel: (variavel, termo, indice_no_param, lo, hi).
Slot = Tuple[str, str, int, float, float]


def _variables(system: MamdaniSystem) -> List[FuzzyVariable]:
    return list(system.inputs) + [system.output]


def build_param_spec(system: MamdaniSystem) -> List[Slot]:
    """Lista os parametros ajustaveis. Fixos = ombros presos a lo/hi do universo."""
    slots: List[Slot] = []
    for var in _variables(system):
        for term, (_, params) in var.mfs.items():
            for i, p in enumerate(params):
                # Pinos no limite do universo permanecem fixos (formam o "ombro").
                if p == var.lo or p == var.hi:
                    continue
                slots.append((var.name, term, i, var.lo, var.hi))
    return slots


def system_to_vector(system: MamdaniSystem, spec: List[Slot]) -> np.ndarray:
    """Extrai o vetor de parametros ajustaveis na ordem do ``spec``."""
    var_by_name = {v.name: v for v in _variables(system)}
    return np.array([var_by_name[vn].mfs[term][1][i] for (vn, term, i, _, _) in spec],
                    dtype=float)


def bounds_from_spec(spec: List[Slot]) -> Tuple[np.ndarray, np.ndarray]:
    """Vetores de limites inferior e superior para cada gene."""
    lo = np.array([s[3] for s in spec], dtype=float)
    hi = np.array([s[4] for s in spec], dtype=float)
    return lo, hi


def vector_to_system(vector: np.ndarray, spec: List[Slot],
                     base: MamdaniSystem | None = None) -> MamdaniSystem:
    """Reconstroi um ``MamdaniSystem`` a partir do genoma.

    Reparo: apos inserir os genes, ordena os parametros de cada termo (a<=b<=c<=d)
    para garantir MFs validas, sem precisar de restricoes no otimizador.
    """
    sys = build_default_system() if base is None else deepcopy(base)
    var_by_name = {v.name: v for v in _variables(sys)}

    for value, (vn, term, i, lo, hi) in zip(vector, spec):
        params = var_by_name[vn].mfs[term][1]
        params[i] = float(np.clip(value, lo, hi))

    # Reparo de ordenacao por termo.
    for var in _variables(sys):
        for term, (kind, params) in var.mfs.items():
            params.sort()
    return sys
