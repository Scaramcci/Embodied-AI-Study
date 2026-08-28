"""Unit 3 final: sweep targets from reachable to outside the workspace."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pybullet as p
import pybullet_data


END_EFFECTOR_LINK_INDEX = 6
POSITION_TOLERANCE_M = 0.005
OUTPUT_PATH = (
    Path(__file__).resolve().parents[1] / "outputs" / "unit03_workspace_boundary.csv"
)


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


def minimum_limit_margin(
    q: np.ndarray, lower: np.ndarray, upper: np.ndarray
) -> float:
    return float(np.min(np.minimum(q - lower, upper - q)))


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
        zero_pose = np.zeros_like(lower_array)

        # Move the target outward along world +x while keeping y and z fixed.
        x_targets = np.arange(0.4, 1.51, 0.1)
        rows: list[list[object]] = []

        print("\nWorkspace sweep: target = [x, 0, 0.7] m")
        print(f"PASS threshold: position error < {POSITION_TOLERANCE_M * 1000:.1f} mm\n")
        print(
            f"{'target x':>8}  {'actual x':>8}  {'actual z':>8}  "
            f"{'error mm':>10}  {'limit margin':>12}  {'verdict':>7}"
        )
        print("-" * 75)

        for target_x in x_targets:
            target_position = np.array([target_x, 0.0, 0.7])
            # Reset before every independent solve so previous cases do not seed it.
            set_configuration(robot_id, zero_pose, client_id)
            solution = p.calculateInverseKinematics(
                bodyUniqueId=robot_id,
                endEffectorLinkIndex=END_EFFECTOR_LINK_INDEX,
                targetPosition=target_position.tolist(),
                lowerLimits=lower_array.tolist(),
                upperLimits=upper_array.tolist(),
                jointRanges=(upper_array - lower_array).tolist(),
                restPoses=zero_pose.tolist(),
                jointDamping=[0.1] * len(lower_array),
                maxNumIterations=1000,
                residualThreshold=1e-10,
                physicsClientId=client_id,
            )
            q_candidate = np.asarray(solution[: len(lower_array)])
            set_configuration(robot_id, q_candidate, client_id)
            actual_position = end_effector_position(robot_id, client_id)
            error_m = float(np.linalg.norm(actual_position - target_position))
            margin = minimum_limit_margin(q_candidate, lower_array, upper_array)
            limits_pass = margin >= 0.0
            overall_pass = error_m < POSITION_TOLERANCE_M and limits_pass

            print(
                f"{target_x:8.2f}  {actual_position[0]:8.3f}  "
                f"{actual_position[2]:8.3f}  {error_m * 1000:10.3f}  "
                f"{margin:12.3f}  {'PASS' if overall_pass else 'FAIL':>7}"
            )
            rows.append(
                [
                    target_x,
                    0.0,
                    0.7,
                    *actual_position.tolist(),
                    error_m,
                    margin,
                    limits_pass,
                    overall_pass,
                    *q_candidate.tolist(),
                ]
            )

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as output_file:
            writer = csv.writer(output_file)
            writer.writerow(
                [
                    "target_x_m",
                    "target_y_m",
                    "target_z_m",
                    "actual_x_m",
                    "actual_y_m",
                    "actual_z_m",
                    "position_error_m",
                    "minimum_limit_margin_rad",
                    "limits_pass",
                    "overall_pass",
                    *[f"q{i}_rad" for i in range(1, 8)],
                ]
            )
            writer.writerows(rows)
        print(f"\nSaved workspace sweep to: {OUTPUT_PATH}")
    finally:
        p.disconnect(client_id)


if __name__ == "__main__":
    main()

