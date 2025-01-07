"""centralized locaiton for db setup and tests"""

SCHEMA_TITLES_TABLE = """
CREATE TABLE IF NOT EXISTS titles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    imdb_title_id TEXT UNIQUE,
    name TEXT NOT NULL,
    type TEXT,
    year INTEGER,
    UNIQUE(name, year)
);
"""

SCHEMA_TITLE_TYPE_TABLE = """
CREATE TABLE IF NOT EXISTS title_types (
    type TEXT PRIMARY KEY,          -- IMDb-style single word type (e.g., "tvSeries")
    display_name TEXT NOT NULL      -- Pretty-printed version (e.g., "TV Series")
);
"""

SCHEMA_COLLECTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);
CREATE TABLE IF NOT EXISTS collection_titles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER NOT NULL,
    title_id INTEGER NOT NULL,
    FOREIGN KEY (collection_id) REFERENCES collections (id),
    FOREIGN KEY (title_id) REFERENCES titles (id),
    UNIQUE(collection_id, title_id)  -- Prevent duplicate entries
);
"""

SCHEMA_SCREEN_TYPE_TABLE = """
CREATE TABLE IF NOT EXISTS screen_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL UNIQUE,         -- Single word type (e.g., "big")
    display_name TEXT NOT NULL,  -- Pretty-printed version (e.g., "Big Screen")
    description TEXT
);

-- TODO: Move these to zinny_api.utils.import_helpers : load_screen_types()
INSERT OR IGNORE INTO screen_types (type, display_name, description) VALUES
    ('big', 'Big screen', 'Theater / Projector'),
    ('medium', 'Medium screen', 'Desktop / UHD TV'),
    ('small', 'Small screen', 'Laptop / HD TV'),
    ('micro', 'Micro screen', 'Phone / Tablet'),
    ('special', 'Special Venue', 'IMAX / 3D / VR');
"""

SCHEMA_RATINGS_TABLE = """
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title_id INTEGER NOT NULL,
    survey_id TEXT NOT NULL,
    ratings TEXT NOT NULL,      -- JSON-encoded dictionary of criteria and scores
    screen_type_id INTEGER,
    comments TEXT,
    FOREIGN KEY (title_id) REFERENCES titles (id),
    FOREIGN KEY (survey_id) REFERENCES surveys (id),
    FOREIGN KEY (screen_type_id) REFERENCES screen_types (id),
    UNIQUE(title_id, survey_id)  -- Enforce unique ratings by title name, year, and survey
);

"""

SCHEMA_SURVEYS_TABLE = """
CREATE TABLE IF NOT EXISTS surveys (
    id TEXT PRIMARY KEY UNIQUE,
    name TEXT NOT NULL,
    version TEXT,
    description TEXT,
    defaults TEXT,
    criteria TEXT NOT NULL,
    extends TEXT,  -- Reference to the parent survey
    FOREIGN KEY (extends) REFERENCES surveys(id) ON DELETE SET NULL
);
"""

SCHEMA_WEIGHTS_TABLE = """
CREATE TABLE IF NOT EXISTS weight_presets (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT NOT NULL UNIQUE,
    survey_id TEXT,
    description TEXT,
    weights TEXT NOT NULL,
    FOREIGN KEY (survey_id) REFERENCES surveys (id)
);
"""
