"""Phase 3 P3-1: joint-copy versus task-space motion retargeting."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
from scipy.optimize import least_squares


HUMAN_LINK_LENGTHS_M = np.array([0.32, 0.26])
ROBOT_LINK_LENGTHS_M = np.array([0.28, 0.23, 0.17])
ROBOT_LOWER_RAD = np.deg2rad(np.array([-160.0, -140.0, -160.0]))
ROBOT_UPPER_RAD = np.deg2rad(np.array([160.0, 140.0, 160.0]))


def wrap_angle(angle: np.ndarray | float) -> np.ndarray | float:
    return np.arctan2(np.sin(angle), np.cos(angle))


def planar_fk(q: np.ndarray, link_lengths: np.ndarray) -> np.ndarray:
    """Return root and every successive joint/end point, shape [DoF+1,2]."""
    absolute_angles = np.cumsum(q)
    link_vectors = np.column_stack(
        (link_lengths * np.cos(absolute_angles), link_lengths * np.sin(absolute_angles))
    )
    return np.vstack((np.zeros(2), np.cumsum(link_vectors, axis=0)))


def make_human_motion(timestamp: np.ndarray) -> np.ndarray:
    """Create a smooth two-joint human arm motion."""
    duration = timestamp[-1]
    phase = 2.0 * np.pi * timestamp / duration
    shoulder = np.deg2rad(30.0 + 25.0 * np.sin(phase))
    elbow = np.deg2rad(55.0 + 20.0 * np.sin(phase + 0.7))
    return np.column_stack((shoulder, elbow))


def extract_scaled_task(
    human_q: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Map human root-relative geometry to the robot scale."""
    scale = np.sum(ROBOT_LINK_LENGTHS_M[:2]) / np.sum(HUMAN_LINK_LENGTHS_M)
    human_points = np.stack(
        [planar_fk(q, HUMAN_LINK_LENGTHS_M) for q in human_q]
    )
    scaled_human_points = scale * human_points
    target_wrist_position = scaled_human_points[:, -1]
    target_wrist_orientation = np.sum(human_q, axis=1)
    return (
        target_wrist_position,
        target_wrist_orientation,
        scaled_human_points,
        scale,
    )


def joint_copy_zero_pad(human_q: np.ndarray) -> np.ndarray:
    """An intentionally naive correspondence: copy two angles and invent q3=0."""
    return np.column_stack((human_q, np.zeros(len(human_q))))


def solve_task_space_trajectory(
    target_position: np.ndarray,
    target_orientation: np.ndarray,
    initial_q: np.ndarray,
) -> np.ndarray:
    """Solve each frame with FK residuals and the previous solution as a warm start."""
    result = np.empty_like(initial_q)
    previous = np.clip(initial_q[0], ROBOT_LOWER_RAD, ROBOT_UPPER_RAD)

    for frame in range(len(target_position)):
        rest = initial_q[frame]

        def residual(q: np.ndarray) -> np.ndarray:
            points = planar_fk(q, ROBOT_LINK_LENGTHS_M)
            position_residual = (points[-1] - target_position[frame]) / 0.005
            orientation_residual = np.array(
                [wrap_angle(np.sum(q) - target_orientation[frame]) / 0.05]
            )
            posture_regularization = 0.02 * (q - rest)
            return np.concatenate(
                (position_residual, orientation_residual, posture_regularization)
            )

        solution = least_squares(
            residual,
            previous,
            bounds=(ROBOT_LOWER_RAD, ROBOT_UPPER_RAD),
            max_nfev=200,
        )
        result[frame] = solution.x
        previous = solution.x
    return result


def evaluate(
    robot_q: np.ndarray,
    target_position: np.ndarray,
    target_orientation: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    robot_points = np.stack(
        [planar_fk(q, ROBOT_LINK_LENGTHS_M) for q in robot_q]
    )
    position_error = np.linalg.norm(robot_points[:, -1] - target_position, axis=1)
    orientation_error = np.abs(
        wrap_angle(np.sum(robot_q, axis=1) - target_orientation)
    )
    return robot_points, position_error, orientation_error


def run_retargeting_experiment() -> tuple[dict[str, np.ndarray], dict[str, object]]:
    timestamp = np.arange(121, dtype=np.float64) / 30.0
    human_q = make_human_motion(timestamp)
    target_position, target_orientation, scaled_human_points, scale = (
        extract_scaled_task(human_q)
    )

    copied_q = joint_copy_zero_pad(human_q)
    optimized_q = solve_task_space_trajectory(
        target_position, target_orientation, copied_q
    )
    copied_points, copied_pos_error, copied_ori_error = evaluate(
        copied_q, target_position, target_orientation
    )
    optimized_points, optimized_pos_error, optimized_ori_error = evaluate(
        optimized_q, target_position, target_orientation
    )

    copied_step = np.linalg.norm(np.diff(copied_q, axis=0), axis=1)
    optimized_step = np.linalg.norm(np.diff(optimized_q, axis=0), axis=1)
    metrics: dict[str, object] = {
        "frame_count": len(timestamp),
        "human_dof": human_q.shape[1],
        "robot_dof": optimized_q.shape[1],
        "human_to_robot_task_scale": float(scale),
        "joint_copy_policy": "copy q1/q2 by index and arbitrarily set robot q3=0",
        "joint_copy_mean_position_error_m": float(np.mean(copied_pos_error)),
        "joint_copy_max_position_error_m": float(np.max(copied_pos_error)),
        "joint_copy_max_orientation_error_rad": float(np.max(copied_ori_error)),
        "task_retarget_mean_position_error_m": float(np.mean(optimized_pos_error)),
        "task_retarget_max_position_error_m": float(np.max(optimized_pos_error)),
        "task_retarget_max_orientation_error_rad": float(np.max(optimized_ori_error)),
        "joint_copy_mean_adjacent_q_change_rad": float(np.mean(copied_step)),
        "task_retarget_mean_adjacent_q_change_rad": float(np.mean(optimized_step)),
        "task_retarget_min_limit_margin_rad": float(
            np.min(
                np.minimum(
                    optimized_q - ROBOT_LOWER_RAD,
                    ROBOT_UPPER_RAD - optimized_q,
                )
            )
        ),
    }
    arrays = {
        "timestamp": timestamp,
        "human_q": human_q,
        "scaled_human_points": scaled_human_points,
        "target_wrist_position": target_position,
        "target_wrist_orientation": target_orientation,
        "joint_copy_robot_q": copied_q,
        "task_retarget_robot_q": optimized_q,
        "joint_copy_robot_points": copied_points,
        "task_retarget_robot_points": optimized_points,
        "joint_copy_position_error": copied_pos_error,
        "task_retarget_position_error": optimized_pos_error,
        "joint_copy_orientation_error": copied_ori_error,
        "task_retarget_orientation_error": optimized_ori_error,
    }
    return arrays, metrics


def save_outputs(
    phase_root: Path, arrays: dict[str, np.ndarray], metrics: dict[str, object]
) -> None:
    data_dir = phase_root / "data"
    output_dir = phase_root / "outputs"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    data_path = data_dir / "p3a_retargeting_baselines.npz"
    report_path = output_dir / "p3a_retargeting_baselines.json"
    figure_path = output_dir / "p3a_retargeting_baselines.png"
    np.savez_compressed(data_path, **arrays)
    report_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    figure, axes = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
    snapshot = 42
    for points, label, style in (
        (arrays["scaled_human_points"][snapshot], "scaled human (2 links)", "o-"),
        (arrays["joint_copy_robot_points"][snapshot], "joint copy (3 links)", "s--"),
        (arrays["task_retarget_robot_points"][snapshot], "task retarget (3 links)", "^-"),
    ):
        axes[0, 0].plot(points[:, 0], points[:, 1], style, label=label)
    axes[0, 0].set_aspect("equal")
    axes[0, 0].set_title(f"Different morphology at frame {snapshot}")
    axes[0, 0].set_xlabel("root-relative x [m]")
    axes[0, 0].set_ylabel("root-relative y [m]")
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(alpha=0.25)

    axes[0, 1].plot(
        *arrays["target_wrist_position"].T, label="target wrist path", linewidth=3
    )
    axes[0, 1].plot(
        *arrays["joint_copy_robot_points"][:, -1].T,
        label="joint-copy wrist path",
    )
    axes[0, 1].plot(
        *arrays["task_retarget_robot_points"][:, -1].T,
        label="task-retarget wrist path",
    )
    axes[0, 1].set_aspect("equal")
    axes[0, 1].set_title("What each baseline preserves")
    axes[0, 1].set_xlabel("root-relative x [m]")
    axes[0, 1].set_ylabel("root-relative y [m]")
    axes[0, 1].legend(fontsize=8)
    axes[0, 1].grid(alpha=0.25)

    time_s = arrays["timestamp"]
    axes[1, 0].plot(
        time_s,
        1000.0 * arrays["joint_copy_position_error"],
        label="joint copy",
    )
    axes[1, 0].plot(
        time_s,
        1000.0 * arrays["task_retarget_position_error"],
        label="task retarget",
    )
    axes[1, 0].set_title("Wrist task error after robot FK")
    axes[1, 0].set_xlabel("time [s]")
    axes[1, 0].set_ylabel("position error [mm]")
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.25)

    for joint in range(arrays["task_retarget_robot_q"].shape[1]):
        axes[1, 1].plot(
            time_s,
            arrays["task_retarget_robot_q"][:, joint],
            label=f"robot q{joint + 1}",
        )
    axes[1, 1].set_title("One valid robot joint trajectory")
    axes[1, 1].set_xlabel("time [s]")
    axes[1, 1].set_ylabel("joint angle [rad]")
    axes[1, 1].legend()
    axes[1, 1].grid(alpha=0.25)
    figure.savefig(figure_path, dpi=160)
    plt.close(figure)

    print(f"\nSaved data   to: {data_path}")
    print(f"Saved report to: {report_path}")
    print(f"Saved figure to: {figure_path}")


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    arrays, metrics = run_retargeting_experiment()

    print("Phase 3 P3-1 - joint copying versus task-space retargeting")
    print(
        f"human / robot DoF                   = "
        f"{metrics['human_dof']} / {metrics['robot_dof']}"
    )
    print(f"human q shape                       = {arrays['human_q'].shape}")
    print(
        f"robot q shape                       = "
        f"{arrays['task_retarget_robot_q'].shape}"
    )
    print(
        f"human-to-robot task scale           = "
        f"{metrics['human_to_robot_task_scale']:.6f}"
    )
    print("\nNaive joint-copy baseline")
    print(f"policy                                = {metrics['joint_copy_policy']}")
    print(
        f"mean wrist position error            = "
        f"{1000.0 * metrics['joint_copy_mean_position_error_m']:.3f} mm"
    )
    print(
        f"max wrist position error             = "
        f"{1000.0 * metrics['joint_copy_max_position_error_m']:.3f} mm"
    )
    print(
        f"max wrist orientation error          = "
        f"{np.rad2deg(metrics['joint_copy_max_orientation_error_rad']):.6f} deg"
    )
    print("\nTask-space geometric retargeting")
    print(
        f"mean wrist position error            = "
        f"{1000.0 * metrics['task_retarget_mean_position_error_m']:.3f} mm"
    )
    print(
        f"max wrist position error             = "
        f"{1000.0 * metrics['task_retarget_max_position_error_m']:.3f} mm"
    )
    print(
        f"max wrist orientation error          = "
        f"{np.rad2deg(metrics['task_retarget_max_orientation_error_rad']):.6f} deg"
    )
    print(
        f"minimum joint-limit margin           = "
        f"{metrics['task_retarget_min_limit_margin_rad']:.6f} rad"
    )
    print("\nThe task-space result preserves the selected wrist task.")
    print("It does not automatically preserve the human elbow or full-arm shape.")
    save_outputs(phase_root, arrays, metrics)


if __name__ == "__main__":
    main()

