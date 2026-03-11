"""General-purpose symbolic equilibrium solver using SymPy."""

import sympy as sp


def solve_equilibrium(known: dict[str, float], unknowns: list[str],
                      equations: list) -> dict[str, float]:
    """
    Solve a system of equilibrium equations symbolically.

    Args:
        known: Dict of variable names to their known numeric values.
        unknowns: List of variable names to solve for.
        equations: List of SymPy Eq objects using Symbol names matching
                   the keys in `known` and `unknowns`.

    Returns:
        Dict mapping unknown names to their solved numeric values.
    """
    symbols_map = {name: sp.Symbol(name) for name in unknowns}

    subbed_eqs = []
    for eq in equations:
        for k, v in known.items():
            eq = eq.subs(sp.Symbol(k), v)
        subbed_eqs.append(eq)

    unknown_symbols = [symbols_map[u] for u in unknowns]
    solution = sp.solve(subbed_eqs, unknown_symbols, dict=True)

    if solution:
        return {str(k): float(v) for k, v in solution[0].items()}
    return {}
