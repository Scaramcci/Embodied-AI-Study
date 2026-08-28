"""Unit 4: preserve and diagnose failed IK frames in a wrist trajectory."""

from __future__ import annotations

import csv
import os
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
CSV_PATH = PROJECT_OUTPUT_DIR / "unit04_failed_waypoints.csv"
FIGURE_PATH = PROJECT_OUTPUT_DIR / "unit04_failed_waypoints.png"


def set_configuration(robot_id: int, q: np.ndarray, client_id: int) -> None:
    for joint_index, angle in enumerate(q):
        p.resetJointState(
            robot_id,
            joint_index,
            float(angle),
            physicsClientId=client_id,
        )


def end_effector_position(robot_id: int, client_id: int) -> np.ndarray:
    state = p.getLinkState(
        robot_id,
        END_EFFECTOR_LINK_INDEX,
        computeForwardKinematics=True,
        physicsClientId=client_id,
    )
    return np.asarray(state[4])


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

        # The target moves smoothly outward and then returns. The middle section
        # crosses the workspace boundary observed in Unit 3.
        phase = np.linspace(0.0, 1.0, FRAME_COUNT)
        target_x = 0.75 + 0.30 * np.sin(np.pi * phase) ** 2
        target_positions = np.column_stack(
            [target_x, np.zeros(FRAME_COUNT), np.full(FRAME_COUNT, 0.7)]
        )

        q_frames = []
        actual_positions = []
        errors = []
        success = []
        previous_q = np.zeros(7)

        for target_position in target_positions:
            set_configuration(robot_id, previous_q, client_id)
            solution = p.calculateInverseKinematics(
                bodyUniqueId=robot_id,
                endEffectorLinkIndex=END_EFFECTOR_LINK_INDEX,
                targetPosition=target_position.tolist(),
                lowerLimits=lower_array.tolist(),
                upperLimits=upper_array.tolist(),
                jointRanges=(upper_array - lower_array).tolist(),
                restPoses=previous_q.tolist(),
                jointDamping=[0.1] * 7,
                maxNumIterations=1000,
                residualThreshold=1e-10,
                physicsClientId=client_id,
            )
            q_candidate = np.asarray(solution[:7])
            set_configuration(robot_id, q_candidate, client_id)
            actual_position = end_effector_position(robot_id, client_id)
            error_m = float(np.linalg.norm(actual_position - target_position))
            limits_valid = bool(
                np.all(q_candidate >= lower_array) and np.all(q_candidate <= upper_array)
            )
            frame_success = error_m < POSITION_TOLERANCE_M and limits_valid

            q_frames.append(q_candidate)
            actual_positions.append(actual_position)
            errors.append(error_m)
            success.append(frame_success)
            previous_q = q_candidate

        q_array = np.asarray(q_frames)
        actual_array = np.asarray(actual_positions)
        error_array = np.asarray(errors)
        success_array = np.asarray(success)
        delta_q = np.zeros(FRAME_COUNT)
        delta_q[1:] = np.linalg.norm(np.diff(q_array, axis=0), axis=1)
        failed_indices = np.flatnonzero(~success_array)
        successful_indices = np.flatnonzero(success_array)
        retained_frame_gaps = np.diff(successful_indices)
        max_gap_after_drop = int(retained_frame_gaps.max()) if len(retained_frame_gaps) else 0

        PROJECT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with CSV_PATH.open("w", newline="", encoding="utf-8") as output_file:
            writer = csv.writer(output_file)
            writer.writerow(
                [
                    "frame",
                    "target_x_m",
                    "target_y_m",
                    "target_z_m",
                    "actual_x_m",
                    "actual_y_m",
                    "actual_z_m",
                    "position_error_m",
                    "delta_q_norm_rad",
                    "success",
                    *[f"q{i}_rad" for i in range(1, 8)],
                ]
            )
            for frame_index in range(FRAME_COUNT):
                writer.writerow(
                    [
                        frame_index,
                        *target_positions[frame_index].tolist(),
                        *actual_array[frame_index].tolist(),
                        error_array[frame_index],
                        delta_q[frame_index],
                        bool(success_array[frame_index]),
                        *q_array[frame_index].tolist(),
                    ]
                )

        figure, axes = plt.subplots(3, 1, figsize=(10, 11))
        frames = np.arange(FRAME_COUNT)
        axes[0].plot(frames, target_positions[:, 0], "k--", label="target x")
        axes[0].plot(frames, actual_array[:, 0], label="actual x after IK/FK")
        axes[0].scatter(
            failed_indices,
            actual_array[failed_indices, 0],
            color="red",
            s=16,
            label="failed frames",
        )
        axes[0].set_ylabel("world x [m]")
        axes[0].set_title("Target crosses the reachable workspace boundary")
        axes[0].grid(True)
        axes[0].legend()

        axes[1].plot(frames, error_array * 1000, label="position error")
        axes[1].plot(
            [0, FRAME_COUNT - 1],
            [POSITION_TOLERANCE_M * 1000] * 2,
            "r--",
            label="5 mm threshold",
        )
        axes[1].scatter(
            failed_indices,
            error_array[failed_indices] * 1000,
            color="red",
            s=16,
        )
        axes[1].set_ylabel("error [mm]")
        axes[1].set_title("Failed frames are recorded, not deleted")
        axes[1].grid(True)
        axes[1].legend()

        axes[2].plot(frames, delta_q, label="adjacent q change")
        axes[2].scatter(
            failed_indices,
            delta_q[failed_indices],
            color="red",
            s=16,
            label="invalid candidate frames",
        )
        axes[2].set_xlabel("original frame index")
        axes[2].set_ylabel("||q[t] - q[t-1]|| [rad]")
        axes[2].set_title("Candidate joint changes do not make failed frames valid")
        axes[2].grid(True)
        axes[2].legend()

        figure.tight_layout()
        figure.savefig(FIGURE_PATH, dpi=160)
        plt.close(figure)

        print("\nTrajectory with a deliberately unreachable middle section")
        print(f"frames                    = {FRAME_COUNT}")
        print(f"successful frames         = {success_array.sum()}/{FRAME_COUNT}")
        print(f"failed frames             = {len(failed_indices)}")
        print(f"failed frame indices      = {failed_indices.tolist()}")
        print(f"maximum position error    = {error_array.max() * 1000:.3f} mm")
        print(f"maximum adjacent q change = {delta_q[1:].max():.6f} rad")
        print(
            "largest original-frame gap if failed rows are deleted "
            f"= {max_gap_after_drop} frames"
        )
        print("\nDo not execute q_candidate at failed frames as if it were valid IK.")
        print(f"Saved frame table to: {CSV_PATH}")
        print(f"Saved diagnostic figure to: {FIGURE_PATH}")
    finally:
        p.disconnect(client_id)


if __name__ == "__main__":
    main()

