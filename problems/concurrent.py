"""Solver for concurrent forces acting at a point."""

import numpy as np

from models import SolverResult


def solve(forces: list[dict]) -> SolverResult:
    """
    Calculate the resultant of concurrent forces acting at a point.

    Args:
        forces: List of dicts, each with 'name', 'magnitude', 'angle_deg'.

    Returns:
        SolverResult with resultant force, equilibrium check, and diagram data.
    """
    sum_x = 0.0
    sum_y = 0.0
    steps = []

    for f in forces:
        angle_rad = np.radians(f["angle_deg"])
        fx = f["magnitude"] * np.cos(angle_rad)
        fy = f["magnitude"] * np.sin(angle_rad)
        sum_x += fx
        sum_y += fy
        steps.append(
            f"{f['name']}: Fx = {f['magnitude']:.2f} cos({f['angle_deg']}°) = {fx:.4f} N, "
            f"Fy = {f['magnitude']:.2f} sin({f['angle_deg']}°) = {fy:.4f} N"
        )

    resultant_mag = np.sqrt(sum_x ** 2 + sum_y ** 2)
    resultant_angle = np.degrees(np.arctan2(sum_y, sum_x))

    steps.append(f"ΣFx = {sum_x:.4f} N")
    steps.append(f"ΣFy = {sum_y:.4f} N")
    steps.append(f"|R| = √(ΣFx² + ΣFy²) = √({sum_x:.4f}² + {sum_y:.4f}²) = {resultant_mag:.4f} N")
    steps.append(f"θ_R = arctan(ΣFy / ΣFx) = arctan({sum_y:.4f} / {sum_x:.4f}) = {resultant_angle:.2f}°")

    equilibrium = bool(resultant_mag < 0.01)

    if equilibrium:
        status = "✅ Forces are in equilibrium (resultant ≈ 0)"
    else:
        eq_angle = (resultant_angle + 180) % 360
        status = (
            f"⚠️ Not in equilibrium — resultant = {resultant_mag:.2f} N at {resultant_angle:.1f}°. "
            f"Equilibrant = {resultant_mag:.2f} N at {eq_angle:.1f}°"
        )
        steps.append(f"Equilibrant: {resultant_mag:.4f} N at {eq_angle:.2f}°")

    values = {
        "ΣFx": sum_x,
        "ΣFy": sum_y,
        "Resultant magnitude": resultant_mag,
        "Resultant direction (°)": resultant_angle,
    }
    if not equilibrium:
        values["Equilibrant magnitude"] = resultant_mag
        values["Equilibrant direction (°)"] = (resultant_angle + 180) % 360

    # Diagram data — include each input force plus the resultant
    diagram_forces = list(forces)  # shallow copy

    return SolverResult(
        values=values,
        status=status,
        working_steps=steps,
        forces_for_diagram=diagram_forces,
        equilibrium=equilibrium,
    )
