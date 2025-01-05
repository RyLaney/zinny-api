"""The main entrypoint file for the Zinny Flask server."""

import os
import argparse
import webbrowser

from zinny_api import create_app


def main():
    """create the flask zinny_api and start the Zinny server."""
    # Parse CLI arguments or environment variables for configuration
    parser = argparse.ArgumentParser(description="Run the Zinny Flask server.")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("ZINNY_PORT", "5219")),
        help="Port number to run the server (default: 5219 or environment variable ZINNY_PORT)."
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not launch the default web browser."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run the server in debug mode."
    )

    args = parser.parse_args()

    zinny_api = create_app()

    if not args.no_browser:
        url = f"http://127.0.0.1:{args.port}/api/v1/surveys"
        webbrowser.open(url)

    # zinny_api.run(port=args.port)
    zinny_api.run(debug=args.debug, port=args.port)


if __name__ == '__main__':
    main()
