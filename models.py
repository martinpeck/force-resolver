"""Data models for the force resolver tool."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SurfaceType(Enum):
    FLAT = "flat"
    INCLINED = "inclined"


@dataclass
class Force:
    """A force acting on a body."""

    name: str
    magnitude: Optional[float] = None  # None if unknown
    angle_deg: Optional[float] = None  # Angle in degrees from +x axis (or along slope)
    is_unknown: bool = False
    color: str = "#3498db"

    @property
    def is_fully_defined(self) -> bool:
        return self.magnitude is not None and self.angle_deg is not None


@dataclass
class Surface:
    """The surface the object rests on."""

    type: SurfaceType = SurfaceType.FLAT
    angle_deg: float = 0.0  # incline angle in degrees
    mu: Optional[float] = None  # coefficient of friction (None = smooth)

    @property
    def is_rough(self) -> bool:
        return self.mu is not None and self.mu > 0


@dataclass
class SolverResult:
    """Result returned by a problem solver."""

    values: dict[str, float] = field(default_factory=dict)
    status: str = ""
    working_steps: list[str] = field(default_factory=list)
    forces_for_diagram: list[dict] = field(default_factory=list)
    equilibrium: bool = True
