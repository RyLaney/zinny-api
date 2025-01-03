# Zinny
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](LICENSE)

## What's the skinny on the ciné?

Zinny is an open-source project for rating films via structured data surveys. Surveys and specifications are from [zinny-surveys](https://github.com/RyLaney/zinny-surveys). Surveys are defined in JSON format, and ratings are stored in a SQLite database. The project is built with Python and Flask, and the frontend uses Bootstrap and jQuery.

This is the API. There are a [web interface](https://github.com/RyLaney/zinny-webui) and a [command-line interface](https://github.com/RyLaney/zinny-cli) that can be used to interact with the API. 

Development was sponsored by **Teus Media**. 

## Quickstart
1. Run the server `python zinny-server.py` or `zinny-server`
2. Open the web browser to http://127.0.0.1:5219

## API Endpoints

### Surveys
- **GET /api/v1/surveys/**: Fetch all surveys.
- **GET /api/v1/surveys/<survey_id>**: Fetch details of a specific survey.
- **POST /api/v1/surveys/import**: Import a survey from a JSON file.
- **POST /api/v1/surveys/load**: Load surveys from the server's predefined directory.

### Titles
- **GET /api/v1/titles/**: Fetch all titles.
- **POST /api/v1/titles/**: Add a new title.
- **GET /api/v1/titles/<title_id>**: Fetch details of a specific title.
- **PUT /api/v1/titles/<title_id>**: Update an existing title.
- **DELETE /api/v1/titles/<title_id>**: Delete a title.
- **POST /api/v1/titles/import**: Import titles from a user-uploaded TSV or CSV file.
- **POST /api/v1/titles/load**: Load titles from the server's predefined directory.
- **GET /api/v1/titles/search?query=<query>&year=<year>&type=<type>**: Search titles by name, year, or type.
- 
### Ratings
- **GET /api/v1/ratings/**: Fetch all ratings.
- **POST /api/v1/ratings/**: Submit a new rating.
- **PUT /api/v1/ratings/<rating_id>**: Update an existing rating.
- **DELETE /api/v1/ratings/<rating_id>**: Delete a rating.
- **GET /api/v1/ratings/export**: Export all ratings as JSON.
- **GET /api/v1/ratings/<title_id>**: Fetch ratings for a specific title.

### Weight Presets
- **GET /api/v1/weights/**: Fetch all weight presets.
- **POST /api/v1/weights/**: Add or update a weight preset.
- **POST /api/v1/weights/import**: Import a weight preset from a JSON file.
- **POST /api/v1/weights/load**: Load weight presets from the server's predefined directory.

### Collections
- **GET /api/v1/collections/**: Fetch all collections.
- **POST /api/v1/collections/**: Create a new collection.
- **GET /api/v1/collections/<collection_id>**: Fetch details of a specific collection.
- **DELETE /api/v1/collections/<collection_id>**: Delete a collection.
- **POST /api/v1/collections/<collection_id>/titles**: Add titles to a collection.
- **DELETE /api/v1/collections/<collection_id>/titles**: Remove titles from a collection.
- **POST /api/v1/collections/import**: Import a collection from a JSON file.
- **GET /api/v1/collections/export**: Export all collections as JSON.
- **GET /api/v1/collections/export/<collection_id>**: Export a specific collection as JSON.
- TODO:
  - **GET /api/v1/collections/search?name=<name>**: Search collections by name.
  - **GET /api/v1/collections/<collection_id>/titles**: Fetch all titles in a specific collection.


## Example API Requests for Title Search
Search Titles by Name:
- `http GET /api/v1/titles/search?query=godzilla `

Filter by Year Range
- `http GET /api/v1/titles/search?year_start=2020&year_end=2023 `

Filter by Type
- `http GET /api/v1/titles/search?type=movie `

Filter by Survey
- `http GET /api/v1/titles/search?survey_id=vfx `

Paginate Results
- `http GET /api/v1/titles/search?page=2&limit=5 `

## Installation

Clone the repository:
```bash
git clone https://github.com/RyLaney/zinny.git
```

Run the server, which will be available at http://127.0.0.1:5219 by default:
```bash
python zinny.py
```

Optional Arguments for zinny.py:
- --no-launch-browser: Prevents automatically opening the web browser.
- --port [PORT]: Changes the server port (default: 5219).
  
Example:

```bash
python zinny.py --port 8080 --no-launch-browser
```

## Environment
The main script will check for and setup the environemt if it is not already set up. The manual steps are below.

#### Set up the environment with conda
```bash
# create a new environment
conda env create -f environment.yml
conda activate zinny

# update an existing environment
conda env update --file environment.yml --prune
```

#### Setup the environment with venv
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Development Environment
There are -dev options for both methods. -dev adds setuptools, linting, and testing packages
```bash
# conda
conda env create -f environment-dev.yml
conda env update --file environment-dev.yml --prune
conda activate zinny-dev

# venv
python -m venv venv-dev
source venv-dev/bin/activate
pip install -r requirements-dev.txt
```


## Proposed Binary Packages
In future releases, standalone executables will be provided to launch the server without needing to install the dependencies first.

## Contributing
Issues and pull requests are welcome. See the [CONTRIBUTING.md](CONTRIBUTING.md) file for more details on how to contribute to this repository.



## Project structure  tree
```bash
tree zinny-server \
    -I __pycache__ \
    -I zinny.egg-info \
    -I _attic \
    -I bootstrap.* \
    -I bootstrap-* \
    > zinny-server/project_tree.txt
    
```

## code coverage
```bash
coverage run -m pytest
coverage report
coverage html
```


## Acknowledgements
- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- To avoid duplicate entries, titles may be matched using IMDb's "tconst" IDs when available. Otherwise, titles are matched using title text only. Title information courtesy of [IMDb](https://www.imdb.com). Used with permission.
- [IMDb](https://www.imdb.com) is a registered trademark of IMDb.com, Inc. or its affiliates.

