# Zinny API: A Backend Server for Structured Media Evaluations
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](LICENSE)

## What's the skinny on the ciné?

Zinny API powers the backend for structured media evaluations using surveys from [zinny-surveys](https://github.com/RyLaney/zinny-surveys). It stores ratings in a SQLite database and provides endpoints for managing surveys, titles, ratings, and collections.

The API is used by the [zinny-webui](https://github.com/RyLaney/zinny-webui) frontend and the [zinny-cli](https://github.com/RyLaney/zinny-cli) command-line interface for seamless user interaction.


## Quickstart
1. Start the server:
  `python zinny-api.py` or `zinny-api`
2. Open the web browser to:
   `http://127.0.0.1:5219`


## API Documentation
For detailed API endpoints and usage, see [API_REFERENCE.md](https://github.com/RyLaney/zinny-api/blob/main/API_REFERENCE.md).


## Installation Details

see [SETUP.md](https://github.com/RyLaney/zinny-api/blob/main/SETUP.md)

## Contributing
We welcome contributions! If you'd like to report an issue, suggest a feature, or contribute code, please check out the [CONTRIBUTING.md](https://github.com/RyLaney/zinny-api/blob/main/CONTRIBUTING.md) file for guidelines.


## Acknowledgements
- [Flask](https://flask.palletsprojects.com/en/1.1.x/) for the API framework.
- [PyInstaller](https://www.pyinstaller.org/) for building executables.
- [Platypus](https://github.com/sveinbjornt/Platypus) for creating macOS app bundles.
- Special thanks to [IMDb](https://www.imdb.com) for being the standard reference for movie and TV data. While no IMDb data is used directly, title information may coincide with their dataset.
- Development sponsored by [Teus Media](https://teus.media).
