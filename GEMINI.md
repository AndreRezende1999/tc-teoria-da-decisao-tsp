# Project Overview

This project is a university assignment for the course "ELE088 - Teoria da Decisão" (Decision Theory). The goal is to implement a solution for a multi-objective Traveling Salesman Problem (TSP). The solution will be developed in Python.

The main objective is to find a route that visits 250 cities, starting from and returning to city 1, minimizing both the total travel time and distance.

## Key Files

*   `enunciado.md`: The main project brief, containing the problem description, mathematical formulation, and the deliverables.
*   `main.py`: The Python script where the solution will be implemented.
*   `distancia.csv`: A 250x250 matrix containing the distance (in km) between cities.
*   `tempo.csv`: A 250x250 matrix containing the time (in hours) to travel between cities.

## Technologies and Libraries

*   **Language:** Python
*   **Libraries:** The project uses a virtual environment (`.venv`) which includes:
    *   `numpy`: For efficient numerical operations and handling of the cost matrices.
    *   `pandas`: For reading and parsing the `.csv` data files.
    *   `matplotlib`: For plotting the results, as required in the later stages of the project.

## Building and Running

There are no complex build steps. The project is run by executing the main Python script.

1.  **Activate the virtual environment:**
    *   On Windows (Command Prompt): `.\.venv\Scripts\activate.bat`
    *   On Windows (PowerShell): `.\.venv\Scripts\Activate.ps1`
    *   On macOS/Linux: `source ./.venv/bin/activate`

2.  **Run the script:**
    ```sh
    python main.py
    ```

## Development Conventions

*   The implementation should follow the algorithms and structures described in `enunciado.md`, including the GVNS metaheuristic, VND for local search, and a randomized greedy constructive heuristic.
*   The code should be written in a clear and understandable manner.
