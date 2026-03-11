"""Unit tests for problem solvers — verified against textbook results."""

import math
import numpy as np
import pytest

from problems import inclined_plane, concurrent, flat_surface


# ── Inclined plane ───────────────────────────────────────────────────────────

class TestInclinedPlane:

    def test_basic_weight_components(self):
        """10 kg on a 30° slope, μ=0.3, no applied force."""
        result = inclined_plane.solve(mass=10, g=9.8, incline_deg=30, mu=0.3)

        assert result.values["Weight (W)"] == pytest.approx(98.0, abs=0.1)
        assert result.values["W parallel to slope"] == pytest.approx(49.0, abs=0.1)
        assert result.values["W perpendicular to slope"] == pytest.approx(84.87, abs=0.1)
        assert result.values["Normal reaction (R)"] == pytest.approx(84.87, abs=0.1)

    def test_limiting_friction(self):
        """At limiting equilibrium on a 30° slope, μ must equal tan(30°) ≈ 0.577."""
        mu = math.tan(math.radians(30))
        result = inclined_plane.solve(mass=10, g=9.8, incline_deg=30, mu=mu)
        assert result.equilibrium is True
        # Friction required = W_parallel ≈ max friction
        assert result.values["Actual friction"] == pytest.approx(49.0, abs=0.1)
        assert result.values["Max friction (μR)"] == pytest.approx(49.0, abs=0.1)

    def test_slides_when_mu_too_low(self):
        """μ=0.1 on a 45° slope — should not be in equilibrium."""
        result = inclined_plane.solve(mass=5, g=9.8, incline_deg=45, mu=0.1)
        assert result.equilibrium is False

    def test_smooth_plane(self):
        """μ=0 — block always slides unless the plane is horizontal."""
        result = inclined_plane.solve(mass=5, g=9.8, incline_deg=10, mu=0.0)
        assert result.equilibrium is False
        assert result.values["Max friction (μR)"] == pytest.approx(0.0, abs=0.01)

    def test_with_applied_force(self):
        """Applied force up the slope should reduce friction needed."""
        result_no_force = inclined_plane.solve(mass=10, g=9.8, incline_deg=30, mu=0.3)
        result_with_force = inclined_plane.solve(
            mass=10, g=9.8, incline_deg=30, mu=0.3,
            applied_mag=20, applied_angle_deg=0,
        )
        # With a force pushing up the slope, net down-slope force decreases
        assert (result_with_force.values["Net force down slope"]
                < result_no_force.values["Net force down slope"])

    def test_diagram_forces_present(self):
        """Solver should return at least weight and normal for diagram."""
        result = inclined_plane.solve(mass=10, g=9.8, incline_deg=30, mu=0.3)
        names = [f["name"] for f in result.forces_for_diagram]
        assert "W" in names
        assert "R" in names


# ── Concurrent forces ────────────────────────────────────────────────────────

class TestConcurrentForces:

    def test_three_equal_forces_at_120_deg(self):
        """Three equal forces at 120° intervals should be in equilibrium."""
        forces = [
            {"name": "F1", "magnitude": 10, "angle_deg": 0},
            {"name": "F2", "magnitude": 10, "angle_deg": 120},
            {"name": "F3", "magnitude": 10, "angle_deg": 240},
        ]
        result = concurrent.solve(forces)
        assert result.equilibrium is True
        assert result.values["Resultant magnitude"] == pytest.approx(0.0, abs=0.01)

    def test_two_opposite_forces(self):
        """Two equal and opposite forces cancel out."""
        forces = [
            {"name": "F1", "magnitude": 50, "angle_deg": 0},
            {"name": "F2", "magnitude": 50, "angle_deg": 180},
        ]
        result = concurrent.solve(forces)
        assert result.equilibrium is True

    def test_resultant_of_perpendicular_forces(self):
        """3 N east + 4 N north → resultant 5 N."""
        forces = [
            {"name": "F1", "magnitude": 3, "angle_deg": 0},
            {"name": "F2", "magnitude": 4, "angle_deg": 90},
        ]
        result = concurrent.solve(forces)
        assert result.equilibrium is False
        assert result.values["Resultant magnitude"] == pytest.approx(5.0, abs=0.01)
        assert result.values["Resultant direction (°)"] == pytest.approx(53.13, abs=0.1)

    def test_single_force_not_equilibrium(self):
        """A single force is never in equilibrium."""
        forces = [{"name": "F1", "magnitude": 10, "angle_deg": 45}]
        result = concurrent.solve(forces)
        assert result.equilibrium is False
        assert result.values["Resultant magnitude"] == pytest.approx(10.0, abs=0.01)


# ── Flat rough surface ───────────────────────────────────────────────────────

class TestFlatSurface:

    def test_horizontal_force_within_friction(self):
        """Small horizontal force — should be in equilibrium."""
        result = flat_surface.solve(mass=10, g=9.8, mu=0.5,
                                    applied_force=10, applied_angle_deg=0)
        assert result.equilibrium is True
        assert result.values["Normal reaction (R)"] == pytest.approx(98.0, abs=0.1)
        assert result.values["Actual friction force"] == pytest.approx(10.0, abs=0.1)

    def test_horizontal_force_exceeds_friction(self):
        """Large horizontal force — should not be in equilibrium."""
        result = flat_surface.solve(mass=10, g=9.8, mu=0.1,
                                    applied_force=50, applied_angle_deg=0)
        assert result.equilibrium is False

    def test_angled_force_reduces_normal(self):
        """Upward component of applied force reduces the normal reaction."""
        result = flat_surface.solve(mass=10, g=9.8, mu=0.5,
                                    applied_force=40, applied_angle_deg=30)
        W = 10 * 9.8
        F_vert = 40 * np.sin(np.radians(30))
        expected_N = W - F_vert
        assert result.values["Normal reaction (R)"] == pytest.approx(expected_N, abs=0.1)

    def test_no_applied_force(self):
        """Zero applied force — everything should be zero except weight and normal."""
        result = flat_surface.solve(mass=5, g=9.8, mu=0.4,
                                    applied_force=0, applied_angle_deg=0)
        assert result.equilibrium is True
        assert result.values["Actual friction force"] == pytest.approx(0.0, abs=0.01)
        assert result.values["Normal reaction (R)"] == pytest.approx(49.0, abs=0.1)
