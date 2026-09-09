"""Persistent top-score storage with safe fallbacks for local play."""

import json
import os
from collections.abc import Iterable
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Optional

MAX_HIGH_SCORES = 5
DEFAULT_HIGH_SCORE_FILE = Path("highscore.json")


def normalize_high_scores(scores: Iterable[object]) -> List[int]:
    """Return the descending top five non-negative integer scores.

    Keeping this policy in one place ensures loading, saving, and in-memory
    leaderboard updates agree on which values are valid.
    """
    valid_scores = (
        score
        for score in scores
        if isinstance(score, int) and not isinstance(score, bool) and score >= 0
    )
    return sorted(valid_scores, reverse=True)[:MAX_HIGH_SCORES]


def load_high_scores(path: Optional[Path] = None) -> List[int]:
    """Return validated scores, or an empty list when the file is unusable.

    A missing, corrupted, or inaccessible high-score file should never prevent
    the game from starting.
    """
    score_file = path or DEFAULT_HIGH_SCORE_FILE
    try:
        with score_file.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        TypeError,
        ValueError,
    ):
        return []

    raw_scores = (
        payload.get("scores", []) if isinstance(payload, dict) else payload
    )
    if not isinstance(raw_scores, list):
        return []

    return normalize_high_scores(raw_scores)


def save_high_scores(scores: List[int], path: Optional[Path] = None) -> bool:
    """Persist up to five valid scores and return whether the operation worked."""
    score_file = path or DEFAULT_HIGH_SCORE_FILE
    valid_scores = normalize_high_scores(scores)

    temporary_file = None
    try:
        score_file.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            "w", encoding="utf-8", dir=score_file.parent, delete=False
        ) as file:
            temporary_file = Path(file.name)
            json.dump({"scores": valid_scores}, file, indent=2)
            file.write("\n")
        os.replace(temporary_file, score_file)
        return True
    except OSError:
        return False
    finally:
        if temporary_file and temporary_file.exists():
            try:
                temporary_file.unlink()
            except OSError:
                pass
