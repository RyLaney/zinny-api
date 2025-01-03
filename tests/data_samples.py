"""Reusable test data for unit tests."""

import json

# pylint: disable=line-too-long

# Sample Survey Data
SURVEY_VFX_SAMPLE = {
  "id": "vfx",
  "name": "Visual Effects Assessment",
  "version": "1.0",
  "description": "Evaluation criteria for visual effects, including animation .",
  "author": "the-zinny team",
  "defaults": {
    "range": [1, 10]
  },
  "criteria": [
    {
      "id": "artistry",
      "name": "Artistry",
      "description": "The artistic quality, creativity, or aesthetic integration of visuals.",
      "markers": {
        "1": "Not exceptional artistry",
        "10": "Exceptional artistry and creativity"
      }
    },
    {
      "id": "technical_achievement",
      "name": "Technical Achievement",
      "description": "The innovation and use of new or improved technology.",
      "markers": {
        "1": "No new technology",
        "10": "Pioneering use of technology"
      }
    },
    {
      "id": "fidelity",
      "name": "Overall Fidelity",
      "description": "The overall realism and believability of the VFX.",
      "markers": {
        "1": "Unconvincing VFX",
        "10": "Highly realistic or immersive"
      }
    }
  ]
}

SURVEY_PICTURE_SAMPLE = {
    "id": "picture",
    "name": "Picture Overall Ratings",
    "version": "1.0",
    "description": "Evaluation criteria for overall excellence of a Picture Show.",
    "author": "the-zinny team",
    "defaults": {
      "range": [1, 10]
    },
    "criteria": [
      {
        "id": "story",
        "name": "Storytelling",
        "description": "Clarity, originality, and impact of the narrative."
      },
      {
        "id": "visual",
        "name": "Visual Aesthetics",
        "description": "Cinematography, production design, and overall visual style."
      },
      {
        "id": "emotional",
        "name": "Emotional Impact",
        "description": "The ability to evoke strong emotions in viewers."
      }
    ]
}

# Convert to JSON strings for database insertion
SURVEY_VFX_JSON = json.dumps(SURVEY_VFX_SAMPLE)
SURVEY_PICTURE_JSON = json.dumps(SURVEY_PICTURE_SAMPLE)


# Sample Title Data

# IMDb-Style Data
TITLES_2024VFX_IMDB_SAMPLE = [
    {"tconst": "tt10146532", "primaryTitle": "Ojai", "startYear": "2024", "titleType": "movie"},
    {"tconst": "tt11057302", "primaryTitle": "Madame Web", "startYear": "2024", "titleType": "movie"},
    {"tconst": "tt12037194", "primaryTitle": "Furiosa: A Mad Max Saga", "startYear": "2024", "titleType": "movie"}
]


# Sample Data (incomplete records)
TITLES_2024VFX_SAMPLE = [
    {"name": "Ojai", "year": 2024},
    {"name": "Madame Web", "year": 2024},
    {"name": "Spaceman", "type": "movie", "year": 2024}
]

# Sample Data from titles TSV
TITLES_WONVFX_SAMPLE = [
    {"name": "Godzilla Minus One", "year": 2023},
    {"name": "Avatar: The Way of Water", "year": 2022},
    {"name": "Dune", "year": 2021},
    {"name": "Tenet", "year": 2020},
    {"name": "1917", "year": 2019}
]

TITLES_SHORT_SAMPLE = [
    {"name": "Carmencita", "type": "short", "year": 1894},
    {"name": "Le clown et ses chiens", "type": "short", "year": 1892},
    {"name": "Poor Pierrot", "type": "short", "year": 1892},
    {"name": "Un bon bock", "type": "short", "year": 1892},
    {"name": "Blacksmith Scene", "type": "short", "year": 1893}
]
TITLES_TVMOVIE_MINISERIES_SAMPLE = [
    {"name": "Julius Caesar", "type": "tvMovie", "year": 1938},
    {"name": "As You Like It", "type": "tvMovie", "year": 1946},
    {"name": "A Midsummer Night's Dream", "type": "tvMovie", "year": 1946},
    {"name": "Quatermass II", "type": "tvMiniSeries", "year": 1955},
    {"name": "Quatermass and the Pit", "type": "tvMiniSeries", "year": 1958}
]
TITLES_VIDEO_TVSHORT_SAMPLE = [
    {"name": "Take It Out in Trade: The Outtakes", "type": "video", "year": 1995},
    {"name": "Queen: Live at the Rainbow", "type": "video", "year": 1992},
    {"name": "Art Game", "type": "video", "year": 1978},
    {"name": "Much Ado About Nothing", "type": "tvShort", "year": 1937},
    {"name": "The Sun Was Setting", "type": "tvShort", "year": 1951}
]
TITLES_TVSERIES_SAMPLE = [
    {"name": "Actor's Studio", "type": "tvSeries", "year": 1948},
    {"name": "The Adventures of Oky Doky", "type": "tvSeries", "year": 1948},
    {"name": "The Alan Dale Show", "type": "tvSeries", "year": 1948},
    {"name": "America Song", "type": "tvSeries", "year": 1948},
    {"name": "America Speaks", "type": "tvSeries", "year": 1948}
]

TITLE_TYPES_SAMPLE = [
    {"type": "tvSeries", "display_name": "TV Series"},
    {"type": "tvMovie", "display_name": "TV Movie"},
    {"type": "movie", "display_name": "Movie"},
    {"type": "short", "display_name": "Short"}
]

# Sample Weights data

WEIGHTS_PICTURE_DEFAULT = {
    # "id": "picture_default",
    "name": "Picture Overall (Even Weights)",
    "description": "Evenly weighted criteria for evaluating feature films.",
    "version": "1.0",
    "survey_id": "picture_extended",
    "criteria_weights": {
        "arts": 1.0,
        "craft": 1.0,
        "cultural_impact": 1.0,
        "emotional_impact": 1.0,
        "humanity": 1.0,
        "storytelling": 1.0,
        "technical_achievement": 1.0,
        "visual_aesthetics": 1.0
    }
}

WEIGHTS_PICTURE_STORYTELLER = {
    # "id": "picture_storyteller",
    "name": "Picture Overall (Storyteller perspective)",
    "description": "Reduced emphasis on visual aesthetics, arts, and technical criteria.",
    "version": "1.0",
    "survey_id": "picture_extended",
    "criteria_weights": {
        "arts": 0.5,
        "craft": 1.0,
        "cultural_impact": 1.0,
        "emotional_impact": 1.5,
        "humanity": 1.0,
        "storytelling": 1.5,
        "technical_achievement": 0.5,
        "visual_aesthetics": 0.5
    }
}

WEIGHTS_PICTURE_TECHNOLOGIST = {
    # "id": "picture_technologist",
    "name": "Picture Overall (Technologist perspective)",
    "description": "Increased emphasis on visual aesthetics and technical criteria.",
    "version": "1.0",
    "survey_id": "picture_extended",
    "criteria_weights": {
        "arts": 0.5,
        "craft": 1.0,
        "cultural_impact": 0.5,
        "emotional_impact": 0.5,
        "humanity": 0.5,
        "storytelling": 1.0,
        "technical_achievement": 1.5,
        "visual_aesthetics": 1.5
    }
}

WEIGHTS_VFX_DEFAULT = {
    # "id": "vfx_default",
    "name": "Visual Effects default (Even Weights)",
    "description": "Evenly distributed weights for evaluating visual effects.",
    "version": "1.0",
    "survey_id": "vfx:1.0",
    "criteria_weights": {
        "artistry": 1.0,
        "contribution": 1.0,
        "fidelity": 1.0,
        "necessity": 1.0,
        "technical_achievement": 1.0
    }
}

WEIGHTS_VFX_SPARSE = {
    # "id": "vfx_default",
    "criteria_weights": {
        "artistry": 1.0,
        "contribution": 1.0,
        "technical_achievement": 1.0
    }
}


# Sample Ratings Data

# tests/data_samples.py

# Ratings for the "VFX" survey
RATINGS_VFX_SAMPLE = [
  {
    "title_id": 1,
    "survey_id": "vfx",
    "ratings": {
      "artistry": 8,
      "technical_achievement": 9,
      "fidelity": 10,
    },
    "comments": "Excellent VFX.",
    "screen_type_id": 'big'
  },
  {
    "title_id": 2,
    "survey_id": "vfx",
    "ratings": {
      "artistry": 7,
      "technical_achievement": 8,
      "fidelity": 9
    },
    "comments": "Solid but not groundbreaking.",
    "screen_type_id": 'medium'
  }
]

# Ratings for the "Picture" survey
RATINGS_PICTURE_SAMPLE = [
  {
    "title_id": 1,
    "survey_id": "picture",
    "ratings": {
      "storytelling": 9,
      "visual_aesthetics": 8,
      "emotional_impact": 10
    },
    "comments": "Great narrative with stunning visuals.",
    "screen_type_id": 'big'
  },
  {
    "title_id": 2,
    "survey_id": "picture",
    "ratings": {
      "storytelling": 7,
      "visual_aesthetics": 6,
      "emotional_impact": 8
    },
    "comments": "Good story, but visuals lacked impact.",
    "screen_type_id": 'small'
  }
]


# Sample Collection Data
# Title Collections
COLLECTION_FAVORITES_SAMPLE = {
    "name": "Favorites 2024",
    "description": "Movies I plan to watch in 2024.",
    "items": [
        {"name": "Madame Web", "year": 2024},
        {"name": "Furiosa: A Mad Max Saga", "year": 2024},
        {"name": "Spaceman", "year": 2024}
    ]
}

COLLECTION_CLASSICS_SAMPLE = {
    "name": "Classic Movies",
    "description": "Timeless movies that everyone should watch.",
    "items": [
        {"name": "Casablanca", "year": 1942},
        {"name": "Gone with the Wind", "year": 1939},
        {"name": "The Wizard of Oz", "year": 1939}
    ]
}

COLLECTION_SCI_FI_SAMPLE = {
    "name": "Sci-Fi Favorites",
    "description": "Top science fiction movies of all time.",
    "items": [
        {"name": "Blade Runner", "year": 1982},
        {"name": "The Matrix", "year": 1999},
        {"name": "Dune", "year": 1984},
        {"name": "Dune: Part One", "year": 2021},
        {"name": "Dune: Part Two", "year": 2024}
    ]
}


SCREEN_TYPES_SAMPLE = [
    { "id": 1, "type": 'big', "display_name": 'Big screen', "description": 'Theater / Projector' },
    { "id": 2, "type": 'medium', "display_name": 'Medium screen', "description": 'Desktop / UHD TV' },
    { "id": 3, "type": 'small', "display_name": 'Small screen', "description": 'Laptop / HD TV' },
    { "id": 4, "type": 'micro', "display_name": 'Micro screen', "description": 'Phone / Tablet' },
    { "id": 5, "type": 'special', "display_name": 'Special Venue', "description": 'IMAX / 3D / VR' },
]
