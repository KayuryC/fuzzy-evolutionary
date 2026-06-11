"""Produto (Opcao B): interface de linha de comando para manutencao preditiva.

Recebe as 3 grandezas de operacao da maquina e devolve o indice de risco, o nivel
linguistico, uma recomendacao e (opcional) a explicacao das regras ativadas.

Exemplos:
    python -m src.cli --desgaste 200 --torque 60 --rotacao 1400
    python -m src.cli --desgaste 200 --torque 60 --rotacao 1400 --explain
    python -m src.cli --desgaste 200 --torque 60 --rotacao 1400 --optimized

Com --optimized, usa o modelo ajustado pelo AG (results/tables/best_ga_model.npz),
se existir; caso contrario, usa a sintonia manual.
"""
from __future__ import annotations

import argparse
import os

import numpy as np

from .fuzzy.system import build_default_system, build_param_spec, vector_to_system

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "results", "tables", "best_ga_model.npz")


def _nivel(risk: float) -> str:
    if risk < 35:
        return "BAIXA"
    if risk < 60:
        return "MODERADA"
    if risk < 80:
        return "ALTA"
    return "CRITICA"


def _recomendacao(nivel: str) -> str:
    return {
        "BAIXA": "Operacao normal. Manter monitoramento de rotina.",
        "MODERADA": "Programar inspecao na proxima janela de manutencao.",
        "ALTA": "Agendar manutencao preventiva em curto prazo.",
        "CRITICA": "Parada/intervencao imediata recomendada.",
    }[nivel]


def load_system(optimized: bool):
    """Constroi o sistema manual ou carrega o otimizado pelo AG."""
    system = build_default_system()
    if optimized and os.path.exists(_MODEL_PATH):
        data = np.load(_MODEL_PATH)
        spec = build_param_spec(system)
        system = vector_to_system(data["vector"], spec, base=system)
        print(f"[modelo otimizado por AG — F1 teste={float(data['f1_test']):.3f}]")
    elif optimized:
        print("[aviso: modelo otimizado nao encontrado; usando sintonia manual]")
    return system


def main(argv=None):
    p = argparse.ArgumentParser(description="Manutencao preditiva fuzzy (Mamdani).")
    p.add_argument("--desgaste", type=float, required=True, help="Tool wear [min] (0-260)")
    p.add_argument("--torque", type=float, required=True, help="Torque [Nm] (0-80)")
    p.add_argument("--rotacao", type=float, required=True, help="Rotacao [rpm] (1100-2900)")
    p.add_argument("--optimized", action="store_true", help="usar modelo ajustado por AG")
    p.add_argument("--explain", action="store_true", help="mostrar regras ativadas")
    args = p.parse_args(argv)

    system = load_system(args.optimized)
    info = system.explain_one(desgaste=args.desgaste, torque=args.torque, rotacao=args.rotacao)
    risk = info["risk"]
    nivel = _nivel(risk)

    print(f"\nEntradas: desgaste={args.desgaste:g} min | torque={args.torque:g} Nm | "
          f"rotacao={args.rotacao:g} rpm")
    print(f"Indice de risco : {risk:5.1f} / 100")
    print(f"Nivel           : {nivel}")
    print(f"Recomendacao    : {_recomendacao(nivel)}")

    if args.explain:
        print("\nPertinencias ativas:")
        for var, terms in info["memberships"].items():
            ativos = ", ".join(f"{t}={mu:.2f}" for t, mu in terms.items() if mu > 0.01)
            print(f"  {var:9s}: {ativos or '-'}")
        print("\nRegras mais ativadas:")
        for r in info["rules"][:4]:
            if r["ativacao"] > 0.01:
                print(f"  [{r['ativacao']:.2f}] SE {r['se']} ENTAO risco={r['entao']}")


if __name__ == "__main__":
    main()
