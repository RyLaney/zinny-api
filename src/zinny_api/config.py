"""zinny_api locations"""

import os

APP_DATA_PATH = "zinny_api/v1/data"
SURVEY_PATHS = {
    "shared": os.path.join(APP_DATA_PATH, "surveys", "shared"),
    "local": os.path.join(APP_DATA_PATH, "surveys", "local")
}

WEIGHTS_PATHS = {
    "shared": os.path.join(APP_DATA_PATH, "weights", "shared"),
    "local": os.path.join(APP_DATA_PATH, "weights", "local")
}

COLLECTION_PATHS = {
    "shared": os.path.join(APP_DATA_PATH, "collections", "shared"),
    "local": os.path.join(APP_DATA_PATH, "collections", "local")
}
