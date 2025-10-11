# Teoria da Decisão - TSP

This project is a university assignment for the course "ELE088 - Teoria da Decisão" (Decision Theory). The goal is to implement a solution for a multi-objective Traveling Salesman Problem (TSP). The solution is developed in Python using a Jupyter Notebook.

## Problem Description

The Traveling Salesman Problem (TSP) aims to find the shortest possible route that visits a set of cities and returns to the origin city, visiting each city exactly once.

In this project, we consider a multi-objective variant of the problem, where we want to minimize both the **time** (in hours) and the **distance** (in km) of a tour that visits 250 cities.

### Objective Functions

*   **Minimize Time ($f_T$):**
    $f_{T} = \sum_{i=1}^{n} \sum_{j=1}^{n} t_{ij} \cdot x_{ij}$

*   **Minimize Distance ($f_D$):**
    $f_{D} = \sum_{i=1}^{n} \sum_{j=1}^{n} d_{ij} \cdot x_{ij}$

### Constraints

1.  You must enter each city exactly once.
2.  You must leave each city exactly once.
3.  The solution must not contain any sub-cycles.

## Running the Project

1.  **Set up the environment:**
    *   It is recommended to use a Python virtual environment. The `.venv` directory in this project was created for this purpose.
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