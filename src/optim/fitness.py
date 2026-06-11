"""Funcao objetivo (fitness) para a otimizacao evolutiva dos parametros fuzzy.

Problema de otimizacao (Parte 2):
  * Variaveis de decisao: os 31 breakpoints ajustaveis das MFs (genoma real).
  * Espaco de busca: cada gene limitado ao universo de sua variavel.
  * Funcao objetivo: F1 da classe falha no conjunto de TREINO (maximizar).
  * Restricoes: ordenacao dos breakpoints (tratada no decode por reparo).

O limiar que converte o risco continuo em decisao binaria e escolhido em cada
avaliacao maximizando o F1 de treino — ou seja, faz parte do classificador. A
avaliacao final (relatorio) usa o TESTE com o limiar fixado no treino.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ..fuzzy.system import (build_default_system, build_param_spec,
                            bounds_from_spec, system_to_vector, vector_to_system)
from ..metrics import best_threshold, score_binary, Scores


@dataclass
class FitnessEvaluator:
    """Avalia genomas contra os dados de treino. Conta avaliacoes (custo)."""
    X_train: np.ndarray
    y_train: np.ndarray
    metric: str = "f1"
    n_evals: int = field(default=0, init=False)

    def __post_init__(self):
        self._base = build_default_system()
        self.spec = build_param_spec(self._base)
        self.lo, self.hi = bounds_from_spec(self.spec)
        self.dim = len(self.spec)

    # -- genoma de referencia (sintonia manual) -------------------------------
    def manual_vector(self) -> np.ndarray:
        return system_to_vector(self._base, self.spec)

    def random_vector(self, rng: np.random.Generator) -> np.ndarray:
        return rng.uniform(self.lo, self.hi)

    # -- avaliacao ------------------------------------------------------------
    def evaluate(self, vector: np.ndarray) -> float:
        """F1 (ou metrica escolhida) no treino para o genoma dado."""
        self.n_evals += 1
        system = vector_to_system(np.asarray(vector), self.spec, base=self._base)
        risk = system.predict(self.X_train)
        _, value = best_threshold(risk, self.y_train, self.metric)
        return value

    def threshold_for(self, vector: np.ndarray) -> float:
        system = vector_to_system(np.asarray(vector), self.spec, base=self._base)
        risk = system.predict(self.X_train)
        thr, _ = best_threshold(risk, self.y_train, self.metric)
        return thr

    def full_test_scores(self, vector: np.ndarray, X_test, y_test) -> tuple[Scores, float]:
        """Constroi o sistema, fixa o limiar no treino e avalia no teste."""
        system = vector_to_system(np.asarray(vector), self.spec, base=self._base)
        thr = self.threshold_for(vector)
        sc = score_binary(y_test, system.predict(X_test) >= thr)
        return sc, thr

    def build_system(self, vector: np.ndarray):
        return vector_to_system(np.asarray(vector), self.spec, base=self._base)
