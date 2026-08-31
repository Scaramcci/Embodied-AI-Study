import sys
from pathlib import Path

import numpy as np


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from p4b_contact_phase_scheduler import run_scheduler_experiment  # noqa: E402


def test_hysteresis_suppresses_chatter() -> None:
    _, metrics = run_scheduler_experiment()
    assert metrics["raw_controller_switches"] > metrics["robust_controller_switches"]
    assert metrics["robust_contact_transition_indices"] == [46, 112]
    assert metrics["robust_controller_switches"] == 2


def test_timestamp_offset_changes_scheduler_output() -> None:
    arrays, metrics = run_scheduler_experiment(offset_frames=5)
    assert metrics["delayed_contact_transition_indices"] == [51, 117]
    assert np.any(arrays["phase_mismatch"])
    assert np.any(arrays["controller_mismatch"])
