"""Phase 3 P3-3: independent IK, warm start, and whole-trajectory refinement."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
from scipy.optimize import minimize


LINK_LENGTHS_M = np.array([0.28, 0.23, 0.17])
LOWER_RAD = np.array([-2.8, -2.6, -2.8])
UPPER_RAD = np.array([2.8, 2.6, 2.8])
POSITION_TOLERANCE_M = 0.005
ORIENTATION_TOLERANCE_RAD = 0.03
JOINT_STEP_SCALE_RAD = 0.05
SMOOTH_WEIGHT = 0.08


def wrap_angle(angle: np.ndarray | float) -> np.ndarray | float:
    return np.arctan2(np.sin(angle), np.cos(angle))


def planar_fk(q: np.ndarray) -> tuple[np.ndarray, float]:
    absolute = np.cumsum(q)
    position = np.array(
        [
            np.sum(LINK_LENGTHS_M * np.cos(absolute)),
            np.sum(LINK_LENGTHS_M * np.sin(absolute)),
        ]
    )
    return position, float(absolute[-1])


def planar_position_jacobian(q: np.ndarray) -> np.ndarray:
    absolute = np.cumsum(q)
    jacobian = np.empty((2, 3), dtype=np.float64)
    for joint in range(3):
        jacobian[0, joint] = -np.sum(
            LINK_LENGTHS_M[joint:] * np.sin(absolute[joint:])
        )
        jacobian[1, joint] = np.sum(
            LINK_LENGTHS_M[joint:] * np.cos(absolute[joint:])
        )
    return jacobian


def make_noisy_task(timestamp: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    progress = timestamp / timestamp[-1]
    clean_q = np.column_stack(
        (
            0.20 + 0.35 * np.sin(2.0 * np.pi * progress),
            1.00 + 0.22 * np.sin(2.0 * np.pi * progress + 0.5),
            -0.45 + 0.18 * np.cos(2.0 * np.pi * progress),
        )
    )
    position = np.empty((len(timestamp), 2), dtype=np.float64)
    orientation = np.empty(len(timestamp), dtype=np.float64)
    for frame, q in enumerate(clean_q):
        position[frame], orientation[frame] = planar_fk(q)

    position[:, 0] += 0.0020 * np.sin(18.0 * np.pi * progress)
    position[:, 1] += 0.0015 * np.sin(22.0 * np.pi * progress + 0.4)
    orientation += np.deg2rad(0.5) * np.sin(20.0 * np.pi * progress)
    return position, orientation


def analytic_ik_branches(position: np.ndarray, orientation: float) -> tuple[np.ndarray, np.ndarray]:
    """Solve the two planar elbow branches after subtracting the final link."""
    wrist_2link = position - LINK_LENGTHS_M[2] * np.array(
        [np.cos(orientation), np.sin(orientation)]
    )
    radius_sq = float(np.dot(wrist_2link, wrist_2link))
    cosine_q2 = (
        radius_sq - LINK_LENGTHS_M[0] ** 2 - LINK_LENGTHS_M[1] ** 2
    ) / (2.0 * LINK_LENGTHS_M[0] * LINK_LENGTHS_M[1])
    if abs(cosine_q2) > 1.0 + 1e-9:
        raise ValueError("noisy target is outside the analytic IK workspace")
    cosine_q2 = float(np.clip(cosine_q2, -1.0, 1.0))

    branches = []
    for sign in (1.0, -1.0):
        q2 = sign * np.arccos(cosine_q2)
        q1 = np.arctan2(wrist_2link[1], wrist_2link[0]) - np.arctan2(
            LINK_LENGTHS_M[1] * np.sin(q2),
            LINK_LENGTHS_M[0] + LINK_LENGTHS_M[1] * np.cos(q2),
        )
        q3 = wrap_angle(orientation - q1 - q2)
        branches.append(np.array([q1, q2, q3]))
    return branches[0], branches[1]


def solve_framewise(
    target_position: np.ndarray, target_orientation: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    branch_positive = np.empty((len(target_position), 3), dtype=np.float64)
    branch_negative = np.empty_like(branch_positive)
    for frame, (position, orientation) in enumerate(
        zip(target_position, target_orientation, strict=True)
    ):
        branch_positive[frame], branch_negative[frame] = analytic_ik_branches(
            position, orientation
        )

    progress = np.linspace(0.0, 1.0, len(target_position))
    independent_positive = np.sin(8.0 * np.pi * progress) >= 0.0
    independent = np.where(
        independent_positive[:, None], branch_positive, branch_negative
    )
    warm_start = branch_positive
    return independent, warm_start


def objective_and_gradient(
    flattened_q: np.ndarray,
    target_position: np.ndarray,
    target_orientation: np.ndarray,
) -> tuple[float, np.ndarray]:
    q_trajectory = flattened_q.reshape(-1, 3)
    frame_count = len(q_trajectory)
    objective = 0.0
    gradient = np.zeros_like(q_trajectory)

    for frame, q in enumerate(q_trajectory):
        position, orientation = planar_fk(q)
        position_error = position - target_position[frame]
        orientation_error = float(wrap_angle(orientation - target_orientation[frame]))
        objective += np.dot(position_error, position_error) / (
            frame_count * POSITION_TOLERANCE_M**2
        )
        objective += orientation_error**2 / (
            frame_count * ORIENTATION_TOLERANCE_RAD**2
        )
        jacobian = planar_position_jacobian(q)
        gradient[frame] += 2.0 * jacobian.T @ position_error / (
            frame_count * POSITION_TOLERANCE_M**2
        )
        gradient[frame] += 2.0 * orientation_error / (
            frame_count * ORIENTATION_TOLERANCE_RAD**2
        )

    steps = np.diff(q_trajectory, axis=0)
    smooth_denominator = (frame_count - 1) * JOINT_STEP_SCALE_RAD**2
    objective += SMOOTH_WEIGHT * np.sum(steps**2) / smooth_denominator
    smooth_gradient = 2.0 * SMOOTH_WEIGHT * steps / smooth_denominator
    gradient[:-1] -= smooth_gradient
    gradient[1:] += smooth_gradient
    return float(objective), gradient.ravel()


def solve_whole_trajectory(
    warm_start: np.ndarray,
    target_position: np.ndarray,
    target_orientation: np.ndarray,
) -> np.ndarray:
    bounds = list(zip(np.tile(LOWER_RAD, len(warm_start)), np.tile(UPPER_RAD, len(warm_start))))
    result = minimize(
        lambda value: objective_and_gradient(
            value, target_position, target_orientation
        ),
        warm_start.ravel(),
        jac=True,
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": 800, "ftol": 1e-12, "gtol": 1e-8},
    )
    if not result.success:
        raise RuntimeError(f"whole-trajectory optimization failed: {result.message}")
    return result.x.reshape(-1, 3)


def evaluate(
    q_trajectory: np.ndarray,
    target_position: np.ndarray,
    target_orientation: np.ndarray,
    dt: float,
) -> tuple[dict[str, float | int], np.ndarray, np.ndarray, np.ndarray]:
    actual_position = np.empty_like(target_position)
    actual_orientation = np.empty_like(target_orientation)
    for frame, q in enumerate(q_trajectory):
        actual_position[frame], actual_orientation[frame] = planar_fk(q)
    position_error = np.linalg.norm(actual_position - target_position, axis=1)
    orientation_error = np.abs(wrap_angle(actual_orientation - target_orientation))
    adjacent_change = np.linalg.norm(np.diff(q_trajectory, axis=0), axis=1)
    velocity = np.diff(q_trajectory, axis=0) / dt
    acceleration = np.diff(q_trajectory, n=2, axis=0) / dt**2
    branch_flips = int(np.sum(np.sign(q_trajectory[1:, 1]) != np.sign(q_trajectory[:-1, 1])))
    metrics: dict[str, float | int] = {
        "mean_position_error_m": float(np.mean(position_error)),
        "max_position_error_m": float(np.max(position_error)),
        "max_orientation_error_rad": float(np.max(orientation_error)),
        "mean_adjacent_q_change_rad": float(np.mean(adjacent_change)),
        "max_adjacent_q_change_rad": float(np.max(adjacent_change)),
        "max_velocity_norm_rad_s": float(np.max(np.linalg.norm(velocity, axis=1))),
        "max_acceleration_norm_rad_s2": float(
            np.max(np.linalg.norm(acceleration, axis=1))
        ),
        "elbow_branch_flips": branch_flips,
    }
    return metrics, actual_position, position_error, adjacent_change


def run_trajectory_experiment() -> tuple[dict[str, np.ndarray], dict[str, object]]:
    timestamp = np.arange(81, dtype=np.float64) / 30.0
    dt = float(timestamp[1] - timestamp[0])
    target_position, target_orientation = make_noisy_task(timestamp)
    independent, warm_start = solve_framewise(target_position, target_orientation)
    whole = solve_whole_trajectory(warm_start, target_position, target_orientation)

    arrays: dict[str, np.ndarray] = {
        "timestamp": timestamp,
        "target_position": target_position,
        "target_orientation": target_orientation,
        "independent_q": independent,
        "warm_start_q": warm_start,
        "whole_trajectory_q": whole,
    }
    metrics: dict[str, object] = {
        "frame_count": len(timestamp),
        "sample_rate_hz": 1.0 / dt,
        "position_tolerance_m": POSITION_TOLERANCE_M,
        "orientation_tolerance_rad": ORIENTATION_TOLERANCE_RAD,
        "smooth_weight": SMOOTH_WEIGHT,
        "cases": {},
    }
    for name, trajectory in (
        ("independent", independent),
        ("warm_start", warm_start),
        ("whole_trajectory", whole),
    ):
        case_metrics, actual_position, position_error, adjacent_change = evaluate(
            trajectory, target_position, target_orientation, dt
        )
        metrics["cases"][name] = case_metrics
        arrays[f"{name}_actual_position"] = actual_position
        arrays[f"{name}_position_error"] = position_error
        arrays[f"{name}_adjacent_q_change"] = adjacent_change
    return arrays, metrics


def save_outputs(
    phase_root: Path, arrays: dict[str, np.ndarray], metrics: dict[str, object]
) -> None:
    data_dir = phase_root / "data"
    output_dir = phase_root / "outputs"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_path = data_dir / "p3c_whole_trajectory_optimization.npz"
    report_path = output_dir / "p3c_whole_trajectory_optimization.json"
    figure_path = output_dir / "p3c_whole_trajectory_optimization.png"
    np.savez_compressed(data_path, **arrays)
    report_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    figure, axes = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
    axes[0, 0].plot(*arrays["target_position"].T, "k--", label="target")
    for name, label in (
        ("independent", "independent IK"),
        ("warm_start", "warm-start IK"),
        ("whole_trajectory", "whole trajectory"),
    ):
        axes[0, 0].plot(*arrays[f"{name}_actual_position"].T, label=label)
    axes[0, 0].set_aspect("equal")
    axes[0, 0].set_title("All methods reach nearly the same wrist path")
    axes[0, 0].set_xlabel("x [m]")
    axes[0, 0].set_ylabel("y [m]")
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(alpha=0.25)

    time_s = arrays["timestamp"]
    axes[0, 1].plot(time_s, arrays["independent_q"][:, 1], label="independent IK")
    axes[0, 1].plot(time_s, arrays["warm_start_q"][:, 1], label="warm-start IK")
    axes[0, 1].plot(
        time_s, arrays["whole_trajectory_q"][:, 1], label="whole trajectory"
    )
    axes[0, 1].set_title("Elbow branch and q2 continuity")
    axes[0, 1].set_xlabel("time [s]")
    axes[0, 1].set_ylabel("q2 [rad]")
    axes[0, 1].legend(fontsize=8)
    axes[0, 1].grid(alpha=0.25)

    for name, label in (
        ("independent", "independent IK"),
        ("warm_start", "warm-start IK"),
        ("whole_trajectory", "whole trajectory"),
    ):
        axes[1, 0].plot(
            time_s,
            1000.0 * arrays[f"{name}_position_error"],
            label=label,
        )
    axes[1, 0].axhline(
        1000.0 * POSITION_TOLERANCE_M,
        color="black",
        linestyle="--",
        label="position tolerance",
    )
    axes[1, 0].set_title("FK task error")
    axes[1, 0].set_xlabel("time [s]")
    axes[1, 0].set_ylabel("position error [mm]")
    axes[1, 0].legend(fontsize=8)
    axes[1, 0].grid(alpha=0.25)

    step_time = time_s[1:]
    for name, label in (
        ("independent", "independent IK"),
        ("warm_start", "warm-start IK"),
        ("whole_trajectory", "whole trajectory"),
    ):
        axes[1, 1].plot(
            step_time,
            arrays[f"{name}_adjacent_q_change"],
            label=label,
        )
    axes[1, 1].set_title("Adjacent joint-space change")
    axes[1, 1].set_xlabel("time [s]")
    axes[1, 1].set_ylabel("||q[t]-q[t-1]|| [rad]")
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].grid(alpha=0.25)
    figure.savefig(figure_path, dpi=160)
    plt.close(figure)

    print(f"\nSaved data   to: {data_path}")
    print(f"Saved report to: {report_path}")
    print(f"Saved figure to: {figure_path}")


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    arrays, metrics = run_trajectory_experiment()
    print("Phase 3 P3-3 - frame-wise IK versus whole-trajectory optimization")
    print(
        f"frames / sample rate              = "
        f"{metrics['frame_count']} / {metrics['sample_rate_hz']:.1f} Hz"
    )
    print(
        f"task tolerances position/orient.  = "
        f"{1000.0 * metrics['position_tolerance_m']:.1f} mm / "
        f"{np.rad2deg(metrics['orientation_tolerance_rad']):.3f} deg"
    )
    print(f"whole-trajectory smooth weight    = {metrics['smooth_weight']:.3f}")
    print("\nCase summaries")
    for name in ("independent", "warm_start", "whole_trajectory"):
        case = metrics["cases"][name]
        print(name)
        print(
            f"  mean / max position error       = "
            f"{1000.0 * case['mean_position_error_m']:.4f} / "
            f"{1000.0 * case['max_position_error_m']:.4f} mm"
        )
        print(
            f"  max orientation error           = "
            f"{np.rad2deg(case['max_orientation_error_rad']):.5f} deg"
        )
        print(f"  elbow branch flips              = {case['elbow_branch_flips']}")
        print(
            f"  mean / max adjacent q change    = "
            f"{case['mean_adjacent_q_change_rad']:.5f} / "
            f"{case['max_adjacent_q_change_rad']:.5f} rad"
        )
        print(
            f"  max velocity / acceleration     = "
            f"{case['max_velocity_norm_rad_s']:.3f} rad/s / "
            f"{case['max_acceleration_norm_rad_s2']:.3f} rad/s^2"
        )
    print("\nIndependent FK success does not guarantee a continuous joint trajectory.")
    print("Whole-trajectory refinement trades a small task error for temporal quality.")
    save_outputs(phase_root, arrays, metrics)


if __name__ == "__main__":
    main()

