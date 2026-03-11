# Building a Static Force Resolution Tool: Comprehensive Research Report

## Executive Summary

You want a tool where you can input forces (magnitudes, angles), distances, coefficients of friction, and inclined plane angles, and have it **solve for unknowns** (reaction forces, friction forces, tensions, etc.) and **illustrate the result** with a free-body diagram. This is a well-scoped project that maps directly onto A-level mechanics topics: resolving forces into components, applying equilibrium conditions (ΣFx = 0, ΣFy = 0, ΣM = 0), and modelling friction (F ≤ μR).

The best approach is a **Python application** using **SymPy** for symbolic equation solving, **NumPy** for numerical computation, and **Matplotlib** (or the `pyfreebody` library) for force-diagram visualisation. For the user interface, **Streamlit** provides the fastest path to an interactive web-based tool that runs locally, while **Tkinter** is a viable desktop alternative. This report covers the full technology landscape, mathematical foundations, architecture options, and working code examples.

---

## 1. The Problem Domain: A-Level Mechanics Statics

### 1.1 Core Problem Types

The tool needs to handle these standard problem categories[^1][^2]:

| Problem Type | Inputs | Unknowns to Solve |
|---|---|---|
| **Concurrent forces at a point** | Multiple forces with magnitudes/angles | Resultant force, equilibrium conditions |
| **Inclined plane (no friction)** | Mass, plane angle, gravity | Normal reaction, component forces |
| **Inclined plane with friction** | Mass, plane angle, μ (coefficient of friction) | Normal reaction, friction force, whether body slides |
| **Object with applied force on rough surface** | Applied force, angle, mass, μ | Friction, normal reaction, acceleration/equilibrium |
| **Particle on rough inclined plane with applied force** | Mass, plane angle, μ, applied force magnitude/direction | Unknown forces, limiting equilibrium conditions |
| **Connected particles / pulleys** | Masses, angles, μ | Tensions, accelerations |

### 1.2 Mathematical Foundation

Every statics problem reduces to these equilibrium equations[^3]:

**Translational equilibrium:**
```
ΣFx = 0   (sum of horizontal force components = 0)
ΣFy = 0   (sum of vertical force components = 0)
```

**Rotational equilibrium (for rigid bodies):**
```
ΣM = 0    (sum of moments about any point = 0)
```

**Friction model:**
```
F_friction ≤ μR        (friction cannot exceed μ × normal reaction)
F_friction = μR        (at limiting equilibrium / point of sliding)
```

**Force resolution into components:**
```
Fx = F × cos(θ)
Fy = F × sin(θ)
```

For an inclined plane at angle θ, weight W = mg resolves to:
```
Component parallel to plane:       W sin(θ)
Component perpendicular to plane:  W cos(θ)
```

---

## 2. Technology Stack Recommendations

### 2.1 Recommended Stack (Primary)

| Layer | Technology | Why |
|---|---|---|
| **Equation solving** | SymPy | Symbolic maths — solves equations analytically, handles unknowns naturally |
| **Numerical computation** | NumPy | Fast numerical linear algebra, matrix equation solving |
| **Visualisation** | Matplotlib (`quiver` for vectors) + `pyfreebody` | Force arrows, labelled diagrams, inclined plane rendering |
| **User interface** | Streamlit | Zero-config interactive web UI, sliders/inputs, runs locally |
| **Language** | Python 3.10+ | Ecosystem support, student-friendly |

### 2.2 Alternative Stacks

| Stack | Pros | Cons |
|---|---|---|
| **Python + Tkinter** | No web server needed, desktop native | Less polished UI, Canvas drawing is manual |
| **Python + Gradio** | Very simple function→UI mapping | Less flexible layout than Streamlit |
| **JavaScript + HTML Canvas** | Runs in any browser, shareable | Must reimplement maths solving, no SymPy equivalent |
| **Jupyter Notebook** | Great for exploration, inline plots | Not a standalone "tool" — more of a worksheet |

**Recommendation**: Use **Streamlit + SymPy + Matplotlib** for the best balance of power, ease of development, and user experience.

---

## 3. Key Libraries in Detail

### 3.1 SymPy — Symbolic Equation Solving

SymPy is the core of the solving engine. It lets you define unknowns as symbols, build equations, and solve them analytically[^4].

**Why SymPy over NumPy for this project:**
- You often don't know *which* variables are unknown until the user specifies the problem
- SymPy gives exact symbolic answers (e.g., `μ = tan(θ)`) not just floating-point approximations
- It handles trigonometric simplification automatically

**Example — solving an inclined plane problem symbolically:**

```python
import sympy as sp

# Define symbols
m, g, theta, N, mu, F_friction = sp.symbols('m g theta N mu F_friction', positive=True)

# Equilibrium perpendicular to plane: N = mg cos(θ)
eq1 = sp.Eq(N, m * g * sp.cos(theta))

# Equilibrium parallel to plane: F_friction = mg sin(θ)
eq2 = sp.Eq(F_friction, m * g * sp.sin(theta))

# Limiting friction: F_friction = μN
eq3 = sp.Eq(F_friction, mu * N)

# Solve for μ in terms of θ (classic result: μ = tan θ)
solution = sp.solve([eq1, eq2, eq3], [N, F_friction, mu])
print(solution)
# Output: {N: g*m*cos(theta), F_friction: g*m*sin(theta), mu: tan(theta)}
```

**Substituting numerical values:**

```python
# Plug in specific values
numerical = {m: 10, g: 9.8, theta: sp.rad(30)}
N_val = solution[N].subs(numerical)
F_val = solution[F_friction].subs(numerical)
mu_val = solution[mu].subs(numerical)
print(f"N = {float(N_val):.2f} N")        # 84.87 N
print(f"F = {float(F_val):.2f} N")        # 49.00 N
print(f"μ = {float(mu_val):.4f}")          # 0.5774
```

[^4]: [SymPy Solve documentation](https://docs.sympy.org/latest/guides/solving/index.html)

### 3.2 NumPy — Numerical Linear Algebra

For problems that reduce to a system of linear equations (e.g., multiple cables/forces with known angles), NumPy's `linalg.solve` is fast and direct[^5][^6]:

```python
import numpy as np

# Example: Three forces at known angles must sum to zero
# F1 at 0°, F2 at 120°, F3 at 240°, with 100N weight downward
# ΣFx = 0:  F1 + F2·cos(120°) + F3·cos(240°) = 0
# ΣFy = 0:  F2·sin(120°) + F3·sin(240°) = 100

A = np.array([
    [1, np.cos(np.radians(120)), np.cos(np.radians(240))],
    [0, np.sin(np.radians(120)), np.sin(np.radians(240))],
    [1, -1, 0]  # symmetry constraint: F1 = F2
])
b = np.array([0, 100, 0])

forces = np.linalg.solve(A, b)
print(f"F1 = {forces[0]:.2f} N, F2 = {forces[1]:.2f} N, F3 = {forces[2]:.2f} N")
```

[^5]: [NumPy linalg.solve documentation](https://numpy.org/doc/stable/reference/generated/numpy.linalg.solve.html)
[^6]: [NumPy static equilibrium tutorial](https://github.com/numpy/numpy-tutorials/blob/main/content/tutorial-static_equilibrium.md)

### 3.3 Matplotlib — Force Vector Visualisation

Use `matplotlib.pyplot.quiver` to draw force arrows from a common point[^7]:

```python
import matplotlib.pyplot as plt
import numpy as np

def draw_force_diagram(forces, title="Free Body Diagram"):
    """
    forces: list of dicts with keys 'name', 'magnitude', 'angle_deg', 'color'
    """
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))

    for f in forces:
        angle_rad = np.radians(f['angle_deg'])
        dx = f['magnitude'] * np.cos(angle_rad)
        dy = f['magnitude'] * np.sin(angle_rad)
        ax.quiver(0, 0, dx, dy, angles='xy', scale_units='xy', scale=1,
                  color=f.get('color', 'blue'), width=0.02)
        ax.text(dx * 1.15, dy * 1.15, f"{f['name']}\n{f['magnitude']:.1f} N",
                ha='center', fontsize=10, color=f.get('color', 'blue'))

    max_mag = max(f['magnitude'] for f in forces) * 1.5
    ax.set_xlim(-max_mag, max_mag)
    ax.set_ylim(-max_mag, max_mag)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.axvline(x=0, color='k', linewidth=0.5)
    ax.set_title(title)
    ax.set_xlabel('x (N)')
    ax.set_ylabel('y (N)')
    plt.tight_layout()
    return fig
```

[^7]: [Matplotlib quiver plot documentation](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.quiver.html)

### 3.4 pyfreebody — Dedicated Free Body Diagram Package

The `pyfreebody` package provides a higher-level API specifically for generating free-body diagrams, including inclined plane support[^8][^9]:

```python
from pyfreebody import Freebody, Direction, SystemType

# Flat surface example
fb = Freebody(name="Block", mass=10)
fb.addForce(name="Weight", magnitude=98.1, theta=Direction.down)
fb.addForce(name="Normal", magnitude=98.1, theta=Direction.up)
fb.addForce(name="Applied", magnitude=50, theta=45)  # 45° above horizontal
fb.addForce(name="Friction", magnitude=30, theta=Direction.left)
fb.diagram()

# Inclined plane example
import math
theta = math.radians(30)
fb2 = Freebody(name="BoxOnSlope", mass=5, sysType=SystemType.inclinedPlane, incline=theta)
fb2.addForce(name="Weight", magnitude=49.05, theta=Direction.down)
fb2.addForce(name="Normal", magnitude=42.5, theta=Direction.perpendicular)
fb2.addForce(name="Friction", magnitude=24.5, theta=Direction.up)  # up the slope
fb2.diagram()
```

Install: `pip install pyfreebody`

[^8]: [pyfreebody on GitHub](https://github.com/velocitatem/pyfreebody)
[^9]: [pyfreebody on PyPI](https://pypi.org/project/pyfreebody/)

---

## 4. Recommended Architecture

### 4.1 System Design

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit Web UI                     │
│  ┌───────────────┐  ┌────────────────────────────┐  │
│  │  Input Panel   │  │   Output Panel              │  │
│  │               │  │                              │  │
│  │ • Problem type│  │  • Solved values (table)     │  │
│  │ • Forces      │  │  • Step-by-step working      │  │
│  │ • Angles      │  │  • Free body diagram         │  │
│  │ • Mass        │  │  • Resultant force vector     │  │
│  │ • μ (friction)│  │                              │  │
│  │ • Unknowns    │  │                              │  │
│  └───────┬───────┘  └──────────────▲───────────────┘  │
│          │                         │                   │
│          ▼                         │                   │
│  ┌───────────────────────────────────────────────┐    │
│  │              Solver Engine                     │    │
│  │                                               │    │
│  │  ┌─────────────┐    ┌──────────────────────┐ │    │
│  │  │  SymPy       │    │  Matplotlib /        │ │    │
│  │  │  Equation    │───▶│  pyfreebody          │ │    │
│  │  │  Solver      │    │  Diagram Renderer    │ │    │
│  │  └─────────────┘    └──────────────────────┘ │    │
│  └───────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

### 4.2 Module Breakdown

The tool has three logical modules:

#### Module 1: Problem Model (`models.py`)
Defines the data structures for forces, surfaces, and problem configurations.

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class SurfaceType(Enum):
    FLAT = "flat"
    INCLINED = "inclined"

@dataclass
class Force:
    name: str
    magnitude: Optional[float] = None  # None if unknown
    angle_deg: Optional[float] = None  # None if unknown
    is_unknown: bool = False

@dataclass
class Surface:
    type: SurfaceType = SurfaceType.FLAT
    angle_deg: float = 0.0             # incline angle
    mu: Optional[float] = None         # coefficient of friction (None = smooth)

@dataclass
class Problem:
    mass: Optional[float] = None       # kg (None if unknown)
    gravity: float = 9.8               # m/s²
    surface: Surface = field(default_factory=Surface)
    forces: list[Force] = field(default_factory=list)
    # Which quantities to solve for
    unknowns: list[str] = field(default_factory=list)
```

#### Module 2: Solver Engine (`solver.py`)
Uses SymPy to build and solve the equilibrium equations.

```python
import sympy as sp
from models import Problem, SurfaceType

def solve_problem(problem: Problem) -> dict:
    """
    Build equilibrium equations from the problem description and solve.
    Returns a dict of {unknown_name: solved_value}.
    """
    # Create symbolic variables for all unknowns
    symbols_map = {}
    for f in problem.forces:
        if f.magnitude is None:
            symbols_map[f"{f.name}_mag"] = sp.Symbol(f"{f.name}_mag", positive=True)
        if f.angle_deg is None:
            symbols_map[f"{f.name}_angle"] = sp.Symbol(f"{f.name}_angle")

    if problem.surface.mu is None and problem.surface.type == SurfaceType.INCLINED:
        symbols_map["mu"] = sp.Symbol("mu", positive=True)

    # Build force component sums
    sum_fx = sp.Integer(0)
    sum_fy = sp.Integer(0)

    for f in problem.forces:
        mag = symbols_map.get(f"{f.name}_mag", f.magnitude)
        angle = symbols_map.get(f"{f.name}_angle", f.angle_deg)

        if isinstance(angle, (int, float)):
            angle_rad = sp.rad(angle)
        else:
            angle_rad = sp.rad(angle)

        sum_fx += mag * sp.cos(angle_rad)
        sum_fy += mag * sp.sin(angle_rad)

    # Equilibrium equations
    equations = [sp.Eq(sum_fx, 0), sp.Eq(sum_fy, 0)]

    # Add friction constraint if applicable
    if "mu" in symbols_map:
        # F_friction = mu * N at limiting equilibrium
        # This depends on which forces are friction/normal — needs problem-specific logic
        pass

    # Solve
    unknowns = list(symbols_map.values())
    solution = sp.solve(equations, unknowns, dict=True)

    if solution:
        return {str(k): float(v) for k, v in solution[0].items()}
    return {}
```

#### Module 3: Diagram Renderer (`diagram.py`)
Generates the free-body diagram visualisation.

```python
import matplotlib.pyplot as plt
import numpy as np

def render_force_diagram(forces_data: list[dict], title: str = "Free Body Diagram",
                         incline_angle: float = 0) -> plt.Figure:
    """
    Render a free body diagram with labelled force arrows.

    forces_data: list of {'name': str, 'magnitude': float, 'angle_deg': float}
    incline_angle: degrees, for drawing the inclined surface
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # Draw surface
    if incline_angle > 0:
        # Draw inclined plane
        length = 4
        angle_rad = np.radians(incline_angle)
        ax.plot([0, length * np.cos(angle_rad)], [0, length * np.sin(angle_rad)],
                'k-', linewidth=3)
        ax.plot([0, length * np.cos(angle_rad)], [0, 0], 'k--', linewidth=1, alpha=0.5)
        # angle arc
        arc_angles = np.linspace(0, angle_rad, 30)
        arc_r = 0.8
        ax.plot(arc_r * np.cos(arc_angles), arc_r * np.sin(arc_angles), 'k-', linewidth=1)
        ax.text(arc_r * 1.3, 0.15, f"{incline_angle}°", fontsize=11)

    # Draw force arrows from the object's position
    cx, cy = 2, 2  # centre of object
    colors = ['#e74c3c', '#2ecc71', '#3498db', '#f39c12', '#9b59b6', '#1abc9c']

    for i, f in enumerate(forces_data):
        angle_rad = np.radians(f['angle_deg'])
        scale = 0.03  # arrow length per Newton
        dx = f['magnitude'] * scale * np.cos(angle_rad)
        dy = f['magnitude'] * scale * np.sin(angle_rad)
        color = colors[i % len(colors)]

        ax.annotate('', xy=(cx + dx, cy + dy), xytext=(cx, cy),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2.5))
        ax.text(cx + dx * 1.2, cy + dy * 1.2,
                f"{f['name']}\n{f['magnitude']:.1f} N",
                ha='center', va='center', fontsize=9, fontweight='bold', color=color)

    # Draw object
    rect = plt.Rectangle((cx - 0.3, cy - 0.3), 0.6, 0.6,
                          fill=True, facecolor='#ecf0f1', edgecolor='black', linewidth=2)
    ax.add_patch(rect)

    ax.set_xlim(-1, 6)
    ax.set_ylim(-1, 6)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2)
    ax.set_title(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig
```

---

## 5. Complete Working Example: Streamlit App

Here is a complete, runnable Streamlit application that solves inclined-plane-with-friction problems:

### 5.1 Installation

```bash
pip install streamlit sympy numpy matplotlib
```

### 5.2 Full Application Code (`app.py`)

```python
import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Force Resolver", layout="wide")
st.title("⚡ Force Resolver — Static Equilibrium Solver")
st.markdown("Solve forces on inclined planes, flat surfaces, and concurrent force problems.")

# --- Sidebar: Problem Configuration ---
st.sidebar.header("Problem Setup")

problem_type = st.sidebar.selectbox("Problem Type", [
    "Inclined plane with friction",
    "Concurrent forces at a point",
    "Object on flat rough surface",
])

if problem_type == "Inclined plane with friction":
    st.sidebar.subheader("Parameters")
    mass = st.sidebar.number_input("Mass (kg)", min_value=0.1, value=10.0, step=0.1)
    g = st.sidebar.number_input("Gravity (m/s²)", value=9.8, step=0.1)
    theta_deg = st.sidebar.slider("Plane angle (degrees)", 0, 89, 30)
    mu = st.sidebar.number_input("Coefficient of friction (μ)", min_value=0.0,
                                  max_value=2.0, value=0.3, step=0.01)
    has_applied_force = st.sidebar.checkbox("Add an applied force?")
    applied_mag = 0
    applied_angle = 0
    if has_applied_force:
        applied_mag = st.sidebar.number_input("Applied force magnitude (N)",
                                               min_value=0.0, value=20.0)
        applied_angle = st.sidebar.number_input("Applied force angle (° from slope upward)",
                                                 value=0.0)

    # --- Solve ---
    if st.sidebar.button("🔍 Solve", type="primary") or True:
        theta_rad = np.radians(theta_deg)
        W = mass * g

        # Weight components (relative to slope)
        W_parallel = W * np.sin(theta_rad)      # down the slope
        W_perpendicular = W * np.cos(theta_rad)  # into the slope

        # Applied force components (if any)
        if has_applied_force:
            app_rad = np.radians(applied_angle)
            F_app_parallel = applied_mag * np.cos(app_rad)     # up the slope
            F_app_perpendicular = applied_mag * np.sin(app_rad) # away from slope
        else:
            F_app_parallel = 0
            F_app_perpendicular = 0

        # Normal reaction: N = W_perp - F_app_perp (net into surface)
        N = W_perpendicular - F_app_perpendicular

        # Maximum friction available
        F_max = mu * N

        # Net force trying to slide the block down the slope
        net_down_slope = W_parallel - F_app_parallel

        # Determine equilibrium
        if net_down_slope <= 0:
            status = "✅ Applied force pushes block UP the slope — friction acts downward"
            F_friction = abs(net_down_slope)
            friction_direction = "down the slope"
        elif abs(net_down_slope) <= F_max:
            status = "✅ In equilibrium — friction is sufficient"
            F_friction = net_down_slope
            friction_direction = "up the slope"
        else:
            status = "⚠️ NOT in equilibrium — block will slide down!"
            F_friction = F_max
            friction_direction = "up the slope (limiting)"

        # --- Display Results ---
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📊 Solution")
            st.info(status)

            results = {
                "Weight (W)": f"{W:.2f} N",
                "W parallel to slope": f"{W_parallel:.2f} N",
                "W perpendicular to slope": f"{W_perpendicular:.2f} N",
                "Normal reaction (N)": f"{N:.2f} N",
                "Friction required": f"{net_down_slope:.2f} N",
                "Max friction available (μN)": f"{F_max:.2f} N",
                "Actual friction force": f"{F_friction:.2f} N ({friction_direction})",
            }
            if has_applied_force:
                results["Applied force (parallel)"] = f"{F_app_parallel:.2f} N"
                results["Applied force (perpendicular)"] = f"{F_app_perpendicular:.2f} N"

            for label, value in results.items():
                st.write(f"**{label}:** {value}")

            # Step-by-step working
            st.subheader("📝 Working")
            st.latex(r"W = mg = " + f"{mass}" + r" \times " + f"{g}" + f" = {W:.2f}" + r"\text{{ N}}")
            st.latex(r"W_{\parallel} = W\sin\theta = " + f"{W:.2f}" + r"\sin(" + f"{theta_deg}°" + f") = {W_parallel:.2f}" + r"\text{{ N}}")
            st.latex(r"W_{\perp} = W\cos\theta = " + f"{W:.2f}" + r"\cos(" + f"{theta_deg}°" + f") = {W_perpendicular:.2f}" + r"\text{{ N}}")
            st.latex(r"R = W_{\perp} = " + f"{N:.2f}" + r"\text{{ N}}")
            st.latex(r"F_{max} = \mu R = " + f"{mu}" + r" \times " + f"{N:.2f} = {F_max:.2f}" + r"\text{{ N}}")

        with col2:
            st.subheader("📐 Free Body Diagram")

            fig, ax = plt.subplots(figsize=(7, 7))
            ax.set_xlim(-2, 8)
            ax.set_ylim(-2, 8)
            ax.set_aspect('equal')

            # Draw inclined plane
            plane_len = 7
            px = plane_len * np.cos(theta_rad)
            py = plane_len * np.sin(theta_rad)
            ax.fill([0, px, px, 0], [0, py, 0, 0], color='#d5dbdb', alpha=0.5)
            ax.plot([0, px], [0, py], 'k-', linewidth=3)

            # Angle arc
            arc_angles = np.linspace(0, theta_rad, 30)
            arc_r = 1.2
            ax.plot(arc_r * np.cos(arc_angles), arc_r * np.sin(arc_angles), 'k-', lw=1.5)
            ax.text(arc_r * 1.1 * np.cos(theta_rad / 2),
                    arc_r * 1.1 * np.sin(theta_rad / 2) - 0.2,
                    f"{theta_deg}°", fontsize=12)

            # Block position on slope
            bx = 3 * np.cos(theta_rad)
            by = 3 * np.sin(theta_rad)

            # Draw block
            block_size = 0.5
            block = patches.FancyBboxPatch((bx - block_size/2, by - block_size/2 + 0.2),
                                            block_size, block_size,
                                            boxstyle="round,pad=0.05",
                                            facecolor='#3498db', edgecolor='black', lw=2)
            ax.add_patch(block)

            # Force arrows (all from centre of block)
            arrow_scale = 0.03
            cx, cy = bx, by + 0.2

            # Weight (straight down)
            ax.annotate('', xy=(cx, cy - W * arrow_scale),
                        xytext=(cx, cy),
                        arrowprops=dict(arrowstyle='->', color='red', lw=2.5))
            ax.text(cx + 0.3, cy - W * arrow_scale - 0.3,
                    f"W = {W:.1f} N", color='red', fontsize=9, fontweight='bold')

            # Normal reaction (perpendicular to slope, outward)
            nx_dir = -np.sin(theta_rad)
            ny_dir = np.cos(theta_rad)
            ax.annotate('', xy=(cx + N * arrow_scale * nx_dir, cy + N * arrow_scale * ny_dir),
                        xytext=(cx, cy),
                        arrowprops=dict(arrowstyle='->', color='green', lw=2.5))
            ax.text(cx + N * arrow_scale * nx_dir - 0.8,
                    cy + N * arrow_scale * ny_dir + 0.2,
                    f"R = {N:.1f} N", color='green', fontsize=9, fontweight='bold')

            # Friction (along slope, upward)
            fx_dir = np.cos(theta_rad)
            fy_dir = np.sin(theta_rad)
            if friction_direction.startswith("down"):
                fx_dir, fy_dir = -fx_dir, -fy_dir
            ax.annotate('',
                        xy=(cx + F_friction * arrow_scale * fx_dir,
                            cy + F_friction * arrow_scale * fy_dir),
                        xytext=(cx, cy),
                        arrowprops=dict(arrowstyle='->', color='orange', lw=2.5))
            ax.text(cx + F_friction * arrow_scale * fx_dir + 0.3,
                    cy + F_friction * arrow_scale * fy_dir + 0.3,
                    f"F = {F_friction:.1f} N", color='orange', fontsize=9, fontweight='bold')

            ax.set_title("Free Body Diagram", fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.15)
            st.pyplot(fig)

elif problem_type == "Concurrent forces at a point":
    st.sidebar.subheader("Enter Forces")
    num_forces = st.sidebar.number_input("Number of known forces", min_value=1, max_value=10, value=3)

    forces = []
    for i in range(int(num_forces)):
        st.sidebar.markdown(f"**Force {i+1}**")
        mag = st.sidebar.number_input(f"Magnitude (N)", key=f"mag_{i}", value=10.0)
        angle = st.sidebar.number_input(f"Angle (° from +x axis)", key=f"ang_{i}", value=i * 120.0)
        forces.append({"name": f"F{i+1}", "magnitude": mag, "angle_deg": angle})

    if st.sidebar.button("🔍 Calculate Resultant", type="primary") or True:
        # Calculate resultant
        sum_x = sum(f['magnitude'] * np.cos(np.radians(f['angle_deg'])) for f in forces)
        sum_y = sum(f['magnitude'] * np.sin(np.radians(f['angle_deg'])) for f in forces)
        resultant_mag = np.sqrt(sum_x**2 + sum_y**2)
        resultant_angle = np.degrees(np.arctan2(sum_y, sum_x))

        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("📊 Results")
            st.write(f"**ΣFx** = {sum_x:.4f} N")
            st.write(f"**ΣFy** = {sum_y:.4f} N")
            st.write(f"**Resultant magnitude** = {resultant_mag:.4f} N")
            st.write(f"**Resultant direction** = {resultant_angle:.2f}°")

            if resultant_mag < 0.001:
                st.success("✅ Forces are in equilibrium!")
            else:
                st.warning(f"⚠️ Net force of {resultant_mag:.2f} N at {resultant_angle:.1f}°")
                st.write(f"**Equilibrant** = {resultant_mag:.4f} N at {resultant_angle + 180:.2f}°")

        with col2:
            st.subheader("📐 Force Diagram")
            fig, ax = plt.subplots(figsize=(7, 7))
            colors = ['#e74c3c', '#2ecc71', '#3498db', '#f39c12', '#9b59b6',
                      '#1abc9c', '#e67e22', '#2c3e50', '#c0392b', '#16a085']

            max_mag = max(f['magnitude'] for f in forces) * 1.5
            for i, f in enumerate(forces):
                angle_rad = np.radians(f['angle_deg'])
                dx = f['magnitude'] * np.cos(angle_rad)
                dy = f['magnitude'] * np.sin(angle_rad)
                color = colors[i % len(colors)]
                ax.quiver(0, 0, dx, dy, angles='xy', scale_units='xy', scale=1,
                          color=color, width=0.015, zorder=3)
                ax.text(dx * 1.15, dy * 1.15,
                        f"{f['name']}: {f['magnitude']:.1f} N\n({f['angle_deg']}°)",
                        color=color, fontsize=9, ha='center', fontweight='bold')

            # Draw resultant
            if resultant_mag > 0.001:
                ax.quiver(0, 0, sum_x, sum_y, angles='xy', scale_units='xy', scale=1,
                          color='black', width=0.02, linestyle='--', zorder=4)
                ax.text(sum_x * 1.15, sum_y * 1.15,
                        f"R = {resultant_mag:.1f} N\n({resultant_angle:.1f}°)",
                        color='black', fontsize=10, ha='center', fontweight='bold')

            ax.set_xlim(-max_mag, max_mag)
            ax.set_ylim(-max_mag, max_mag)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='k', lw=0.5)
            ax.axvline(x=0, color='k', lw=0.5)
            ax.set_title("Force Diagram", fontsize=14, fontweight='bold')
            st.pyplot(fig)

elif problem_type == "Object on flat rough surface":
    st.sidebar.subheader("Parameters")
    mass = st.sidebar.number_input("Mass (kg)", min_value=0.1, value=5.0)
    g = st.sidebar.number_input("Gravity (m/s²)", value=9.8)
    mu = st.sidebar.number_input("Coefficient of friction (μ)", min_value=0.0, value=0.4)
    applied_force = st.sidebar.number_input("Applied force (N)", min_value=0.0, value=30.0)
    applied_angle = st.sidebar.number_input("Angle of applied force (° above horizontal)", value=25.0)

    if st.sidebar.button("🔍 Solve", type="primary") or True:
        angle_rad = np.radians(applied_angle)
        W = mass * g
        F_horizontal = applied_force * np.cos(angle_rad)
        F_vertical = applied_force * np.sin(angle_rad)

        # Normal reaction: W - F_vertical (upward applied component reduces N)
        N = W - F_vertical
        F_max = mu * N
        F_friction = min(F_horizontal, F_max)

        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("📊 Solution")
            if F_horizontal <= F_max:
                st.success("✅ In equilibrium — friction holds the object")
            else:
                st.warning("⚠️ Object will accelerate — applied force exceeds max friction")

            st.write(f"**Weight (W):** {W:.2f} N")
            st.write(f"**Applied horizontal component:** {F_horizontal:.2f} N")
            st.write(f"**Applied vertical component:** {F_vertical:.2f} N")
            st.write(f"**Normal reaction (R):** {N:.2f} N")
            st.write(f"**Max friction (μR):** {F_max:.2f} N")
            st.write(f"**Actual friction:** {F_friction:.2f} N")

        with col2:
            st.subheader("📐 Free Body Diagram")
            fig, ax = plt.subplots(figsize=(7, 5))
            ax.plot([-1, 5], [0, 0], 'k-', lw=3)  # ground
            rect = plt.Rectangle((1.5, 0), 1, 1, fill=True,
                                  facecolor='#3498db', edgecolor='black', lw=2)
            ax.add_patch(rect)
            cx, cy = 2, 0.5
            sc = 0.02

            # Weight
            ax.annotate('', xy=(cx, cy - W*sc), xytext=(cx, cy),
                        arrowprops=dict(arrowstyle='->', color='red', lw=2))
            ax.text(cx + 0.15, cy - W*sc - 0.15, f"W={W:.1f}N", color='red', fontsize=9)

            # Normal
            ax.annotate('', xy=(cx, cy + N*sc), xytext=(cx, cy),
                        arrowprops=dict(arrowstyle='->', color='green', lw=2))
            ax.text(cx + 0.15, cy + N*sc + 0.1, f"R={N:.1f}N", color='green', fontsize=9)

            # Applied force
            ax.annotate('', xy=(cx + applied_force*sc*np.cos(angle_rad),
                                cy + applied_force*sc*np.sin(angle_rad)),
                        xytext=(cx, cy),
                        arrowprops=dict(arrowstyle='->', color='blue', lw=2))
            ax.text(cx + applied_force*sc*np.cos(angle_rad) + 0.1,
                    cy + applied_force*sc*np.sin(angle_rad) + 0.1,
                    f"F={applied_force:.1f}N", color='blue', fontsize=9)

            # Friction
            ax.annotate('', xy=(cx - F_friction*sc, cy), xytext=(cx, cy),
                        arrowprops=dict(arrowstyle='->', color='orange', lw=2))
            ax.text(cx - F_friction*sc - 0.6, cy + 0.1,
                    f"Fr={F_friction:.1f}N", color='orange', fontsize=9)

            ax.set_xlim(-1, 5)
            ax.set_ylim(-2, 3)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.2)
            ax.set_title("Free Body Diagram", fontweight='bold')
            st.pyplot(fig)
```

### 5.3 Running the App

```bash
streamlit run app.py
```

This opens a browser window with the interactive tool at `http://localhost:8501`.

---

## 6. Extending the Tool

### 6.1 Adding More Problem Types

To add a new problem type (e.g., connected particles, beams, trusses):

1. **Add to the selectbox** in the sidebar
2. **Add input widgets** for the new problem's parameters
3. **Write the equilibrium equations** using SymPy or NumPy
4. **Render the diagram** with Matplotlib

### 6.2 Symbolic Solving for Arbitrary Unknowns

For more advanced use, let the user mark any variable as "unknown" and use SymPy to solve:

```python
import sympy as sp

def solve_general_equilibrium(known: dict, unknowns: list[str], equations: list) -> dict:
    """
    known: {'m': 10, 'g': 9.8, 'theta': 30, ...}
    unknowns: ['N', 'F_friction', 'mu']
    equations: list of SymPy Eq objects
    """
    symbols = {name: sp.Symbol(name) for name in unknowns}
    # Substitute known values
    subbed_eqs = []
    for eq in equations:
        for k, v in known.items():
            eq = eq.subs(sp.Symbol(k), v)
        subbed_eqs.append(eq)

    solution = sp.solve(subbed_eqs, [symbols[u] for u in unknowns], dict=True)
    if solution:
        return {str(k): float(v) for k, v in solution[0].items()}
    return {}
```

### 6.3 Moments / Turning Effects

Add moment calculations for rigid body problems:

```python
def calculate_moment(force_magnitude, perpendicular_distance, direction="clockwise"):
    """Calculate moment = F × d"""
    moment = force_magnitude * perpendicular_distance
    return moment if direction == "clockwise" else -moment
```

### 6.4 Alternative Visualisation with pyfreebody

If you want simpler diagram code, use the `pyfreebody` package instead of manual Matplotlib:

```bash
pip install pyfreebody
```

```python
from pyfreebody import Freebody, Direction
fb = Freebody(name="Block", mass=mass)
fb.addForce(name="Weight", magnitude=W, theta=Direction.down)
fb.addForce(name="Normal", magnitude=N, theta=Direction.up)
fb.addForce(name="Friction", magnitude=F_friction, theta=Direction.left)
fb.diagram()
```

---

## 7. Existing Tools and Alternatives

If you'd prefer to use or learn from existing tools rather than building from scratch:

| Tool | Type | What It Does | URL |
|---|---|---|---|
| **pyfreebody** | Python package | Generates free-body diagrams programmatically | [GitHub](https://github.com/velocitatem/pyfreebody) |
| **MechPy** | Python package | Statics calculations, shear/bending diagrams | [GitHub Pages](https://nagordon.github.io/mechpy/statics.html) |
| **IndeterminateBeam** | Python package | Beam analysis with reactions, shear, moment diagrams | [PyPI](https://pypi.org/project/indeterminatebeam/) |
| **Multi-Body Static Equilibrium Solver** | Python project | 3D multi-body equilibrium solver | [GitHub](https://github.com/ITregear/multi-body-static-equilibrium-solver) |
| **CalcForge** | Python framework | Collection of engineering calculators | [GitHub](https://github.com/slukiceng/CalcForge) |
| **Go Math Science FBD Creator** | Web tool | Interactive browser-based force diagram creator | [Website](https://go-math-science.com/tools/physics-tools/force-diagram-creator) |
| **MechEnSoft Statics Solver** | Web tool | Step-by-step statics problem solver | [Website](https://www.mechensoft.com/statics/) |
| **NumPy Statics Tutorial** | Tutorial | Jupyter notebook for equilibrium problems | [GitHub](https://github.com/numpy/numpy-tutorials/blob/main/content/tutorial-static_equilibrium.md) |

---

## 8. Project Structure Recommendation

```
force-resolver/
├── app.py                 # Streamlit entry point (UI)
├── solver.py              # SymPy equation solving engine
├── diagram.py             # Matplotlib diagram rendering
├── models.py              # Data classes (Force, Surface, Problem)
├── problems/
│   ├── inclined_plane.py  # Inclined plane solver
│   ├── concurrent.py      # Concurrent forces solver
│   ├── flat_surface.py    # Flat rough surface solver
│   └── moments.py         # Moments / rigid body solver
├── requirements.txt       # Dependencies
├── README.md
└── tests/
    ├── test_solver.py     # Unit tests for solver
    └── test_problems.py   # Specific problem regression tests
```

**`requirements.txt`:**
```
streamlit>=1.30
sympy>=1.12
numpy>=1.24
matplotlib>=3.7
```

---

## 9. Testing Strategy

Verify your solver against known textbook answers:

```python
# test_solver.py
import math

def test_inclined_plane_basic():
    """Block on 30° incline, mass 10kg, g=9.8"""
    m, g, theta = 10, 9.8, math.radians(30)
    W = m * g
    N = W * math.cos(theta)
    F_parallel = W * math.sin(theta)

    assert abs(N - 84.87) < 0.1, f"Normal force should be ~84.87, got {N}"
    assert abs(F_parallel - 49.0) < 0.1, f"Parallel force should be ~49.0, got {F_parallel}"

def test_limiting_friction():
    """At limiting equilibrium on 30° incline, μ = tan(30°)"""
    theta = math.radians(30)
    mu = math.tan(theta)
    assert abs(mu - 0.5774) < 0.001, f"μ should be ~0.577, got {mu}"

def test_concurrent_forces_equilibrium():
    """Three equal forces at 120° intervals should be in equilibrium"""
    import numpy as np
    angles = [0, 120, 240]
    F = 10
    sum_x = sum(F * np.cos(np.radians(a)) for a in angles)
    sum_y = sum(F * np.sin(np.radians(a)) for a in angles)
    assert abs(sum_x) < 1e-10
    assert abs(sum_y) < 1e-10
```

---

## Confidence Assessment

| Aspect | Confidence | Notes |
|---|---|---|
| **SymPy for symbolic solving** | ✅ High | Well-documented, widely used for exactly this kind of problem |
| **Matplotlib for force diagrams** | ✅ High | `quiver` and `annotate` are proven tools for vector visualisation |
| **Streamlit for UI** | ✅ High | Ideal for this kind of interactive calculator; minimal setup |
| **pyfreebody for diagrams** | ⚠️ Medium | Smaller project, may have limitations for complex scenarios |
| **Architecture recommendation** | ✅ High | Standard separation of concerns (model/solver/view) |
| **A-level maths coverage** | ✅ High | Inclined planes, friction, concurrent forces are core topics |
| **Moments/rigid body extension** | ⚠️ Medium | Straightforward extension but not fully implemented in example |

**Assumptions made:**
- You are comfortable with Python (or willing to learn the basics)
- The tool is primarily for personal study use, not production deployment
- A-level maths mechanics scope (2D statics, not 3D or dynamics)

---

## Footnotes

[^1]: [Save My Exams — Resolving Forces & Inclined Planes](https://www.savemyexams.com/a-level/maths/cie/20/mechanics/revision-notes/forces-and-equilibrium/resolving-forces-inclined-planes-and-friction/resolving-forces-and-inclined-planes/)
[^2]: [Physics & Maths Tutor — Forces and Friction Cheat Sheet](https://pmt.physicsandmathstutor.com/download/Maths/A-level/Mechanics/Forces-and-Newtons-Laws-2/Cheat-Sheets/Forces%20and%20Friction.pdf)
[^3]: [Engineering Statics — Equations of Equilibrium](https://engineeringstatics.org/Chapter_05-equations-of-equilibrium.html)
[^4]: [SymPy Solve documentation](https://docs.sympy.org/latest/guides/solving/index.html)
[^5]: [NumPy linalg.solve documentation](https://numpy.org/doc/stable/reference/generated/numpy.linalg.solve.html)
[^6]: [NumPy static equilibrium tutorial](https://github.com/numpy/numpy-tutorials/blob/main/content/tutorial-static_equilibrium.md)
[^7]: [Matplotlib quiver documentation](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.quiver.html)
[^8]: [pyfreebody on GitHub](https://github.com/velocitatem/pyfreebody)
[^9]: [pyfreebody on PyPI](https://pypi.org/project/pyfreebody/)
