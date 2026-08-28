"""Unit 3: compare redundant IK solutions and their joint-limit margins."""

from __future__ import annotations

import numpy as np
import pybullet as p
import pybullet_data


END_EFFECTOR_LINK_INDEX = 6


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
    dot = float(np.clip(abs(np.dot(target, actual)), 0.0, 1.0))
    return 2.0 * np.arccos(dot)


def solve_with_rest_pose(
    robot_id: int,
    target_position: np.ndarray,
    target_orientation: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    rest_pose: np.ndarray,
    client_id: int,
) -> np.ndarray:
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
        maxNumIterations=1000,
        residualThreshold=1e-10,
        physicsClientId=client_id,
    )
    return np.asarray(solution[: len(lower)])


def joint_limit_margin(q: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> float:
    """Smallest angular distance from any joint to either limit."""
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

        q_reference = np.array([0.3, 0.5, -0.2, -0.8, 0.4, 0.6, -0.3])
        target_position, target_orientation = forward_kinematics(
            robot_id, q_reference, client_id
        )

        rest_poses = {
            "zero_rest": np.zeros(7),
            "reference_rest": q_reference,
            "alternate_rest": np.array([-0.8, 0.4, 0.8, -0.9, -0.6, 0.5, 0.7]),
        }

        print("\nSame target pose, different null-space preferences")
        print("restPoses is a preference, not a hard target or an initial state.\n")
        solutions: dict[str, np.ndarray] = {}
        for name, rest_pose in rest_poses.items():
            q_solution = solve_with_rest_pose(
                robot_id,
                target_position,
                target_orientation,
                lower_array,
                upper_array,
                rest_pose,
                client_id,
            )
            actual_position, actual_orientation = forward_kinematics(
                robot_id, q_solution, client_id
            )
            position_error_mm = np.linalg.norm(actual_position - target_position) * 1000
            orientation_error_deg = np.rad2deg(
                orientation_error_rad(target_orientation, actual_orientation)
            )
            margin = joint_limit_margin(q_solution, lower_array, upper_array)
            solutions[name] = q_solution

            print(name)
            print(f"  rest pose [rad]          = {np.round(rest_pose, 3)}")
            print(f"  IK solution [rad]        = {np.round(q_solution, 3)}")
            print(f"  position error           = {position_error_mm:.4f} mm")
            print(f"  orientation error        = {orientation_error_deg:.4f} deg")
            print(f"  minimum limit margin     = {margin:.4f} rad")
            print()

        names = list(solutions)
        print("Joint-space distances between valid solutions")
        for index, first_name in enumerate(names):
            for second_name in names[index + 1 :]:
                distance = np.linalg.norm(
                    solutions[first_name] - solutions[second_name]
                )
                print(f"  {first_name} vs {second_name}: {distance:.4f} rad")

        print("\nInterpretation: similar FK error does not imply similar joint posture.")
    finally:
        p.disconnect(client_id)


if __name__ == "__main__":
    main()

