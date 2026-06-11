"""Busca aleatoria — baseline ingenuo exigido para comparacao na Parte 2.

Amostra genomas uniformemente no espaco de busca e guarda o melhor. Serve para
mostrar que o ganho do AG/PSO vem da *busca dirigida*, e nao apenas do numero de
avaliacoes (usamos o mesmo orcamento de avaliacoes).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np

from .fitness import FitnessEvaluator


@dataclass
class RandomResult:
    best_vector: np.ndarray
    best_fitness: float
    history: List[float]      # melhor fitness acumulado por amostra
    n_evals: int


def run_random_search(evaluator: FitnessEvaluator, *, budget=3200, seed=0,
                      include_manual=True) -> RandomResult:
    rng = np.random.default_rng(seed)
    best_vec = evaluator.manual_vector() if include_manual else evaluator.random_vector(rng)
    best_fit = evaluator.evaluate(best_vec)
    history = [best_fit]
    for _ in range(budget - 1):
        cand = evaluator.random_vector(rng)
        f = evaluator.evaluate(cand)
        if f > best_fit:
            best_vec, best_fit = cand, f
        history.append(best_fit)
    return RandomResult(best_vector=best_vec, best_fitness=best_fit,
                        history=history, n_evals=evaluator.n_evals)
