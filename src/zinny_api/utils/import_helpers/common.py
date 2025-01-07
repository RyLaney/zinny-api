"""Common functions used in helpers"""

import re

def scrub_string(value):
    """Scrub a string to remove special characters and convert to lowercase."""
    if not value:
        return ""

    scrubbed = re.sub(r"\s+", "_", value)
    scrubbed = re.sub(r"[^a-zA-Z0-9_-]", "", scrubbed)
    return scrubbed.lower()
