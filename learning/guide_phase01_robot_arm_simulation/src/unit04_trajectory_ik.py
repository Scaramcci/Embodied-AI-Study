"""Unit 4: solve and validate a Cartesian wrist trajectory frame by frame."""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"
MPL_CONFIG_DIR = PROJECT_OUTPUT_DIR / ".matplotlib"
MPL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG_DIR))

import matplotlib
import numpy as np
import pybullet as p
import pybullet_data

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


END_EFFECTOR_LINK_INDEX = 6
FRAME_COUNT = 121
POSITION_TOLERANCE_M = 0.005
ORIENTATION_TOLERANCE_RAD = np.deg2rad(2.0)
OUTPUT_DIR = PROJECT_OUTPUT_DIR
CSV_PATH = OUTPUT_DIR / "unit04_trajectory_results.csv"
FIGURE_PATH = OUTPUT_DIR / "unit04_trajectory_summary.png"


@dataclass
class TrajectoryResult:
    strategy: str
    q: np.ndarray
    actual_positions: np.ndarray
    position_errors: np.ndarray
    orientation_errors: np.ndarray
    delta_q_norms: np.ndarray
    success: np.ndarray


def set_configuration(robot_id: int, q: np.ndarray, client_id: int) -> None:
    for joint_index, angle in enumerate(q):
        p.resetJointState(
            robot_id,
            joint_index,
            float(angle),
            physicsClientId=client_id,
        )


def forward_kinematics(
    robot_id: int, q: np.ndarray, client_id: int
) -> tuple[np.ndarray, np.ndarray]:
    set_configuration(robot_id, q, client_id)
    state = p.getLinkState(
        robot_id,
        END_EFFECTOR_LINK_INDEX,
        computeForwardKinematics=True,
        physicsClientId=client_id,
    )
    return np.asarray(state[4]), np.asarray(state[5])


def orientation_error_rad(target: np.ndarray, actual: np.ndarray) -> float:
    target = target / np.linalg.norm(target)
    actual = actual / np.linalg.norm(actual)
    dot = float(np.clip(abs(np.dot(target, actual)), 0.0, 1.0))
    return 2.0 * np.arccos(dot)


def solve_trajectory(
    strategy: str,
    robot_id: int,
    target_positions: np.ndarray,
    target_orientation: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    initial_q: np.ndarray,
    client_id: int,
) -> TrajectoryResult:
    q_frames = []
    actual_positions = []
    position_errors = []
    orientation_errors = []
    success_flags = []
    previous_q = initial_q.copy()
    zero_q = np.zeros_like(initial_q)

    for target_position in target_positions:
        if strategy == "previous_solution":
            rest_pose = previous_q
            set_configuration(robot_id, previous_q, client_id)
        elif strategy == "independent_zero":
            rest_pose = zero_q
            set_configuration(robot_id, zero_q, client_id)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        solution = p.calculateInverseKinematics(
            bodyUniqueId=robot_id,
            endEffectorLinkIndex=END_EFFECTOR_LINK_INDEX,
            targetPosition=target_position.tolist(),
            targetOrientation=target_orientation.tolist(),
            lowerLimits=lower.tolist(),
            upperLimits=upper.tolist(),
            jointRanges=(upper - lower).tolist(),
            restPoses=rest_pose.tolist(),
            jointDamping=[0.1] * len(lower),
            maxNumIterations=500,
            residualThreshold=1e-8,
            physicsClientId=client_id,
        )
        q_candidate = np.asarray(solution[: len(lower)])
        actual_position, actual_orientation = forward_kinematics(
            robot_id, q_candidate, client_id
        )
        position_error = float(np.linalg.norm(actual_position - target_position))
        orientation_error = orientation_error_rad(
            target_orientation, actual_orientation
        )
        limits_valid = bool(np.all(q_candidate >= lower) and np.all(q_candidate <= upper))
        frame_success = (
            position_error < POSITION_TOLERANCE_M
            and orientation_error < ORIENTATION_TOLERANCE_RAD
            and limits_valid
        )

        q_frames.append(q_candidate)
        actual_positions.append(actual_position)
        position_errors.append(position_error)
        orientation_errors.append(orientation_error)
        success_flags.append(frame_success)
        previous_q = q_candidate

    q_array = np.asarray(q_frames)
    delta_q_norms = np.zeros(len(q_array))
    delta_q_norms[1:] = np.linalg.norm(np.diff(q_array, axis=0), axis=1)
    return TrajectoryResult(
        strategy=strategy,
        q=q_array,
        actual_positions=np.asarray(actual_positions),
        position_errors=np.asarray(position_errors),
        orientation_errors=np.asarray(orientation_errors),
        delta_q_norms=delta_q_norms,
        success=np.asarray(success_flags),
    )


def save_csv(target_positions: np.ndarray, results: list[TrajectoryResult]) -> None:
    with CSV_PATH.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(
            [
                "strategy",
                "frame",
                "target_x_m",
                "target_y_m",
                "target_z_m",
                "actual_x_m",
                "actual_y_m",
                "actual_z_m",
                "position_error_m",
                "orientation_error_rad",
                "delta_q_norm_rad",
                "success",
                *[f"q{i}_rad" for i in range(1, 8)],
            ]
        )
        for result in results:
            for frame_index in range(len(target_positions)):
                writer.writerow(
                    [
                        result.strategy,
                        frame_index,
                        *target_positions[frame_index].tolist(),
                        *result.actual_positions[frame_index].tolist(),
                        result.position_errors[frame_index],
                        result.orientation_errors[frame_index],
                        result.delta_q_norms[frame_index],
                        bool(result.success[frame_index]),
                        *result.q[frame_index].tolist(),
                    ]
                )


def save_figure(target_positions: np.ndarray, results: list[TrajectoryResult]) -> None:
    figure, axes = plt.subplots(3, 1, figsize=(10, 11), constrained_layout=True)

    axes[0].plot(
        target_positions[:, 1],
        target_positions[:, 2],
        "k--",
        linewidth=2,
        label="target",
    )
    for result in results:
        axes[0].plot(
            result.actual_positions[:, 1],
            result.actual_positions[:, 2],
            label=result.strategy,
        )
    axes[0].set_title("Wrist path in the world y-z plane")
    axes[0].set_xlabel("y [m]")
    axes[0].set_ylabel("z [m]")
    axes[0].axis("equal")
    axes[0].grid(True)
    axes[0].legend()

    for result in results:
        axes[1].plot(
            result.position_errors * 1000,
            label=f"position: {result.strategy}",
        )
    axes[1].plot(
        [0, len(target_positions) - 1],
        [POSITION_TOLERANCE_M * 1000] * 2,
        color="red",
        linestyle="--",
        label="position threshold",
    )
    axes[1].set_title("FK position validation")
    axes[1].set_xlabel("frame")
    axes[1].set_ylabel("error [mm]")
    axes[1].grid(True)
    axes[1].legend()

    for result in results:
        axes[2].plot(result.delta_q_norms, label=result.strategy)
    axes[2].set_title("Joint-space change between adjacent frames")
    axes[2].set_xlabel("frame")
    axes[2].set_ylabel("||q[t] - q[t-1]|| [rad]")
    axes[2].grid(True)
    axes[2].legend()

    figure.savefig(FIGURE_PATH, dpi=160)
    plt.close(figure)


def main() -> None:
    client_id = p.connect(p.DIRECT)
    if client_id < 0:
        raise RuntimeError("Could not connect to PyBullet")

    try:
        p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=client_id)
        robot_id = p.loadURDF(
            "kuka_iiwa/model.urdf",
            useFixedBase=True,
            physicsClientId=client_id,
        )

        lower = []
        upper = []
        for joint_index in range(p.getNumJoints(robot_id, physicsClientId=client_id)):
            info = p.getJointInfo(robot_id, joint_index, physicsClientId=client_id)
            if info[2] == p.JOINT_REVOLUTE:
                lower.append(float(info[8]))
                upper.append(float(info[9]))
        lower_array = np.asarray(lower)
        upper_array = np.asarray(upper)

        q_center = np.array([0.3, 0.5, -0.2, -0.8, 0.4, 0.6, -0.3])
        center_position, target_orientation = forward_kinematics(
            robot_id, q_center, client_id
        )
        phase = np.linspace(0.0, 2.0 * np.pi, FRAME_COUNT)
        target_positions = np.repeat(center_position[None, :], FRAME_COUNT, axis=0)
        target_positions[:, 1] += 0.03 * np.cos(phase)
        target_positions[:, 2] += 0.03 * np.sin(phase)

        results = [
            solve_trajectory(
                "independent_zero",
                robot_id,
                target_positions,
                target_orientation,
                lower_array,
                upper_array,
                q_center,
                client_id,
            ),
            solve_trajectory(
                "previous_solution",
                robot_id,
                target_positions,
                target_orientation,
                lower_array,
                upper_array,
                q_center,
                client_id,
            ),
        ]

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        save_csv(target_positions, results)
        save_figure(target_positions, results)

        print("\nFrame-wise IK trajectory summary")
        print(f"frames: {FRAME_COUNT}")
        print("target path: 3 cm radius circle in the world y-z plane")
        print("target orientation: fixed\n")
        for result in results:
            failed_frames = np.flatnonzero(~result.success)
            print(result.strategy)
            print(f"  successful frames       = {result.success.sum()}/{FRAME_COUNT}")
            print(
                f"  max position error      = "
                f"{result.position_errors.max() * 1000:.4f} mm"
            )
            print(
                f"  max orientation error   = "
                f"{np.rad2deg(result.orientation_errors.max()):.4f} deg"
            )
            print(
                f"  mean adjacent q change  = "
                f"{result.delta_q_norms[1:].mean():.6f} rad"
            )
            print(
                f"  max adjacent q change   = "
                f"{result.delta_q_norms[1:].max():.6f} rad"
            )
            print(f"  failed frame indices    = {failed_frames.tolist()}\n")

        print(f"Saved frame table to: {CSV_PATH}")
        print(f"Saved summary figure to: {FIGURE_PATH}")
    finally:
        p.disconnect(client_id)


if __name__ == "__main__":
    main()
