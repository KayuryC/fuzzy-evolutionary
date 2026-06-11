"""Algoritmo Genetico real-coded para otimizar os parametros das MFs fuzzy.

Operadores:
  * Selecao .... torneio (tamanho configuravel).
  * Crossover .. BLX-alpha (mistura linear com extrapolacao controlada).
  * Mutacao .... gaussiana por gene, sigma proporcional ao intervalo do gene.
  * Elitismo ... preserva os melhores individuos entre geracoes.

Inicializacao informada: um individuo recebe a sintonia manual (especialista) e
parte da populacao e perturbacao em torno dela; o restante e aleatorio uniforme.
Com elitismo, isso garante que o resultado nunca piore em relacao ao baseline
(util para a comparacao antes/depois) sem impedir a exploracao do espaco.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import numpy as np

from .fitness import FitnessEvaluator


@dataclass
class GAResult:
    best_vector: np.ndarray
    best_fitness: float
    history: List[float]      # melhor fitness por geracao
    n_evals: int


def _tournament(pop, fit, rng, k):
    idx = rng.integers(0, len(pop), size=k)
    return pop[idx[np.argmax(fit[idx])]].copy()


def _blx_alpha(p1, p2, rng, lo, hi, alpha=0.5):
    cmin = np.minimum(p1, p2)
    cmax = np.maximum(p1, p2)
    d = cmax - cmin
    child = rng.uniform(cmin - alpha * d, cmax + alpha * d)
    return np.clip(child, lo, hi)


def run_ga(evaluator: FitnessEvaluator, *, pop_size=40, generations=80,
           tournament_k=3, crossover_rate=0.9, mutation_rate=0.15,
           elitism=2, seed=0, init_around_manual=0.5, verbose=False) -> GAResult:
    rng = np.random.default_rng(seed)
    lo, hi, dim = evaluator.lo, evaluator.hi, evaluator.dim
    span = hi - lo

    # --- populacao inicial ---------------------------------------------------
    manual = evaluator.manual_vector()
    pop = []
    pop.append(manual.copy())                                   # especialista exato
    n_perturb = int(round((pop_size - 1) * init_around_manual))
    for _ in range(n_perturb):                                  # perturbacoes do manual
        pop.append(np.clip(manual + rng.normal(0, 0.1 * span), lo, hi))
    while len(pop) < pop_size:                                  # aleatorios uniformes
        pop.append(evaluator.random_vector(rng))
    pop = np.array(pop)

    fit = np.array([evaluator.evaluate(ind) for ind in pop])
    history = [float(fit.max())]

    for gen in range(generations):
        # elitismo
        elite_idx = np.argsort(fit)[-elitism:]
        new_pop = [pop[i].copy() for i in elite_idx]

        while len(new_pop) < pop_size:
            p1 = _tournament(pop, fit, rng, tournament_k)
            p2 = _tournament(pop, fit, rng, tournament_k)
            child = _blx_alpha(p1, p2, rng, lo, hi) if rng.random() < crossover_rate else p1.copy()
            # mutacao gaussiana por gene
            mask = rng.random(dim) < mutation_rate
            child[mask] = np.clip(child[mask] + rng.normal(0, 0.1 * span[mask]), lo[mask], hi[mask])
            new_pop.append(child)

        pop = np.array(new_pop)
        fit = np.array([evaluator.evaluate(ind) for ind in pop])
        history.append(float(fit.max()))
        if verbose and (gen % 10 == 0 or gen == generations - 1):
            print(f"  [GA seed={seed}] gen {gen+1:3d}/{generations}  best F1={fit.max():.4f}")

    best_i = int(np.argmax(fit))
    return GAResult(best_vector=pop[best_i].copy(), best_fitness=float(fit[best_i]),
                    history=history, n_evals=evaluator.n_evals)
