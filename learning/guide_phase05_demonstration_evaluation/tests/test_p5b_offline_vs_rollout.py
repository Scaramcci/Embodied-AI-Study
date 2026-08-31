import sys
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from p5b_offline_vs_rollout import run_offline_vs_rollout_experiment  # noqa: E402


def test_low_offline_error_does_not_guarantee_ood_success() -> None:
    _, summary = run_offline_vs_rollout_experiment()
    assert summary["offline_action_mae_mps"] < 0.001
    assert summary["rollouts"]["bc_id"]["success"] is True
    assert summary["rollouts"]["bc_ood"]["success"] is False
    assert summary["rollouts"]["expert_ood"]["success"] is True


def test_full_chunk_delays_feedback_response() -> None:
    _, summary = run_offline_vs_rollout_experiment()
    chunk = summary["action_chunk"]
    assert chunk["every_step_first_response_frame"] == chunk["disturbance_state_frame"]
    assert chunk["full_chunk_extra_delay_frames"] > 0


def test_paper_metrics_are_nonnegative_and_success_is_false() -> None:
    _, summary = run_offline_vs_rollout_experiment()
    metrics = summary["paper_metric_example_bc_ood_vs_expert"]
    numeric = [value for key, value in metrics.items() if key not in ("task_success", "success_predicate")]
    assert all(value >= 0.0 for value in numeric)
    assert metrics["task_success"] is False
