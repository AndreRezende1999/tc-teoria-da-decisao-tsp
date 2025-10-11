# Project Overview

This project is a university assignment for the course "ELE088 - Teoria da Decisão" (Decision Theory). The goal is to implement a solution for a multi-objective Traveling Salesman Problem (TSP). The solution is developed in Python using a Jupyter Notebook.

The main objective is to find a route that visits 250 cities, starting from and returning to city 1, minimizing both the total travel time and distance.

## Key Files

*   `enunciado.md`: The main project brief, containing the problem description, mathematical formulation, and the deliverables.
*   `TD_TC1.ipynb`: The Jupyter Notebook containing the implementation of the solution.
*   `distancia.csv`: A 250x250 matrix containing the distance (in km) between cities.
*   `tempo.csv`: A 250x250 matrix containing the time (in hours) to travel between cities.
*   `requirements.txt`: A list of the Python libraries required to run the project.
*   `README.md`: A summary of the project and instructions on how to run it.

## Technologies and Libraries

*   **Language:** Python
*   **Libraries:** The project uses a virtual environment (`.venv`) and the required libraries are listed in `requirements.txt`. The main libraries are:
    *   `numpy`: For efficient numerical operations and handling of the cost matrices.
    *   `pandas`: For reading and parsing the `.csv` data files.
    *   `matplotlib`: For plotting the results.

## Building and Running

1.  **Set up the environment:**
    *   It is recommended to use a Python virtual environment.
    *   Activate the virtual environment:
        *   On Windows (Command Prompt): `.\.venv\Scripts\activate.bat`
        *   On Windows (PowerShell): `.\.venv\Scripts\Activate.ps1`
        *   On macOS/Linux: `source ./.venv/bin/activate`

2.  **Install dependencies:**
    *   Install the required libraries using the `requirements.txt` file:
        ```sh
        pip install -r requirements.txt
        ```

3.  **Run the Jupyter Notebook:**
    *   Start the Jupyter Notebook server:
        ```sh
        jupyter notebook
        ```
    *   In the browser window that opens, navigate to and open the `TD_TC1.ipynb` file.
    *   Run the cells in the notebook sequentially to see the results.

## Git Repository

A local Git repository has been initialized for this project. The `example` directory is ignored by Git.