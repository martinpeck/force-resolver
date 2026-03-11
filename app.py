"""Force Resolver — Static Equilibrium Solver.

A Streamlit app for resolving forces, calculating unknowns, and drawing
free body diagrams.  Covers A-level mechanics: inclined planes, friction,
concurrent forces, and flat-surface problems.
"""

import numpy as np
import streamlit as st

from problems import inclined_plane, concurrent, flat_surface
from diagram import render_inclined_plane, render_concurrent_forces, render_flat_surface

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(page_title="Force Resolver", page_icon="⚡", layout="wide")
st.title("⚡ Force Resolver")
st.markdown("Resolve static forces, calculate unknowns, and visualise free body diagrams.")

# ── Sidebar: choose problem type ─────────────────────────────────────────────

PROBLEM_TYPES = [
    "Inclined plane with friction",
    "Concurrent forces at a point",
    "Object on flat rough surface",
]

problem_type = st.sidebar.selectbox("Problem type", PROBLEM_TYPES)

# ═══════════════════════════════════════════════════════════════════════════════
# INCLINED PLANE
# ═══════════════════════════════════════════════════════════════════════════════

if problem_type == "Inclined plane with friction":
    st.sidebar.header("Parameters")
    mass = st.sidebar.number_input("Mass (kg)", min_value=0.1, value=10.0, step=0.1)
    g = st.sidebar.number_input("Gravity (m/s²)", value=9.8, step=0.1)
    theta_deg = st.sidebar.slider("Plane angle (°)", 1, 89, 30)
    mu = st.sidebar.number_input("Coefficient of friction (μ)", min_value=0.0,
                                  max_value=5.0, value=0.3, step=0.01)

    has_applied = st.sidebar.checkbox("Add an applied force?")
    app_mag, app_angle = 0.0, 0.0
    if has_applied:
        app_mag = st.sidebar.number_input("Applied force magnitude (N)",
                                           min_value=0.0, value=20.0, step=0.5)
        app_angle = st.sidebar.number_input(
            "Applied force angle (° from slope surface, +ve = away from slope)",
            value=0.0, step=1.0,
        )

    # Solve
    result = inclined_plane.solve(mass, g, theta_deg, mu, app_mag, app_angle)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📊 Solution")
        if result.equilibrium:
            st.success(result.status)
        else:
            st.warning(result.status)

        for label, value in result.values.items():
            st.write(f"**{label}:** {value:.2f} N")

        with st.expander("📝 Step-by-step working", expanded=True):
            for step in result.working_steps:
                st.write(f"- {step}")

    with col2:
        st.subheader("📐 Free Body Diagram")
        fig = render_inclined_plane(result.forces_for_diagram, theta_deg)
        st.pyplot(fig)

# ═══════════════════════════════════════════════════════════════════════════════
# CONCURRENT FORCES
# ═══════════════════════════════════════════════════════════════════════════════

elif problem_type == "Concurrent forces at a point":
    st.sidebar.header("Forces")
    num_forces = st.sidebar.number_input("Number of forces", min_value=2, max_value=10, value=3)

    forces = []
    for i in range(int(num_forces)):
        st.sidebar.markdown(f"---\n**Force {i + 1}**")
        name = st.sidebar.text_input(f"Name", value=f"F{i + 1}", key=f"name_{i}")
        mag = st.sidebar.number_input("Magnitude (N)", min_value=0.0, value=10.0,
                                       step=0.5, key=f"mag_{i}")
        angle = st.sidebar.number_input("Angle (° from +x axis, anticlockwise)",
                                         value=float(i * (360 / int(num_forces))),
                                         step=1.0, key=f"ang_{i}")
        forces.append({"name": name, "magnitude": mag, "angle_deg": angle})

    result = concurrent.solve(forces)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📊 Results")
        if result.equilibrium:
            st.success(result.status)
        else:
            st.warning(result.status)

        for label, value in result.values.items():
            st.write(f"**{label}:** {value:.4f}")

        with st.expander("📝 Step-by-step working", expanded=True):
            for step in result.working_steps:
                st.write(f"- {step}")

    with col2:
        st.subheader("📐 Force Diagram")
        resultant = None
        if not result.equilibrium:
            resultant = {
                "magnitude": result.values["Resultant magnitude"],
                "angle_deg": result.values["Resultant direction (°)"],
            }
        fig = render_concurrent_forces(result.forces_for_diagram, resultant=resultant)
        st.pyplot(fig)

# ═══════════════════════════════════════════════════════════════════════════════
# FLAT ROUGH SURFACE
# ═══════════════════════════════════════════════════════════════════════════════

elif problem_type == "Object on flat rough surface":
    st.sidebar.header("Parameters")
    mass = st.sidebar.number_input("Mass (kg)", min_value=0.1, value=5.0, step=0.1)
    g = st.sidebar.number_input("Gravity (m/s²)", value=9.8, step=0.1)
    mu = st.sidebar.number_input("Coefficient of friction (μ)", min_value=0.0,
                                  max_value=5.0, value=0.4, step=0.01)
    applied_force = st.sidebar.number_input("Applied force (N)", min_value=0.0,
                                             value=30.0, step=0.5)
    applied_angle = st.sidebar.number_input("Angle of applied force (° above horizontal)",
                                             min_value=-90.0, max_value=90.0,
                                             value=25.0, step=1.0)

    result = flat_surface.solve(mass, g, mu, applied_force, applied_angle)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📊 Solution")
        if result.equilibrium:
            st.success(result.status)
        else:
            st.warning(result.status)

        for label, value in result.values.items():
            st.write(f"**{label}:** {value:.2f} N")

        with st.expander("📝 Step-by-step working", expanded=True):
            for step in result.working_steps:
                st.write(f"- {step}")

    with col2:
        st.subheader("📐 Free Body Diagram")
        fig = render_flat_surface(result.forces_for_diagram)
        st.pyplot(fig)
