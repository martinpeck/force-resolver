"""Solver for an object on a flat rough surface with an applied force."""

import numpy as np

from models import SolverResult


def solve(mass: float, g: float, mu: float,
          applied_force: float, applied_angle_deg: float) -> SolverResult:
    """
    Solve for equilibrium of an object on a flat rough surface.

    Args:
        mass: Mass of the object (kg).
        g: Gravitational acceleration (m/s²).
        mu: Coefficient of friction.
        applied_force: Magnitude of the applied force (N).
        applied_angle_deg: Angle of the applied force above the horizontal (degrees).

    Returns:
        SolverResult with all computed values, working steps, and diagram data.
    """
    angle_rad = np.radians(applied_angle_deg)
    W = mass * g

    F_horizontal = applied_force * np.cos(angle_rad)
    F_vertical = applied_force * np.sin(angle_rad)

    # Normal reaction (weight minus upward component of applied force)
    N = W - F_vertical
    if N < 0:
        N = 0  # object lifts off the surface

    F_max = mu * N

    if F_horizontal <= F_max:
        F_friction = F_horizontal
        status = "✅ In equilibrium — friction is sufficient to hold the object"
        equilibrium = True
    else:
        F_friction = F_max
        net_force = F_horizontal - F_max
        accel = net_force / mass
        status = (
            f"⚠️ Not in equilibrium — the object accelerates at {accel:.2f} m/s² "
            f"(net horizontal force = {net_force:.2f} N)"
        )
        equilibrium = False

    steps = [
        f"W = mg = {mass} × {g} = {W:.2f} N",
        f"F_horizontal = F cos θ = {applied_force:.2f} × cos({applied_angle_deg}°) = {F_horizontal:.2f} N",
        f"F_vertical = F sin θ = {applied_force:.2f} × sin({applied_angle_deg}°) = {F_vertical:.2f} N",
        f"R = W − F_vertical = {W:.2f} − {F_vertical:.2f} = {N:.2f} N",
        f"F_max = μR = {mu} × {N:.2f} = {F_max:.2f} N",
        f"Friction required = F_horizontal = {F_horizontal:.2f} N",
        f"Max friction available = {F_max:.2f} N",
        status,
    ]

    values = {
        "Weight (W)": W,
        "Horizontal component of applied force": F_horizontal,
        "Vertical component of applied force": F_vertical,
        "Normal reaction (R)": N,
        "Max friction available (μR)": F_max,
        "Actual friction force": F_friction,
    }

    # Diagram forces (global angles: 0°=right, 90°=up, 270°=down, 180°=left)
    diagram_forces = [
        {"name": "W", "magnitude": W, "angle_deg": 270, "color": "#e74c3c"},
        {"name": "R", "magnitude": N, "angle_deg": 90, "color": "#2ecc71"},
        {"name": "F", "magnitude": applied_force, "angle_deg": applied_angle_deg, "color": "#3498db"},
    ]
    if F_friction > 0.01:
        diagram_forces.append(
            {"name": "Fr", "magnitude": F_friction, "angle_deg": 180, "color": "#f39c12"}
        )

    return SolverResult(
        values=values,
        status=status,
        working_steps=steps,
        forces_for_diagram=diagram_forces,
        equilibrium=equilibrium,
    )
