# Setup Instructions for zinny-api

`zinny-api` provides a backend server for the Zinny project, exposing URL endpoints for interacting with surveys, titles, ratings, and collections. While it benefits from being seeded with `zinny-surveys`, it can accept any survey that conforms to the surveys definition.

## Prerequisites
- Python 3.8 or later
- Optionally, `zinny-surveys` to preload survey data

`zinny-surveys` is in requirements.txt, no extra installation is needed.

## Installation

### Clone the Repository
1. Clone the repository:
    ```bash
    git clone https://github.com/RyLaney/zinny-api.git
    ```

2. Create and activate a virtual environment:
    ```bash
    # With venv
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
    ```bash
    # With conda
    conda env create -f environment.yml
    conda activate zinny

    # Update an existing zinny environment
    conda env update --file environment.yml --prune
    ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Setup
1. (Optional) Seed the application with surveys:
   - Copy the survey files from `zinny-surveys` into the appropriate directory:
     ```bash
     cp -r zinny-surveys/surveys zinny-api/data/surveys
     ```

2. Initialize the SQLite database:
   ```bash
   python scripts/setup_database.py
   ```

## Running the Server
Run the server:
   ```bash
   python zinny.py
   ```

The API will be available at http://127.0.0.1:5219 by default. Use the `--port` flag to specify a different port.
