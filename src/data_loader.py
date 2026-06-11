"""Carga do dataset AI4I 2020 e split estratificado treino/teste.

Selecionamos as 3 variaveis de entrada do sistema fuzzy (desgaste, torque,
rotacao) e o rotulo binario 'Machine failure'. O split e estratificado para
preservar a proporcao de falhas (~3.4%) em treino e teste.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

# Colunas de entrada na ORDEM esperada pelo sistema fuzzy (desgaste, torque, rotacao).
FEATURE_COLUMNS = ["Tool wear [min]", "Torque [Nm]", "Rotational speed [rpm]"]
TARGET_COLUMN = "Machine failure"
INPUT_NAMES = ["desgaste", "torque", "rotacao"]

_DEFAULT_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "ai4i2020.csv")


@dataclass
class Dataset:
    X: np.ndarray            # (N, 3) desgaste, torque, rotacao
    y: np.ndarray            # (N,) 0/1
    feature_names: list      # nomes "fuzzy" das entradas


def load_dataset(csv_path: str | None = None) -> Dataset:
    """Le o CSV e devolve features + rotulo."""
    path = csv_path or _DEFAULT_CSV
    df = pd.read_csv(path)
    X = df[FEATURE_COLUMNS].to_numpy(dtype=float)
    y = df[TARGET_COLUMN].to_numpy(dtype=int)
    return Dataset(X=X, y=y, feature_names=list(INPUT_NAMES))


def stratified_split(ds: Dataset, test_size: float = 0.30, seed: int = 42):
    """Particao estratificada treino/teste preservando a taxa de falhas."""
    rng = np.random.default_rng(seed)
    train_idx, test_idx = [], []
    for cls in np.unique(ds.y):
        idx = np.where(ds.y == cls)[0]
        rng.shuffle(idx)
        cut = int(round(len(idx) * (1 - test_size)))
        train_idx.extend(idx[:cut])
        test_idx.extend(idx[cut:])
    train_idx = np.array(train_idx)
    test_idx = np.array(test_idx)
    rng.shuffle(train_idx)
    rng.shuffle(test_idx)
    train = Dataset(ds.X[train_idx], ds.y[train_idx], ds.feature_names)
    test = Dataset(ds.X[test_idx], ds.y[test_idx], ds.feature_names)
    return train, test
