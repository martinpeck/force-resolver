"""Solver for inclined-plane problems with optional friction and applied force."""

import numpy as np

from models import SolverResult


def solve(mass: float, g: float, incline_deg: float, mu: float,
          applied_mag: float = 0.0, applied_angle_deg: float = 0.0) -> SolverResult:
    """
    Solve a block-on-inclined-plane problem.

    Args:
        mass: Mass of the object in kg.
        g: Gravitational acceleration (m/s²).
        incline_deg: Angle of the plane from horizontal in degrees.
        mu: Coefficient of friction.
        applied_mag: Magnitude of an additional applied force (N).
        applied_angle_deg: Direction of the applied force in degrees measured
                           from the slope surface (positive = away from slope).

    Returns:
        SolverResult with all computed values, working steps, and diagram data.
    """
    theta = np.radians(incline_deg)
    W = mass * g

    # Weight components resolved relative to the slope
    W_parallel = W * np.sin(theta)       # component down the slope
    W_perpendicular = W * np.cos(theta)  # component into the slope

    # Applied force components (relative to slope)
    app_rad = np.radians(applied_angle_deg)
    F_app_parallel = applied_mag * np.cos(app_rad)       # along slope (up = +ve)
    F_app_perpendicular = applied_mag * np.sin(app_rad)  # away from slope

    # Normal reaction
    N = W_perpendicular - F_app_perpendicular
    if N < 0:
        N = 0  # object lifts off

    # Maximum available friction
    F_max = mu * N

    # Net force trying to move the block down the slope
    net_down_slope = W_parallel - F_app_parallel

    # Determine friction and equilibrium status
    if net_down_slope <= 0:
        status = "✅ Applied force pushes block UP the slope — friction acts down the slope"
        F_friction = abs(net_down_slope)
        friction_up_slope = False
        equilibrium = F_friction <= F_max
    elif abs(net_down_slope) <= F_max:
        status = "✅ In equilibrium — friction is sufficient to prevent sliding"
        F_friction = net_down_slope
        friction_up_slope = True
        equilibrium = True
    else:
        status = "⚠️ NOT in equilibrium — the block will slide down the slope"
        F_friction = F_max
        friction_up_slope = True
        equilibrium = False

    # Build working steps
    steps = [
        f"W = mg = {mass} × {g} = {W:.2f} N",
        f"W‖ = W sin θ = {W:.2f} × sin({incline_deg}°) = {W_parallel:.2f} N",
        f"W⊥ = W cos θ = {W:.2f} × cos({incline_deg}°) = {W_perpendicular:.2f} N",
    ]
    if applied_mag > 0:
        steps.append(f"F_app along slope = {applied_mag} × cos({applied_angle_deg}°) = {F_app_parallel:.2f} N")
        steps.append(f"F_app away from slope = {applied_mag} × sin({applied_angle_deg}°) = {F_app_perpendicular:.2f} N")
    steps += [
        f"R = W⊥ − F_app⊥ = {W_perpendicular:.2f} − {F_app_perpendicular:.2f} = {N:.2f} N",
        f"F_max = μR = {mu} × {N:.2f} = {F_max:.2f} N",
        f"Net force down slope = W‖ − F_app‖ = {W_parallel:.2f} − {F_app_parallel:.2f} = {net_down_slope:.2f} N",
        f"Friction required = {abs(net_down_slope):.2f} N, max available = {F_max:.2f} N",
        status,
    ]

    # Build forces for diagram (using global/absolute angles)
    # Weight: straight down → 270°
    # Normal: perpendicular to slope, outward → (90 + incline_deg)°
    # Friction: along slope → up-slope or down-slope
    up_slope_angle = 180 - incline_deg
    down_slope_angle = 360 - incline_deg

    diagram_forces = [
        {"name": "W", "magnitude": W, "angle_deg": 270, "color": "#e74c3c"},
        {"name": "R", "magnitude": N, "angle_deg": 90 + incline_deg, "color": "#2ecc71"},
    ]

    if F_friction > 0.01:
        fr_angle = up_slope_angle if friction_up_slope else down_slope_angle
        diagram_forces.append(
            {"name": "Fr", "magnitude": F_friction, "angle_deg": fr_angle, "color": "#f39c12"}
        )

    if applied_mag > 0:
        # Applied force angle is given relative to slope; convert to global
        global_applied_angle = (180 - incline_deg) + applied_angle_deg
        diagram_forces.append(
            {"name": "F_app", "magnitude": applied_mag,
             "angle_deg": global_applied_angle, "color": "#9b59b6"}
        )

    values = {
        "Weight (W)": W,
        "W parallel to slope": W_parallel,
        "W perpendicular to slope": W_perpendicular,
        "Normal reaction (R)": N,
        "Max friction (μR)": F_max,
        "Actual friction": F_friction,
        "Net force down slope": net_down_slope,
    }
    if applied_mag > 0:
        values["Applied force (along slope)"] = F_app_parallel
        values["Applied force (away from slope)"] = F_app_perpendicular

    return SolverResult(
        values=values,
        status=status,
        working_steps=steps,
        forces_for_diagram=diagram_forces,
        equilibrium=equilibrium,
    )
