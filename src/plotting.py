"""Funcoes de visualizacao reutilizadas pelos notebooks.

Mantemos a plotagem aqui para que os notebooks fiquem focados na narrativa
(uma chamada por figura) e para reaproveitar o mesmo codigo no relatorio.
Todas as funcoes aceitam um ``ax`` opcional (composicao inline) e podem salvar
em ``results/figures``.
"""
from __future__ import annotations

import os
from typing import Dict, List

import numpy as np

# NAO forcamos backend aqui: nos notebooks o `%matplotlib inline` cuida da
# exibicao (e da embutida das figuras como evidencia de execucao). Em uso
# headless, o savefig funciona com o backend padrao.
import matplotlib.pyplot as plt

from .fuzzy.engine import FuzzyVariable, MamdaniSystem
from .metrics import Scores

FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "figures")
_UNITS = {"desgaste": "min", "torque": "Nm", "rotacao": "rpm", "risco": "indice 0-100"}


def _save(fig, save):
    if save:
        os.makedirs(FIG_DIR, exist_ok=True)
        fig.savefig(os.path.join(FIG_DIR, save), dpi=120, bbox_inches="tight")


def plot_membership(var: FuzzyVariable, ax=None, n: int = 500, save: str | None = None):
    """Plota as MFs de uma variavel sobre seu universo."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 3))
    else:
        fig = ax.figure
    x = np.linspace(var.lo, var.hi, n)
    for term, mu in var.memberships(x).items():
        ax.plot(x, mu, label=term, linewidth=2)
    ax.set_title(f"{var.name}  [{_UNITS.get(var.name, '')}]")
    ax.set_ylim(-0.03, 1.05)
    ax.set_xlabel(var.name)
    ax.set_ylabel("pertinencia")
    ax.legend(fontsize=8, loc="upper center", ncol=len(var.mfs))
    ax.grid(alpha=0.3)
    _save(fig, save)
    return ax


def plot_all_memberships(system: MamdaniSystem, save: str | None = None):
    """Grade com as MFs das 3 entradas + saida."""
    variables = list(system.inputs) + [system.output]
    fig, axes = plt.subplots(2, 2, figsize=(11, 6))
    for ax, var in zip(axes.ravel(), variables):
        plot_membership(var, ax=ax)
    fig.tight_layout()
    _save(fig, save)
    return fig


def control_surface(system: MamdaniSystem, x_name: str, y_name: str,
                    fixed: Dict[str, float], grid: int = 45):
    """Calcula a superficie de controle (risco) variando x_name e y_name."""
    var_by_name = {v.name: v for v in system.inputs}
    vx, vy = var_by_name[x_name], var_by_name[y_name]
    xs = np.linspace(vx.lo, vx.hi, grid)
    ys = np.linspace(vy.lo, vy.hi, grid)
    XX, YY = np.meshgrid(xs, ys)
    cols = {}
    for var in system.inputs:
        if var.name == x_name:
            cols[var.name] = XX.ravel()
        elif var.name == y_name:
            cols[var.name] = YY.ravel()
        else:
            cols[var.name] = np.full(XX.size, fixed[var.name], dtype=float)
    Z = system.predict(cols).reshape(XX.shape)
    return XX, YY, Z


def plot_control_surface(system: MamdaniSystem, x_name: str, y_name: str,
                        fixed: Dict[str, float], grid: int = 45, ax=None,
                        save: str | None = None):
    """Mapa de calor da superficie de controle."""
    XX, YY, Z = control_surface(system, x_name, y_name, fixed, grid)
    if ax is None:
        fig, ax = plt.subplots(figsize=(5.2, 4))
    else:
        fig = ax.figure
    cs = ax.contourf(XX, YY, Z, levels=20, cmap="RdYlGn_r")
    fig.colorbar(cs, ax=ax, label="risco")
    fixed_txt = ", ".join(f"{k}={v:g}" for k, v in fixed.items())
    ax.set_title(f"Superficie de controle\n({fixed_txt})", fontsize=9)
    ax.set_xlabel(x_name)
    ax.set_ylabel(y_name)
    _save(fig, save)
    return ax


def plot_sensitivity(system: MamdaniSystem, var_name: str, base: Dict[str, float],
                    n: int = 150, ax=None, save: str | None = None):
    """Curva de sensibilidade: varia uma entrada e mantem as demais fixas."""
    var_by_name = {v.name: v for v in system.inputs}
    var = var_by_name[var_name]
    sweep = np.linspace(var.lo, var.hi, n)
    cols = {v.name: np.full(n, base[v.name], dtype=float) for v in system.inputs}
    cols[var_name] = sweep
    risk = system.predict(cols)
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 3))
    else:
        fig = ax.figure
    ax.plot(sweep, risk, linewidth=2, color="C3")
    others = ", ".join(f"{k}={v:g}" for k, v in base.items() if k != var_name)
    ax.set_title(f"Sensibilidade ao {var_name}  ({others})", fontsize=9)
    ax.set_xlabel(var_name)
    ax.set_ylabel("risco")
    ax.grid(alpha=0.3)
    _save(fig, save)
    return ax


def plot_confusion(scores: Scores, title: str = "Matriz de confusao",
                  ax=None, save: str | None = None):
    """Heatmap 2x2 [[TN,FP],[FN,TP]]."""
    cm = scores.confusion
    if ax is None:
        fig, ax = plt.subplots(figsize=(3.6, 3.2))
    else:
        fig = ax.figure
    ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1], ["prev. 0", "prev. 1"])
    ax.set_yticks([0, 1], ["real 0", "real 1"])
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{cm[i, j]}", ha="center", va="center",
                    color="black", fontsize=12)
    ax.set_title(f"{title}\nF1={scores.f1:.3f}  rec={scores.recall:.3f}", fontsize=9)
    _save(fig, save)
    return ax


def plot_convergence(histories: Dict[str, List[float]], ax=None,
                    save: str | None = None):
    """Curvas de convergencia: melhor fitness por geracao/iteracao por metodo."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(6.5, 4))
    else:
        fig = ax.figure
    for label, hist in histories.items():
        ax.plot(range(1, len(hist) + 1), hist, linewidth=2, label=label)
    ax.set_xlabel("geracao / iteracao")
    ax.set_ylabel("melhor fitness (F1)")
    ax.set_title("Convergencia")
    ax.legend()
    ax.grid(alpha=0.3)
    _save(fig, save)
    return ax


def plot_convergence_bands(runs: Dict[str, np.ndarray], ax=None,
                          xlabel: str = "geracao / iteracao",
                          save: str | None = None):
    """Convergencia media +/- desvio entre sementes.

    ``runs[label]`` deve ter shape (n_sementes, n_passos).
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 4.2))
    else:
        fig = ax.figure
    for label, arr in runs.items():
        arr = np.asarray(arr, dtype=float)
        mean = arr.mean(axis=0)
        std = arr.std(axis=0)
        steps = np.arange(1, arr.shape[1] + 1)
        line, = ax.plot(steps, mean, linewidth=2, label=label)
        ax.fill_between(steps, mean - std, mean + std, alpha=0.15, color=line.get_color())
    ax.set_xlabel(xlabel)
    ax.set_ylabel("melhor fitness (F1) — media +/- dp")
    ax.set_title("Convergencia (5 sementes)")
    ax.legend()
    ax.grid(alpha=0.3)
    _save(fig, save)
    return ax


def plot_budget_curves(curves: Dict[str, list], ax=None, n_grid: int = 200,
                      save: str | None = None):
    """Melhor-ate-agora x numero de avaliacoes (comparacao justa por orcamento).

    ``curves[label]`` = lista (por semente) de tuplas (evals_array, valores_array).
    Interpola cada semente numa grade comum e plota media +/- desvio.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 4.2))
    else:
        fig = ax.figure
    # grade comum = ate o menor "maximo de evals" entre as sementes/metodos
    max_eval = min(min(ev[-1] for ev, _ in seeds) for seeds in curves.values())
    grid = np.linspace(1, max_eval, n_grid)
    for label, seeds in curves.items():
        stacked = np.array([np.interp(grid, ev, val) for ev, val in seeds])
        mean, std = stacked.mean(axis=0), stacked.std(axis=0)
        line, = ax.plot(grid, mean, linewidth=2, label=label)
        ax.fill_between(grid, mean - std, mean + std, alpha=0.15, color=line.get_color())
    ax.set_xlabel("avaliacoes da funcao objetivo")
    ax.set_ylabel("melhor F1 ate o momento")
    ax.set_title("Eficiencia por orcamento (5 sementes)")
    ax.legend()
    ax.grid(alpha=0.3)
    _save(fig, save)
    return ax
