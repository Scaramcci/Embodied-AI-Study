import sys
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from p4c_rolling_force_control import run_force_experiment  # noqa: E402


def test_balanced_controller_reaches_target() -> None:
    _, summary = run_force_experiment()
    balanced = summary["cases"]["balanced"]
    baseline = summary["cases"]["no_adjustment"]
    assert balanced["final_30_frame_mae_n"] < 0.15
    assert balanced["final_30_frame_mae_n"] < baseline["final_30_frame_mae_n"]


def test_regularization_reduces_initial_command_jump() -> None:
    _, summary = run_force_experiment()
    weak = summary["cases"]["weak_regularization"]
    balanced = summary["cases"]["balanced"]
    over = summary["cases"]["over_regularized"]
    assert weak["max_command_step_rad"] > balanced["max_command_step_rad"]
    assert balanced["max_command_step_rad"] > over["max_command_step_rad"]
