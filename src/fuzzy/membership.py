"""Funcoes de pertinencia (membership functions) vetorizadas em NumPy.

Todas as funcoes recebem ``x`` (escalar ou array) e retornam o grau de
pertinencia em [0, 1] com o mesmo formato de ``x``. Sao usadas tanto pelo
motor de inferencia quanto pela geracao dos graficos das MFs.

Implementamos triangular e trapezoidal (suficientes para o sistema e faceis
de parametrizar pelo otimizador evolutivo). As formulas seguem a definicao
classica de Jang, Sun & Mizutani (1997).
"""
from __future__ import annotations

import numpy as np


def trimf(x, a: float, b: float, c: float):
    """Funcao triangular com pes ``a`` <= pico ``b`` <= pe ``c``.

    mu(x) = 0                      , x <= a ou x >= c
            (x - a) / (b - a)      , a < x <= b
            (c - x) / (c - b)      , b < x <  c
    Degeneracoes (a == b ou b == c) viram "rampas" verticais, tratadas
    com np.errstate para evitar divisao por zero.
    """
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x)
    with np.errstate(divide="ignore", invalid="ignore"):
        left = (x - a) / (b - a) if b != a else np.where(x <= a, 0.0, 1.0)
        right = (c - x) / (c - b) if c != b else np.where(x >= c, 0.0, 1.0)
    y = np.maximum(np.minimum(left, right), 0.0)
    return y


def trapmf(x, a: float, b: float, c: float, d: float):
    """Funcao trapezoidal com pes ``a`` <= ombro ``b`` <= ombro ``c`` <= pe ``d``.

    Patamar 1.0 em [b, c]; rampas lineares em [a, b] e [c, d]; 0 fora de [a, d].
    """
    x = np.asarray(x, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        left = (x - a) / (b - a) if b != a else np.where(x < b, 0.0, 1.0)
        right = (d - x) / (d - c) if d != c else np.where(x > c, 0.0, 1.0)
    y = np.maximum(np.minimum(np.minimum(left, right), 1.0), 0.0)
    return y


def eval_mf(x, kind: str, params):
    """Despacha para a MF certa a partir de ``kind`` ('tri'|'trap') e parametros."""
    if kind == "tri":
        return trimf(x, *params)
    if kind == "trap":
        return trapmf(x, *params)
    raise ValueError(f"tipo de MF desconhecido: {kind!r}")
