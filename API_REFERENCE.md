# API Endpoints

This file documents all available endpoints in the Zinny API, grouped by resource type (Surveys, Titles, Ratings, etc.). For detailed usage examples, refer to the API documentation.

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


## Examples 

### API Requests for Title Search
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