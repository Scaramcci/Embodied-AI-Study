"""Phase 5 P5-2: offline BC error, distribution shift, and rollout metrics."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np


DT_S = 0.05
SAMPLE_RATE_HZ = 1.0 / DT_S
ROLLOUT_FRAMES = 161
TRAIN_ERROR_LIMIT_M = 0.08
SUCCESS_TOLERANCE_M = 0.02
CHUNK_HORIZON = 8


def expert_action(position_m: np.ndarray | float, goal_m: np.ndarray | float) -> np.ndarray:
    error = np.asarray(goal_m) - np.asarray(position_m)
    return np.clip(0.35 * error + 8.0 * error**3, -1.5, 1.5)


def make_expert_dataset(seed: int = 7) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    observations: list[np.ndarray] = []
    actions: list[float] = []
    errors: list[float] = []
    episode_ids: list[int] = []
    for episode in range(36):
        goal = rng.uniform(-0.4, 0.4)
        position = goal + rng.uniform(-TRAIN_ERROR_LIMIT_M, TRAIN_ERROR_LIMIT_M)
        for _ in range(31):
            action = float(expert_action(position, goal))
            observations.append(np.array([position, goal, 1.0]))
            actions.append(action)
            errors.append(goal - position)
            episode_ids.append(episode)
            position += DT_S * action
    return {
        "observation": np.asarray(observations),
        "expert_action_mps": np.asarray(actions),
        "goal_error_m": np.asarray(errors),
        "episode_id": np.asarray(episode_ids),
    }


def fit_linear_bc(dataset: dict[str, np.ndarray]) -> np.ndarray:
    weights, *_ = np.linalg.lstsq(
        dataset["observation"], dataset["expert_action_mps"], rcond=None
    )
    return weights


def bc_action(position_m: np.ndarray | float, goal_m: np.ndarray | float, weights: np.ndarray) -> np.ndarray:
    position = np.asarray(position_m)
    goal = np.asarray(goal_m)
    features = np.stack(np.broadcast_arrays(position, goal, np.ones_like(position)), axis=-1)
    return np.clip(features @ weights, -1.5, 1.5)


def rollout(
    name: str,
    policy,
    initial_position_m: float,
    goal_m: float,
    replan_interval: int = 1,
    chunk_horizon: int = 1,
    disturbance_state_frame: int | None = None,
    disturbance_m: float = 0.0,
) -> dict[str, object]:
    position = np.empty(ROLLOUT_FRAMES, dtype=np.float64)
    action = np.zeros(ROLLOUT_FRAMES - 1, dtype=np.float64)
    position[0] = initial_position_m
    active_chunk = np.zeros(chunk_horizon, dtype=np.float64)
    chunk_start = 0
    next_replan = 0

    for frame in range(ROLLOUT_FRAMES - 1):
        if frame >= next_replan:
            imagined_position = position[frame]
            for step in range(chunk_horizon):
                active_chunk[step] = float(policy(imagined_position, goal_m))
                imagined_position += DT_S * active_chunk[step]
            chunk_start = frame
            next_replan = frame + replan_interval
        chunk_index = min(frame - chunk_start, chunk_horizon - 1)
        action[frame] = active_chunk[chunk_index]
        position[frame + 1] = position[frame] + DT_S * action[frame]
        if disturbance_state_frame == frame + 1:
            position[frame + 1] += disturbance_m

    error = goal_m - position
    success = bool(np.all(np.abs(error[-10:]) <= SUCCESS_TOLERANCE_M))
    outside_fraction = float(np.mean(np.abs(error) > TRAIN_ERROR_LIMIT_M))
    return {
        "name": name,
        "position_m": position,
        "action_mps": action,
        "goal_error_m": error,
        "final_error_m": float(abs(error[-1])),
        "trajectory_rmse_m": float(np.sqrt(np.mean(error**2))),
        "outside_training_fraction": outside_fraction,
        "success": success,
        "replan_interval": replan_interval,
        "chunk_horizon": chunk_horizon,
    }


def discrete_frechet(curve_a: np.ndarray, curve_b: np.ndarray) -> float:
    cache = np.full((len(curve_a), len(curve_b)), np.nan)

    def recurse(i: int, j: int) -> float:
        if not np.isnan(cache[i, j]):
            return float(cache[i, j])
        distance = float(np.linalg.norm(curve_a[i] - curve_b[j]))
        if i == 0 and j == 0:
            value = distance
        elif i > 0 and j == 0:
            value = max(recurse(i - 1, 0), distance)
        elif i == 0 and j > 0:
            value = max(recurse(0, j - 1), distance)
        else:
            value = max(
                min(recurse(i - 1, j), recurse(i - 1, j - 1), recurse(i, j - 1)),
                distance,
            )
        cache[i, j] = value
        return value

    return recurse(len(curve_a) - 1, len(curve_b) - 1)


def trajectory_to_joint_positions(position_m: np.ndarray) -> np.ndarray:
    frames = len(position_m)
    joints = np.zeros((frames, 3, 3), dtype=np.float64)
    joints[:, 0] = np.column_stack((0.30 * position_m, np.zeros(frames), np.full(frames, 0.50)))
    joints[:, 1] = np.column_stack((0.65 * position_m, np.full(frames, 0.04), np.full(frames, 0.70)))
    joints[:, 2] = np.column_stack((position_m, np.zeros(frames), np.full(frames, 0.90)))
    return joints


def yaw_quaternions(yaw_rad: np.ndarray) -> np.ndarray:
    quaternion = np.zeros((len(yaw_rad), 4), dtype=np.float64)
    quaternion[:, 2] = np.sin(yaw_rad / 2.0)
    quaternion[:, 3] = np.cos(yaw_rad / 2.0)
    return quaternion


def paper_metric_example(reference: dict[str, object], candidate: dict[str, object]) -> dict[str, object]:
    reference_joints = trajectory_to_joint_positions(reference["position_m"])
    candidate_joints = trajectory_to_joint_positions(candidate["position_m"])
    position_difference = candidate_joints - reference_joints
    mpjpe = float(np.mean(np.linalg.norm(position_difference, axis=2)))

    reference_quaternion = yaw_quaternions(np.zeros(ROLLOUT_FRAMES))
    candidate_quaternion = yaw_quaternions(0.25 * candidate["goal_error_m"])
    dots = np.abs(np.sum(reference_quaternion * candidate_quaternion, axis=1))
    quat_distance = float(np.mean(2.0 * np.arccos(np.clip(dots, -1.0, 1.0))))

    reference_velocity = np.diff(reference_joints, axis=0) / DT_S
    candidate_velocity = np.diff(candidate_joints, axis=0) / DT_S
    velocity_error = float(
        np.mean(np.linalg.norm(candidate_velocity - reference_velocity, axis=2))
    )
    reference_acceleration = np.diff(reference_velocity, axis=0) / DT_S
    candidate_acceleration = np.diff(candidate_velocity, axis=0) / DT_S
    acceleration_error = float(
        np.mean(np.linalg.norm(candidate_acceleration - reference_acceleration, axis=2))
    )
    frechet = discrete_frechet(reference_joints[:, 2], candidate_joints[:, 2])

    hand_relative_object = np.column_stack(
        (
            np.linspace(0.0, 0.012, ROLLOUT_FRAMES),
            0.0015 * np.sin(np.linspace(0.0, 4.0 * np.pi, ROLLOUT_FRAMES)),
            np.zeros(ROLLOUT_FRAMES),
        )
    )
    slip = float(np.sum(np.linalg.norm(np.diff(hand_relative_object, axis=0), axis=1)))
    reference_edges = np.array([0.040, 0.052, 0.061, 0.073, 0.084, 0.095])
    candidate_edges = reference_edges * np.array([1.02, 0.97, 1.05, 0.96, 1.01, 1.04])
    geometry_error = float(
        np.mean(np.abs(candidate_edges - reference_edges) / reference_edges)
    )
    return {
        "mpjpe_m": mpjpe,
        "mean_quaternion_distance_rad": quat_distance,
        "velocity_error_mps": velocity_error,
        "acceleration_error_mps2": acceleration_error,
        "discrete_frechet_m": frechet,
        "cumulative_slip_m": slip,
        "normalized_geometry_error": geometry_error,
        "task_success": bool(candidate["success"]),
        "success_predicate": "absolute goal error <= 0.02 m for the final 10 frames",
    }


def first_response_after_disturbance(
    disturbed_action: np.ndarray,
    nominal_action: np.ndarray,
    disturbance_state_frame: int,
    threshold: float = 1e-6,
) -> int | None:
    candidates = np.flatnonzero(
        np.abs(disturbed_action - nominal_action) > threshold
    )
    candidates = candidates[candidates >= disturbance_state_frame]
    return None if len(candidates) == 0 else int(candidates[0])


def run_offline_vs_rollout_experiment() -> tuple[dict[str, object], dict[str, object]]:
    dataset = make_expert_dataset()
    weights = fit_linear_bc(dataset)
    offline_prediction = dataset["observation"] @ weights
    offline_error = offline_prediction - dataset["expert_action_mps"]

    goal = 0.40
    expert_policy = lambda position, target: expert_action(position, target)
    bc_policy = lambda position, target: bc_action(position, target, weights)
    rollouts = {
        "expert_ood": rollout("expert_ood", expert_policy, goal - 0.80, goal),
        "bc_id": rollout("bc_id", bc_policy, goal - 0.05, goal),
        "bc_ood": rollout("bc_ood", bc_policy, goal - 0.80, goal),
    }

    disturbance_frame = 37
    disturbance_m = -0.20
    nominal_step = rollout("nominal_step", bc_policy, goal - 0.05, goal)
    disturbed_step = rollout(
        "disturbed_replan_every_step",
        bc_policy,
        goal - 0.05,
        goal,
        replan_interval=1,
        chunk_horizon=CHUNK_HORIZON,
        disturbance_state_frame=disturbance_frame,
        disturbance_m=disturbance_m,
    )
    nominal_chunk = rollout(
        "nominal_full_chunk",
        bc_policy,
        goal - 0.05,
        goal,
        replan_interval=CHUNK_HORIZON,
        chunk_horizon=CHUNK_HORIZON,
    )
    disturbed_chunk = rollout(
        "disturbed_execute_full_chunk",
        bc_policy,
        goal - 0.05,
        goal,
        replan_interval=CHUNK_HORIZON,
        chunk_horizon=CHUNK_HORIZON,
        disturbance_state_frame=disturbance_frame,
        disturbance_m=disturbance_m,
    )
    step_response = first_response_after_disturbance(
        disturbed_step["action_mps"], nominal_step["action_mps"], disturbance_frame
    )
    chunk_response = first_response_after_disturbance(
        disturbed_chunk["action_mps"], nominal_chunk["action_mps"], disturbance_frame
    )
    rollouts.update(
        {
            "disturbed_replan_every_step": disturbed_step,
            "disturbed_execute_full_chunk": disturbed_chunk,
        }
    )

    metrics = paper_metric_example(rollouts["expert_ood"], rollouts["bc_ood"])
    summary: dict[str, object] = {
        "training_episodes": int(len(np.unique(dataset["episode_id"]))),
        "training_samples": int(len(dataset["expert_action_mps"])),
        "training_error_range_m": [
            float(np.min(dataset["goal_error_m"])),
            float(np.max(dataset["goal_error_m"])),
        ],
        "bc_weights_position_goal_bias": weights.tolist(),
        "offline_action_mae_mps": float(np.mean(np.abs(offline_error))),
        "offline_action_max_error_mps": float(np.max(np.abs(offline_error))),
        "rollouts": {
            name: {
                "initial_error_m": float(abs(case["goal_error_m"][0])),
                "final_error_m": case["final_error_m"],
                "trajectory_rmse_m": case["trajectory_rmse_m"],
                "outside_training_fraction": case["outside_training_fraction"],
                "success": case["success"],
            }
            for name, case in rollouts.items()
        },
        "action_chunk": {
            "horizon": CHUNK_HORIZON,
            "disturbance_state_frame": disturbance_frame,
            "disturbance_m": disturbance_m,
            "every_step_first_response_frame": step_response,
            "full_chunk_first_response_frame": chunk_response,
            "full_chunk_extra_delay_frames": None
            if step_response is None or chunk_response is None
            else chunk_response - step_response,
        },
        "paper_metric_example_bc_ood_vs_expert": metrics,
    }
    arrays: dict[str, object] = {
        "dataset": dataset,
        "weights": weights,
        "offline_prediction": offline_prediction,
        "rollouts": rollouts,
    }
    return arrays, summary


def save_outputs(phase_root: Path, arrays: dict[str, object], summary: dict[str, object]) -> None:
    output_dir = phase_root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "p5b_offline_vs_rollout.json"
    csv_path = output_dir / "p5b_offline_vs_rollout.csv"
    figure_path = output_dir / "p5b_offline_vs_rollout.png"
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["case", "frame", "timestamp_s", "position_m", "goal_error_m"])
        for name, case in arrays["rollouts"].items():
            for frame, (position, error) in enumerate(
                zip(case["position_m"], case["goal_error_m"])
            ):
                writer.writerow([name, frame, frame * DT_S, position, error])

    weights = arrays["weights"]
    dataset = arrays["dataset"]
    error_grid = np.linspace(-0.9, 0.9, 500)
    goal_grid = np.zeros_like(error_grid)
    position_grid = goal_grid - error_grid
    expert_grid = expert_action(position_grid, goal_grid)
    bc_grid = bc_action(position_grid, goal_grid, weights)
    time_s = np.arange(ROLLOUT_FRAMES) * DT_S

    figure, axes = plt.subplots(3, 1, figsize=(11, 10), constrained_layout=True)
    axes[0].scatter(
        dataset["goal_error_m"],
        dataset["expert_action_mps"],
        s=7,
        alpha=0.16,
        label="expert training samples",
    )
    axes[0].plot(error_grid, expert_grid, color="black", label="expert outside training range")
    axes[0].plot(error_grid, bc_grid, color="tab:red", linestyle="--", label="linear BC extrapolation")
    axes[0].axvspan(-TRAIN_ERROR_LIMIT_M, TRAIN_ERROR_LIMIT_M, color="tab:green", alpha=0.10, label="training support")
    axes[0].set_xlabel("goal error [m]")
    axes[0].set_ylabel("action velocity [m/s]")
    axes[0].set_title("Low offline error only describes the narrow expert-state distribution")
    axes[0].legend(ncol=2, fontsize=8)
    axes[0].grid(alpha=0.25)

    for name, color in (("expert_ood", "black"), ("bc_id", "tab:green"), ("bc_ood", "tab:red")):
        case = arrays["rollouts"][name]
        axes[1].plot(time_s, np.abs(case["goal_error_m"]), label=name, color=color)
    axes[1].axhline(SUCCESS_TOLERANCE_M, color="tab:blue", linestyle=":", label="success tolerance")
    axes[1].axhline(TRAIN_ERROR_LIMIT_M, color="tab:orange", linestyle=":", label="training error envelope")
    axes[1].set_yscale("log")
    axes[1].set_ylabel("absolute goal error [m]")
    axes[1].set_title("Teacher-forced accuracy versus closed-loop ID/OOD rollout")
    axes[1].legend(ncol=2, fontsize=8)
    axes[1].grid(alpha=0.25, which="both")

    for name, color in (("disturbed_replan_every_step", "tab:blue"), ("disturbed_execute_full_chunk", "tab:purple")):
        case = arrays["rollouts"][name]
        axes[2].plot(time_s, case["goal_error_m"], label=name, color=color)
    disturbance_frame = summary["action_chunk"]["disturbance_state_frame"]
    axes[2].axvline(disturbance_frame * DT_S, color="tab:red", linestyle="--", label="external disturbance")
    axes[2].axhline(0.0, color="black", linewidth=0.8)
    axes[2].set_xlabel("time [s]")
    axes[2].set_ylabel("signed goal error [m]")
    axes[2].set_title("Full-chunk execution delays feedback correction")
    axes[2].legend(fontsize=8)
    axes[2].grid(alpha=0.25)
    figure.savefig(figure_path, dpi=160)
    plt.close(figure)

    print(f"\nSaved table  to: {csv_path}")
    print(f"Saved report to: {report_path}")
    print(f"Saved figure to: {figure_path}")


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    arrays, summary = run_offline_vs_rollout_experiment()
    print("Phase 5 P5-2 - offline BC error versus closed-loop rollout")
    print(f"training episodes / samples       = {summary['training_episodes']} / {summary['training_samples']}")
    print(f"training goal-error range [m]     = {np.round(summary['training_error_range_m'], 5)}")
    print(f"linear BC weights [x,goal,bias]   = {np.round(summary['bc_weights_position_goal_bias'], 6)}")
    print(f"offline action MAE / max error    = {summary['offline_action_mae_mps']:.6f} / {summary['offline_action_max_error_mps']:.6f} m/s")
    print("\nClosed-loop rollout summaries")
    for name in ("expert_ood", "bc_id", "bc_ood"):
        case = summary["rollouts"][name]
        print(name)
        print(f"  initial / final goal error      = {case['initial_error_m']:.4f} / {case['final_error_m']:.4f} m")
        print(f"  trajectory RMSE                 = {case['trajectory_rmse_m']:.4f} m")
        print(f"  outside training distribution   = {100.0 * case['outside_training_fraction']:.1f}% frames")
        print(f"  task success                    = {case['success']}")

    chunk = summary["action_chunk"]
    print("\nAction-chunk disturbance response")
    print(f"  horizon / full execute interval = {chunk['horizon']} / {chunk['horizon']} frames")
    print(f"  disturbance                     = {chunk['disturbance_m']:+.3f} m at state frame {chunk['disturbance_state_frame']}")
    print(f"  replan-every-step response      = action frame {chunk['every_step_first_response_frame']}")
    print(f"  execute-full-chunk response     = action frame {chunk['full_chunk_first_response_frame']}")
    print(f"  extra feedback delay            = {chunk['full_chunk_extra_delay_frames']} frames")

    metrics = summary["paper_metric_example_bc_ood_vs_expert"]
    print("\nPaper-style metrics: BC OOD rollout versus expert rollout")
    print(f"  MPJPE                            = {1000.0 * metrics['mpjpe_m']:.3f} mm")
    print(f"  mean Quat distance              = {metrics['mean_quaternion_distance_rad']:.5f} rad")
    print(f"  velocity / acceleration error   = {metrics['velocity_error_mps']:.4f} m/s / {metrics['acceleration_error_mps2']:.4f} m/s^2")
    print(f"  discrete Frechet distance       = {metrics['discrete_frechet_m']:.4f} m")
    print(f"  cumulative hand-object slip     = {1000.0 * metrics['cumulative_slip_m']:.3f} mm")
    print(f"  normalized geometry error       = {100.0 * metrics['normalized_geometry_error']:.3f}%")
    print(f"  task success                    = {metrics['task_success']}")
    print("\nLow teacher-forced action error is not a closed-loop success guarantee.")
    print("Trajectory, contact, and task metrics answer different questions.")
    save_outputs(phase_root, arrays, summary)


if __name__ == "__main__":
    main()
