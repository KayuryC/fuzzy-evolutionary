"""Otimizacao por Enxame de Particulas (PSO) global-best.

Atualizacao classica (Kennedy & Eberhart, 1995):
  v <- w*v + c1*r1*(pbest - x) + c2*r2*(gbest - x)
  x <- x + v
com inercia ``w``, coeficientes cognitivo ``c1`` e social ``c2``, clamp de
velocidade e reflexao nos limites do espaco de busca. Mesma funcao objetivo e
mesma codificacao do AG, permitindo comparacao justa AG x PSO.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np

from .fitness import FitnessEvaluator


@dataclass
class PSOResult:
    best_vector: np.ndarray
    best_fitness: float
    history: List[float]      # melhor fitness (gbest) por iteracao
    n_evals: int


def run_pso(evaluator: FitnessEvaluator, *, swarm_size=30, iterations=80,
            w=0.72, c1=1.49, c2=1.49, vmax_frac=0.2, seed=0,
            seed_with_manual=True, verbose=False) -> PSOResult:
    rng = np.random.default_rng(seed)
    lo, hi, dim = evaluator.lo, evaluator.hi, evaluator.dim
    span = hi - lo
    vmax = vmax_frac * span

    # posicoes iniciais (uma semeada com a sintonia manual)
    X = rng.uniform(lo, hi, size=(swarm_size, dim))
    if seed_with_manual:
        X[0] = evaluator.manual_vector()
    V = rng.uniform(-vmax, vmax, size=(swarm_size, dim))

    pbest = X.copy()
    pbest_fit = np.array([evaluator.evaluate(x) for x in X])
    g = int(np.argmax(pbest_fit))
    gbest = pbest[g].copy()
    gbest_fit = float(pbest_fit[g])
    history = [gbest_fit]

    for it in range(iterations):
        r1 = rng.random((swarm_size, dim))
        r2 = rng.random((swarm_size, dim))
        V = w * V + c1 * r1 * (pbest - X) + c2 * r2 * (gbest - X)
        V = np.clip(V, -vmax, vmax)
        X = X + V
        # reflexao nos limites (mantem dentro do espaco factivel)
        below, above = X < lo, X > hi
        X = np.where(below, 2 * lo - X, X)
        X = np.where(above, 2 * hi - X, X)
        X = np.clip(X, lo, hi)
        V[below | above] *= -0.5

        fit = np.array([evaluator.evaluate(x) for x in X])
        improved = fit > pbest_fit
        pbest[improved] = X[improved]
        pbest_fit[improved] = fit[improved]
        g = int(np.argmax(pbest_fit))
        if pbest_fit[g] > gbest_fit:
            gbest, gbest_fit = pbest[g].copy(), float(pbest_fit[g])
        history.append(gbest_fit)
        if verbose and (it % 10 == 0 or it == iterations - 1):
            print(f"  [PSO seed={seed}] iter {it+1:3d}/{iterations}  best F1={gbest_fit:.4f}")

    return PSOResult(best_vector=gbest, best_fitness=gbest_fit,
                     history=history, n_evals=evaluator.n_evals)
