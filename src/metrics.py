"""Metricas de classificacao, implementadas explicitamente.

Mesmo havendo scikit-learn no ambiente, calculamos as metricas a mao para
deixar claro o que esta sendo medido (a rubrica valoriza dominio conceitual).
O dataset e desbalanceado (~3.4% de falhas), entao a metrica-alvo do otimizador
e o **F1 da classe falha**; acuracia crua seria enganosa (~96% prevendo "sem
falha"). Tambem oferecemos o J de Youden como alternativa balanceada.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Scores:
    tp: int
    fp: int
    tn: int
    fn: int

    @property
    def accuracy(self) -> float:
        tot = self.tp + self.fp + self.tn + self.fn
        return (self.tp + self.tn) / tot if tot else 0.0

    @property
    def precision(self) -> float:
        d = self.tp + self.fp
        return self.tp / d if d else 0.0

    @property
    def recall(self) -> float:  # sensibilidade / TPR
        d = self.tp + self.fn
        return self.tp / d if d else 0.0

    @property
    def specificity(self) -> float:  # TNR
        d = self.tn + self.fp
        return self.tn / d if d else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    @property
    def youden_j(self) -> float:
        return self.recall + self.specificity - 1.0

    @property
    def confusion(self) -> np.ndarray:
        # linhas = real {0,1}, colunas = previsto {0,1}
        return np.array([[self.tn, self.fp], [self.fn, self.tp]], dtype=int)

    def as_dict(self) -> dict:
        return {
            "accuracy": self.accuracy, "precision": self.precision,
            "recall": self.recall, "specificity": self.specificity,
            "f1": self.f1, "youden_j": self.youden_j,
            "tp": self.tp, "fp": self.fp, "tn": self.tn, "fn": self.fn,
        }


def score_binary(y_true, y_pred) -> Scores:
    """Confronta rotulos reais e previstos (ambos binarios 0/1)."""
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    tp = int(np.sum((y_pred == 1) & (y_true == 1)))
    fp = int(np.sum((y_pred == 1) & (y_true == 0)))
    tn = int(np.sum((y_pred == 0) & (y_true == 0)))
    fn = int(np.sum((y_pred == 0) & (y_true == 1)))
    return Scores(tp, fp, tn, fn)


def best_threshold(risk, y_true, metric: str = "f1", grid=None):
    """Varre limiares no escore de risco e devolve (melhor_limiar, melhor_valor).

    Permite converter a saida continua do fuzzy em decisao binaria de forma
    objetiva (a curva metrica x limiar tambem serve de evidencia experimental).
    """
    risk = np.asarray(risk, dtype=float)
    if grid is None:
        grid = np.linspace(risk.min(), risk.max(), 101)
    best_t, best_v = grid[0], -1.0
    for t in grid:
        v = getattr(score_binary(y_true, risk >= t), metric)
        if v > best_v:
            best_t, best_v = float(t), float(v)
    return best_t, best_v
