"""Free body diagram rendering with Matplotlib."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


# Colour palette for force arrows
COLORS = [
    "#e74c3c",  # red
    "#2ecc71",  # green
    "#3498db",  # blue
    "#f39c12",  # orange
    "#9b59b6",  # purple
    "#1abc9c",  # teal
    "#e67e22",  # dark orange
    "#2c3e50",  # navy
]


def _draw_force_arrow(ax, origin, magnitude, angle_deg, label, color, scale):
    """Draw a single labelled force arrow from `origin`."""
    angle_rad = np.radians(angle_deg)
    dx = magnitude * scale * np.cos(angle_rad)
    dy = magnitude * scale * np.sin(angle_rad)

    ax.annotate(
        "",
        xy=(origin[0] + dx, origin[1] + dy),
        xytext=origin,
        arrowprops=dict(arrowstyle="->", color=color, lw=2.5),
    )

    # Position label just past the arrowhead
    lx = origin[0] + dx * 1.18
    ly = origin[1] + dy * 1.18

    ax.text(
        lx, ly, label,
        ha="center", va="center",
        fontsize=9, fontweight="bold", color=color,
    )


def render_concurrent_forces(forces: list[dict], resultant: dict | None = None,
                             title: str = "Force Diagram") -> plt.Figure:
    """
    Draw forces radiating from a common point.

    Each entry in `forces`: {'name', 'magnitude', 'angle_deg'}
    `resultant` (optional): {'magnitude', 'angle_deg'}
    """
    fig, ax = plt.subplots(figsize=(7, 7))

    max_mag = max(f["magnitude"] for f in forces)
    scale = 3.0 / max_mag  # normalise longest arrow to ~3 units

    for i, f in enumerate(forces):
        color = COLORS[i % len(COLORS)]
        label = f"{f['name']}\n{f['magnitude']:.1f} N"
        _draw_force_arrow(ax, (0, 0), f["magnitude"], f["angle_deg"], label, color, scale)

    if resultant and resultant["magnitude"] > 0.001:
        label = f"R = {resultant['magnitude']:.1f} N\n({resultant['angle_deg']:.1f}°)"
        _draw_force_arrow(ax, (0, 0), resultant["magnitude"], resultant["angle_deg"],
                          label, "black", scale)

    span = max_mag * scale * 1.6
    ax.set_xlim(-span, span)
    ax.set_ylim(-span, span)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.2)
    ax.axhline(y=0, color="k", lw=0.5)
    ax.axvline(x=0, color="k", lw=0.5)
    ax.set_title(title, fontsize=14, fontweight="bold")
    plt.tight_layout()
    return fig


def render_flat_surface(forces: list[dict], title: str = "Free Body Diagram") -> plt.Figure:
    """
    Draw an object on a flat surface with force arrows.

    Each entry in `forces`: {'name', 'magnitude', 'angle_deg', 'color'}
    """
    fig, ax = plt.subplots(figsize=(7, 6))

    # Ground
    ax.plot([-1, 5], [0, 0], "k-", lw=3)
    # Hatching under ground
    for x in np.arange(-0.8, 5, 0.4):
        ax.plot([x, x - 0.3], [0, -0.25], "k-", lw=0.7, alpha=0.5)

    # Block
    bw, bh = 1.0, 0.8
    bx, by = 1.5, 0.0
    rect = patches.FancyBboxPatch(
        (bx, by), bw, bh,
        boxstyle="round,pad=0.04",
        facecolor="#3498db", edgecolor="black", lw=2,
    )
    ax.add_patch(rect)

    cx, cy = bx + bw / 2, by + bh / 2
    max_mag = max(f["magnitude"] for f in forces) if forces else 1
    scale = 1.8 / max_mag

    for i, f in enumerate(forces):
        color = f.get("color", COLORS[i % len(COLORS)])
        label = f"{f['name']} = {f['magnitude']:.1f} N"
        _draw_force_arrow(ax, (cx, cy), f["magnitude"], f["angle_deg"], label, color, scale)

    ax.set_xlim(-1.5, 6)
    ax.set_ylim(-1.5, 4.5)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.15)
    ax.set_title(title, fontsize=14, fontweight="bold")
    plt.tight_layout()
    return fig


def render_inclined_plane(forces: list[dict], incline_deg: float,
                          title: str = "Free Body Diagram") -> plt.Figure:
    """
    Draw an object on an inclined plane with force arrows.

    Forces use an absolute (global) angle convention:
      - 270° = straight down, 90° = straight up, etc.

    `incline_deg`: slope angle in degrees from horizontal.
    """
    fig, ax = plt.subplots(figsize=(8, 7))
    theta = np.radians(incline_deg)

    # Draw inclined plane
    plane_len = 6.5
    px = plane_len * np.cos(theta)
    py = plane_len * np.sin(theta)
    ax.fill([0, px, px, 0], [0, py, 0, 0], color="#d5dbdb", alpha=0.5)
    ax.plot([0, px], [0, py], "k-", linewidth=3)
    ax.plot([0, px], [0, 0], "k-", linewidth=1, alpha=0.4)

    # Angle arc
    arc_angles = np.linspace(0, theta, 40)
    arc_r = 1.0
    ax.plot(arc_r * np.cos(arc_angles), arc_r * np.sin(arc_angles), "k-", lw=1.5)
    ax.text(
        arc_r * 1.25 * np.cos(theta / 2),
        arc_r * 1.25 * np.sin(theta / 2) - 0.15,
        f"{incline_deg}°", fontsize=11,
    )

    # Block on slope
    dist_along = 3.0
    bx = dist_along * np.cos(theta)
    by = dist_along * np.sin(theta)

    block_size = 0.45
    block = patches.FancyBboxPatch(
        (bx - block_size / 2, by + 0.08),
        block_size, block_size,
        boxstyle="round,pad=0.04",
        facecolor="#3498db", edgecolor="black", lw=2,
    )
    ax.add_patch(block)

    cx, cy = bx, by + 0.08 + block_size / 2
    max_mag = max(f["magnitude"] for f in forces) if forces else 1
    scale = 2.0 / max_mag

    for i, f in enumerate(forces):
        color = f.get("color", COLORS[i % len(COLORS)])
        label = f"{f['name']} = {f['magnitude']:.1f} N"
        _draw_force_arrow(ax, (cx, cy), f["magnitude"], f["angle_deg"], label, color, scale)

    ax.set_xlim(-1.5, 8)
    ax.set_ylim(-1.5, 6.5)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.15)
    ax.set_title(title, fontsize=14, fontweight="bold")
    plt.tight_layout()
    return fig
