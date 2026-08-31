import sys
from pathlib import Path

import numpy as np


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from p5a_demonstration_contract import (  # noqa: E402
    ACTION_CHUNK_HORIZON,
    build_action_chunks,
    run_demonstration_experiment,
    validate_chunks,
    validate_demonstration,
)


def test_canonical_demonstration_and_chunks_pass() -> None:
    arrays, metrics = run_demonstration_experiment()
    validate_demonstration(arrays)
    validate_chunks(
        arrays,
        arrays["action_chunk_rad"],
        arrays["action_chunk_valid"],
        arrays["action_chunk_source_episode"],
    )
    assert metrics["episode_lengths"] == [9, 7]
    assert arrays["action_chunk_rad"].shape == (16, ACTION_CHUNK_HORIZON, 3)


def test_chunk_stops_at_first_episode_boundary() -> None:
    arrays, _ = run_demonstration_experiment()
    _, mask, source_episode, source_local_frame = build_action_chunks(arrays)
    assert np.array_equal(mask[7], np.array([True, True, False, False]))
    assert np.array_equal(source_episode[7], np.array([0, 0, -1, -1]))
    assert np.array_equal(source_local_frame[7], np.array([7, 8, -1, -1]))


def test_deliberate_violations_are_rejected() -> None:
    _, metrics = run_demonstration_experiment()
    assert all(
        result.startswith("REJECTED:")
        for result in metrics["violations"].values()
    )
