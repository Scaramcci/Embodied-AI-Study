from pathlib import Path
import sys


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from p3c_whole_trajectory_optimization import (  # noqa: E402
    POSITION_TOLERANCE_M,
    run_trajectory_experiment,
)


def test_trajectory_packet_shapes() -> None:
    arrays, metrics = run_trajectory_experiment()

    assert arrays["target_position"].shape == (81, 2)
    assert arrays["independent_q"].shape == (81, 3)
    assert arrays["whole_trajectory_q"].shape == (81, 3)
    assert metrics["frame_count"] == 81


def test_continuity_strategies_and_task_tolerance() -> None:
    _, metrics = run_trajectory_experiment()
    independent = metrics["cases"]["independent"]
    warm = metrics["cases"]["warm_start"]
    whole = metrics["cases"]["whole_trajectory"]

    assert independent["elbow_branch_flips"] > 0
    assert warm["elbow_branch_flips"] == 0
    assert independent["max_adjacent_q_change_rad"] > 10.0 * warm["max_adjacent_q_change_rad"]
    assert whole["mean_adjacent_q_change_rad"] < warm["mean_adjacent_q_change_rad"]
    assert whole["max_position_error_m"] < POSITION_TOLERANCE_M

