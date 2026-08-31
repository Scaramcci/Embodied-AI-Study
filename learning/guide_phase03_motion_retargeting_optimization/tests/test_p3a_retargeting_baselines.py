from pathlib import Path
import sys

import numpy as np


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from p3a_retargeting_baselines import (  # noqa: E402
    ROBOT_LOWER_RAD,
    ROBOT_UPPER_RAD,
    run_retargeting_experiment,
)


def test_retargeting_shapes_and_limits() -> None:
    arrays, metrics = run_retargeting_experiment()

    assert arrays["human_q"].shape == (121, 2)
    assert arrays["joint_copy_robot_q"].shape == (121, 3)
    assert arrays["task_retarget_robot_q"].shape == (121, 3)
    assert np.all(arrays["task_retarget_robot_q"] >= ROBOT_LOWER_RAD)
    assert np.all(arrays["task_retarget_robot_q"] <= ROBOT_UPPER_RAD)
    assert metrics["task_retarget_min_limit_margin_rad"] >= 0.0


def test_task_space_retargeting_improves_selected_task() -> None:
    _, metrics = run_retargeting_experiment()

    assert (
        metrics["task_retarget_mean_position_error_m"]
        < 0.1 * metrics["joint_copy_mean_position_error_m"]
    )
    assert metrics["task_retarget_max_position_error_m"] < 0.002
    assert metrics["task_retarget_max_orientation_error_rad"] < np.deg2rad(0.1)

