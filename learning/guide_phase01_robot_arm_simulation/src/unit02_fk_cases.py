"""Unit 2: map joint configurations q to end-effector poses with FK."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pybullet as p
import pybullet_data


END_EFFECTOR_LINK_INDEX = 6
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "outputs" / "unit02_fk_poses.csv"

CONFIGURATIONS = {
    "zero": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    "shoulder_turn": np.array([0.5, -0.4, 0.0, 0.0, 0.0, 0.0, 0.0]),
    "bent_arm": np.array([0.3, 0.5, -0.2, -0.8, 0.4, 0.6, -0.3]),
}


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


def quaternion_distance(q1: np.ndarray, q2: np.ndarray) -> float:
    """Shortest orientation difference in radians for xyzw quaternions."""
    dot = float(np.clip(abs(np.dot(q1, q2)), 0.0, 1.0))
    return 2.0 * np.arccos(dot)


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

        rows: list[list[object]] = []
        print("\nFK mapping: joint space q -> task-space wrist pose")
        print("PyBullet quaternion convention: [x, y, z, w]\n")
        for name, q in CONFIGURATIONS.items():
            position, quaternion = forward_kinematics(robot_id, q, client_id)
            euler = np.asarray(p.getEulerFromQuaternion(quaternion))
            print(f"{name}")
            print(f"  q [rad]       = {np.round(q, 4)}")
            print(f"  position [m]  = {np.round(position, 4)}")
            print(f"  quat xyzw     = {np.round(quaternion, 4)}")
            print(f"  Euler rpy     = {np.round(euler, 4)}")
            rows.append(
                [
                    name,
                    *q.tolist(),
                    *position.tolist(),
                    *quaternion.tolist(),
                ]
            )

        # Convention error 1: treating a degree value as if it were radians.
        correct_q = np.zeros(7)
        correct_q[0] = np.deg2rad(30.0)
        wrong_q = np.zeros(7)
        wrong_q[0] = 30.0
        _, correct_degree_quat = forward_kinematics(robot_id, correct_q, client_id)
        _, wrong_degree_quat = forward_kinematics(robot_id, wrong_q, client_id)
        degree_error = quaternion_distance(correct_degree_quat, wrong_degree_quat)

        # Convention error 2: passing wxyz data to an API that expects xyzw.
        _, correct_quat = forward_kinematics(
            robot_id, CONFIGURATIONS["bent_arm"], client_id
        )
        wrong_order_quat = correct_quat[[3, 0, 1, 2]]
        order_error = quaternion_distance(correct_quat, wrong_order_quat)

        print("\nConvention error demonstrations")
        print(
            "  Intended 30 degrees, but passed 30 radians: "
            f"orientation error = {degree_error:.4f} rad"
        )
        print(
            "  Passed wxyz data to PyBullet's xyzw API: "
            f"orientation error = {order_error:.4f} rad"
        )

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as output_file:
            writer = csv.writer(output_file)
            writer.writerow(
                [
                    "name",
                    "q1_rad",
                    "q2_rad",
                    "q3_rad",
                    "q4_rad",
                    "q5_rad",
                    "q6_rad",
                    "q7_rad",
                    "px_m",
                    "py_m",
                    "pz_m",
                    "qx",
                    "qy",
                    "qz",
                    "qw",
                ]
            )
            writer.writerows(rows)
        print(f"\nSaved FK table to: {OUTPUT_PATH}")
    finally:
        p.disconnect(client_id)


if __name__ == "__main__":
    main()

