"""
Deduplication — tracks already-posted video IDs to avoid duplicate posts.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

MAX_TRACKED_VIDEOS = 500  # Keep the file size bounded


def load_posted_ids(filepath: str) -> set:
    """
    Load the set of already-posted video IDs from disk.
    Returns an empty set if the file doesn't exist or is corrupted.
    """
    if not os.path.exists(filepath):
        logger.info(f"No dedup file found at {filepath}, starting fresh.")
        return set()

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            ids = set(data.get("posted_ids", []))
            logger.info(f"Loaded {len(ids)} previously posted video IDs.")
            return ids
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Could not read dedup file: {e}. Starting fresh.")
        return set()


def save_posted_ids(filepath: str, posted_ids: set):
    """
    Save the set of posted video IDs to disk.
    Keeps only the most recent MAX_TRACKED_VIDEOS entries.
    """
    # Convert to list and trim to max size (keep most recent)
    ids_list = list(posted_ids)
    if len(ids_list) > MAX_TRACKED_VIDEOS:
        ids_list = ids_list[-MAX_TRACKED_VIDEOS:]

    data = {"posted_ids": ids_list}

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(ids_list)} posted video IDs to {filepath}")
    except IOError as e:
        logger.error(f"Could not save dedup file: {e}")


def add_posted_ids(filepath: str, new_ids: list):
    """
    Load existing IDs, add new ones, and save back to disk.
    """
    existing = load_posted_ids(filepath)
    existing.update(new_ids)
    save_posted_ids(filepath, existing)
