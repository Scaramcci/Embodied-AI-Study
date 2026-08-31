from pathlib import Path
import sys


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from p3b_arm_plane_losses import run_arm_plane_experiment  # noqa: E402


def test_arm_plane_packet_and_fixed_wrist_task() -> None:
    arrays, metrics = run_arm_plane_experiment()

    assert arrays["wrist_position"].shape == (121, 3)
    assert arrays["reference_elbow"].shape == (121, 3)
    assert arrays["plane_plus_smooth_elbow"].shape == (121, 3)
    assert metrics["all_cases_wrist_task_error_m"] == 0.0


def test_plane_and_smoothness_change_redundant_elbow_quality() -> None:
    _, metrics = run_arm_plane_experiment()
    task_only = metrics["cases"]["task_only"]
    plane_only = metrics["cases"]["plane_only"]
    balanced = metrics["cases"]["plane_plus_smooth"]
    over_smooth = metrics["cases"]["over_smooth"]

    assert plane_only["mean_arm_plane_error_deg"] < task_only["mean_arm_plane_error_deg"]
    assert balanced["max_adjacent_elbow_change_m"] < task_only["max_adjacent_elbow_change_m"]
    assert over_smooth["mean_adjacent_elbow_change_m"] < plane_only["mean_adjacent_elbow_change_m"]
    assert over_smooth["mean_arm_plane_error_deg"] > plane_only["mean_arm_plane_error_deg"]

