# Force Resolver ⚡

An interactive tool for resolving static forces, calculating unknowns, and visualising free body diagrams. Built for A-level Maths Mechanics revision.

## Features

- **Inclined plane with friction** — resolve weight into components, calculate normal reaction and friction, check equilibrium, add applied forces
- **Concurrent forces** — find the resultant of multiple forces at different angles, check equilibrium, calculate the equilibrant
- **Flat rough surface** — applied force at an angle on a rough surface, friction and normal reaction calculations
- **Free body diagrams** — auto-generated, labelled force diagrams for every problem
- **Step-by-step working** — see the full calculation breakdown

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## Project Structure

```
force-resolver/
├── app.py                      # Streamlit UI (entry point)
├── models.py                   # Data classes (Force, Surface, SolverResult)
├── solver.py                   # General-purpose symbolic solver (SymPy)
├── diagram.py                  # Matplotlib force diagram rendering
├── problems/
│   ├── inclined_plane.py       # Inclined plane solver
│   ├── concurrent.py           # Concurrent forces solver
│   └── flat_surface.py         # Flat rough surface solver
├── tests/
│   └── test_solver.py          # Unit tests (textbook-verified)
├── requirements.txt
└── README.md
```

## How It Works

1. **Choose a problem type** from the sidebar
2. **Enter parameters** (mass, angles, forces, coefficient of friction)
3. **View the solution** — computed values, equilibrium status, and step-by-step working
4. **See the free body diagram** — auto-generated with labelled force arrows
