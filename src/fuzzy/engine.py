"""Motor de inferencia Mamdani vetorizado em NumPy.

Por que motor proprio (e nao apenas scikit-fuzzy)?
  1. A rubrica valoriza dominio conceitual acima de "rodar biblioteca pronta".
  2. O otimizador evolutivo (AG/PSO) avalia o sistema milhares de vezes sobre
     ~10 mil amostras; precisamos avaliar o dataset INTEIRO de uma vez. Este
     motor processa as N amostras em paralelo, em vez de um laco por amostra.

Operadores (Mamdani classico):
  - AND (t-norma) ............ min
  - implicacao ............... min (corte/clipping do consequente)
  - agregacao das regras ..... max
  - defuzzificacao ........... centroide (centro de gravidade)

A saida final e o "indice de risco" continuo no universo da variavel de saida.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

from .membership import eval_mf


@dataclass
class FuzzyVariable:
    """Variavel linguistica: universo [lo, hi] e suas MFs por termo."""
    name: str
    lo: float
    hi: float
    # mfs: {termo: (kind, [params...])}  ex.: {"Novo": ("trap", [0,0,40,90])}
    mfs: Dict[str, Tuple[str, List[float]]]

    @property
    def terms(self) -> List[str]:
        return list(self.mfs.keys())

    def memberships(self, x) -> Dict[str, np.ndarray]:
        """Grau de pertinencia de ``x`` em cada termo (dict termo->array)."""
        return {t: eval_mf(x, kind, params) for t, (kind, params) in self.mfs.items()}


@dataclass
class Rule:
    """Regra fuzzy: SE (antecedentes ligados por AND) ENTAO saida=consequente.

    ``antecedent``: {nome_variavel: termo}.  ``consequent``: termo da saida.
    ``weight`` in [0,1] pondera o grau de ativacao (default 1.0).
    """
    antecedent: Dict[str, str]
    consequent: str
    weight: float = 1.0


@dataclass
class MamdaniSystem:
    """Sistema fuzzy Mamdani completo (entradas, saida, regras)."""
    inputs: List[FuzzyVariable]
    output: FuzzyVariable
    rules: List[Rule]
    resolution: int = 201  # n. de pontos da grade de defuzzificacao

    _ygrid: np.ndarray = field(init=False, repr=False)
    _out_term_mf: Dict[str, np.ndarray] = field(init=False, repr=False)

    def __post_init__(self):
        self._ygrid = np.linspace(self.output.lo, self.output.hi, self.resolution)
        # Pre-computa a MF de cada termo de saida sobre a grade (nao muda por amostra).
        self._out_term_mf = self.output.memberships(self._ygrid)

    # ------------------------------------------------------------------ #
    def _as_columns(self, X) -> Dict[str, np.ndarray]:
        """Aceita X como dict {var: array} ou array 2D (colunas na ordem de inputs)."""
        if isinstance(X, dict):
            return {k: np.atleast_1d(np.asarray(v, dtype=float)) for k, v in X.items()}
        X = np.atleast_2d(np.asarray(X, dtype=float))
        return {var.name: X[:, i] for i, var in enumerate(self.inputs)}

    def predict(self, X) -> np.ndarray:
        """Defuzzifica o risco para cada amostra. Retorna array (N,)."""
        cols = self._as_columns(X)
        n = len(next(iter(cols.values())))

        # 1) Pertinencias de cada (variavel, termo) para as N amostras.
        mu = {var.name: var.memberships(cols[var.name]) for var in self.inputs}

        # 2) Grau de ativacao de cada regra: min dos antecedentes * peso. (N x R)
        fire = np.empty((n, len(self.rules)), dtype=float)
        for r, rule in enumerate(self.rules):
            strength = np.ones(n, dtype=float)
            for var_name, term in rule.antecedent.items():
                strength = np.minimum(strength, mu[var_name][term])
            fire[:, r] = strength * rule.weight

        # 3) Ativacao agregada por TERMO de saida (max das regras com mesmo
        #    consequente). Reduz o custo de memoria da etapa de implicacao.
        out_terms = self.output.terms
        act = np.zeros((n, len(out_terms)), dtype=float)
        term_index = {t: i for i, t in enumerate(out_terms)}
        for r, rule in enumerate(self.rules):
            j = term_index[rule.consequent]
            act[:, j] = np.maximum(act[:, j], fire[:, r])

        # 4) Implicacao (corte) + agregacao: para cada y, pega o maior dentre
        #    min(ativacao_termo, MF_termo(y)).  (N x T x G) -> (N x G)
        term_mf = np.stack([self._out_term_mf[t] for t in out_terms], axis=0)  # (T x G)
        clipped = np.minimum(act[:, :, None], term_mf[None, :, :])             # (N x T x G)
        aggregated = clipped.max(axis=1)                                       # (N x G)

        # 5) Defuzzificacao por centroide. Onde nenhuma regra disparou,
        #    devolve o ponto medio do universo (saida neutra).
        denom = aggregated.sum(axis=1)
        num = (aggregated * self._ygrid[None, :]).sum(axis=1)
        mid = 0.5 * (self.output.lo + self.output.hi)
        out = np.where(denom > 1e-12, num / np.where(denom > 1e-12, denom, 1.0), mid)
        return out

    # ------------------------------------------------------------------ #
    def predict_one(self, **kwargs) -> float:
        """Conveniencia para uma unica amostra via keywords (nomes das entradas)."""
        X = {k: np.array([v], dtype=float) for k, v in kwargs.items()}
        return float(self.predict(X)[0])

    def explain_one(self, **kwargs) -> dict:
        """Explica uma decisao: pertinencias por termo e regras mais ativadas.

        Util para o produto (transparencia) e para a defesa oral: mostra POR QUE
        o sistema chegou aquele risco. Retorna dict com 'risk', 'memberships' e
        'rules' (ordenadas por grau de ativacao decrescente).
        """
        risk = self.predict_one(**kwargs)
        memberships = {}
        for var in self.inputs:
            x = float(kwargs[var.name])
            memberships[var.name] = {t: float(mu) for t, mu in var.memberships(x).items()}

        activations = []
        for rule in self.rules:
            strength = min(memberships[v][t] for v, t in rule.antecedent.items()) * rule.weight
            ant = " e ".join(f"{v}={t}" for v, t in rule.antecedent.items())
            activations.append({"se": ant, "entao": rule.consequent, "ativacao": strength})
        activations.sort(key=lambda a: a["ativacao"], reverse=True)
        return {"risk": risk, "memberships": memberships, "rules": activations}
