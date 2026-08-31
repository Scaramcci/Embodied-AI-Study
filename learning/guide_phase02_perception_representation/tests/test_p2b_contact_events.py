from pathlib import Path
import sys

import numpy as np


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from p2b_contact_events import (  # noqa: E402
    CONTACT_THRESHOLD_M,
    run_contact_experiment,
)


def test_contact_packet_shapes_and_units() -> None:
    arrays, metrics = run_contact_experiment()

    assert arrays["timestamp"].shape == (121,)
    assert arrays["world_T_object"].shape == (121, 4, 4)
    assert arrays["hand_keypoints_world"].shape == (121, 6, 3)
    assert arrays["hand_object_distance"].shape == (121, 5)
    assert arrays["contact_event"].shape == (121, 5)
    assert arrays["contact_event"].dtype == np.bool_
    assert metrics["aligned_min_distance_m"] < CONTACT_THRESHOLD_M
    assert metrics["aligned_max_distance_m"] > CONTACT_THRESHOLD_M


def test_timestamp_offset_changes_contact_decisions() -> None:
    arrays, metrics = run_contact_experiment()

    expected = arrays["hand_object_distance"] < CONTACT_THRESHOLD_M
    np.testing.assert_array_equal(arrays["contact_event"], expected)
    assert metrics["mismatched_contact_entries"] > 0
    assert len(metrics["frames_with_any_mismatch"]) > 0

