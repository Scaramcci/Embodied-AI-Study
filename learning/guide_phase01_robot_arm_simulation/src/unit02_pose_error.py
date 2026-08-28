"""Unit 2 final: compute position and orientation errors for FK validation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pybullet as p
import pybullet_data


END_EFFECTOR_LINK_INDEX = 6
POSITION_TOLERANCE_M = 0.01
ORIENTATION_TOLERANCE_RAD = np.deg2rad(2.0)
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "outputs" / "unit02_pose_error.json"


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


def orientation_error_rad(target_quat: np.ndarray, actual_quat: np.ndarray) -> float:
    """Return the shortest rotation angle between two xyzw unit quaternions."""
    target_quat = target_quat / np.linalg.norm(target_quat)
    actual_quat = actual_quat / np.linalg.norm(actual_quat)
    dot = float(np.clip(abs(np.dot(target_quat, actual_quat)), 0.0, 1.0))
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

        # The target is reachable because it is generated from a known q_target.
        q_target = np.array([0.3, 0.5, -0.2, -0.8, 0.4, 0.6, -0.3])
        # Simulate an imperfect IK/control result with small joint-angle errors.
        q_actual = q_target + np.array([0.01, -0.008, 0.006, 0.01, 0.0, -0.006, 0.004])

        target_position, target_quat = forward_kinematics(
            robot_id, q_target, client_id
        )
        actual_position, actual_quat = forward_kinematics(
            robot_id, q_actual, client_id
        )

        position_error_vector = actual_position - target_position
        position_error_m = float(np.linalg.norm(position_error_vector))
        orientation_error = orientation_error_rad(target_quat, actual_quat)

        position_pass = position_error_m < POSITION_TOLERANCE_M
        orientation_pass = orientation_error < ORIENTATION_TOLERANCE_RAD
        overall_pass = position_pass and orientation_pass

        # A dimensionless score is possible after normalizing by task tolerances.
        # This score is useful for ranking/optimization, not a physical distance.
        normalized_score = (
            (position_error_m / POSITION_TOLERANCE_M) ** 2
            + (orientation_error / ORIENTATION_TOLERANCE_RAD) ** 2
        )

        print("\nTarget pose")
        print(f"  position [m] = {np.round(target_position, 6)}")
        print(f"  quat xyzw    = {np.round(target_quat, 6)}")
        print("\nActual pose after joint perturbation")
        print(f"  position [m] = {np.round(actual_position, 6)}")
        print(f"  quat xyzw    = {np.round(actual_quat, 6)}")
        print("\nSeparate pose errors")
        print(f"  position error vector [m] = {np.round(position_error_vector, 6)}")
        print(f"  position error norm [m]   = {position_error_m:.6f}")
        print(f"  orientation error [rad]   = {orientation_error:.6f}")
        print(f"  orientation error [deg]   = {np.rad2deg(orientation_error):.4f}")
        print("\nThreshold checks")
        print(
            f"  position < {POSITION_TOLERANCE_M:.3f} m: "
            f"{'PASS' if position_pass else 'FAIL'}"
        )
        print(
            f"  orientation < {np.rad2deg(ORIENTATION_TOLERANCE_RAD):.1f} deg: "
            f"{'PASS' if orientation_pass else 'FAIL'}"
        )
        print(f"  overall: {'PASS' if overall_pass else 'FAIL'}")
        print("\nOptional normalized objective")
        print(
            "  score = (position_error / position_tolerance)^2"
            " + (orientation_error / orientation_tolerance)^2"
        )
        print(f"  dimensionless score = {normalized_score:.6f}")

        result = {
            "position_error_vector_m": position_error_vector.tolist(),
            "position_error_norm_m": position_error_m,
            "orientation_error_rad": orientation_error,
            "orientation_error_deg": float(np.rad2deg(orientation_error)),
            "position_tolerance_m": POSITION_TOLERANCE_M,
            "orientation_tolerance_deg": float(
                np.rad2deg(ORIENTATION_TOLERANCE_RAD)
            ),
            "position_pass": bool(position_pass),
            "orientation_pass": bool(orientation_pass),
            "overall_pass": bool(overall_pass),
            "normalized_score": float(normalized_score),
        }
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"\nSaved result to: {OUTPUT_PATH}")
    finally:
        p.disconnect(client_id)


if __name__ == "__main__":
    main()

