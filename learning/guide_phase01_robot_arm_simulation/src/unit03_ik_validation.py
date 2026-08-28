"""Unit 3: solve IK and validate every candidate with FK and joint limits."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pybullet as p
import pybullet_data


END_EFFECTOR_LINK_INDEX = 6
POSITION_TOLERANCE_M = 0.005
ORIENTATION_TOLERANCE_RAD = np.deg2rad(2.0)
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "outputs" / "unit03_ik_results.csv"


@dataclass
class ValidationResult:
    name: str
    position_constrained: bool
    orientation_constrained: bool
    position_error_m: float
    orientation_error_rad: float
    max_limit_violation_rad: float
    position_pass: bool
    orientation_pass: bool
    limits_pass: bool
    overall_pass: bool
    q_candidate: np.ndarray


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


def get_joint_limits(robot_id: int, client_id: int) -> tuple[np.ndarray, np.ndarray]:
    lower = []
    upper = []
    for joint_index in range(p.getNumJoints(robot_id, physicsClientId=client_id)):
        info = p.getJointInfo(robot_id, joint_index, physicsClientId=client_id)
        if info[2] == p.JOINT_REVOLUTE:
            lower.append(float(info[8]))
            upper.append(float(info[9]))
    return np.asarray(lower), np.asarray(upper)


def solve_ik(
    robot_id: int,
    target_position: np.ndarray,
    target_orientation: np.ndarray | None,
    lower: np.ndarray,
    upper: np.ndarray,
    client_id: int,
) -> np.ndarray:
    common_arguments = {
        "bodyUniqueId": robot_id,
        "endEffectorLinkIndex": END_EFFECTOR_LINK_INDEX,
        "targetPosition": target_position.tolist(),
        "lowerLimits": lower.tolist(),
        "upperLimits": upper.tolist(),
        "jointRanges": (upper - lower).tolist(),
        "restPoses": np.zeros_like(lower).tolist(),
        "jointDamping": [0.1] * len(lower),
        "maxNumIterations": 500,
        "residualThreshold": 1e-8,
        "physicsClientId": client_id,
    }
    if target_orientation is not None:
        common_arguments["targetOrientation"] = target_orientation.tolist()
    solution = p.calculateInverseKinematics(**common_arguments)
    return np.asarray(solution[: len(lower)])


def validate(
    name: str,
    robot_id: int,
    target_position: np.ndarray,
    target_orientation: np.ndarray,
    constrain_orientation: bool,
    lower: np.ndarray,
    upper: np.ndarray,
    client_id: int,
) -> ValidationResult:
    q_candidate = solve_ik(
        robot_id,
        target_position,
        target_orientation if constrain_orientation else None,
        lower,
        upper,
        client_id,
    )
    actual_position, actual_orientation = forward_kinematics(
        robot_id, q_candidate, client_id
    )

    position_error = float(np.linalg.norm(actual_position - target_position))
    orientation_error = orientation_error_rad(target_orientation, actual_orientation)
    lower_violation = np.maximum(lower - q_candidate, 0.0)
    upper_violation = np.maximum(q_candidate - upper, 0.0)
    max_limit_violation = float(max(lower_violation.max(), upper_violation.max()))

    position_pass = position_error < POSITION_TOLERANCE_M
    # Orientation is reported in every case, but required only when constrained.
    orientation_pass = (
        orientation_error < ORIENTATION_TOLERANCE_RAD
        if constrain_orientation
        else True
    )
    limits_pass = max_limit_violation < 1e-9
    overall_pass = position_pass and orientation_pass and limits_pass

    return ValidationResult(
        name=name,
        position_constrained=True,
        orientation_constrained=constrain_orientation,
        position_error_m=position_error,
        orientation_error_rad=orientation_error,
        max_limit_violation_rad=max_limit_violation,
        position_pass=position_pass,
        orientation_pass=orientation_pass,
        limits_pass=limits_pass,
        overall_pass=overall_pass,
        q_candidate=q_candidate,
    )


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
        lower, upper = get_joint_limits(robot_id, client_id)

        # Generate a known-reachable target from a valid reference configuration.
        q_reference = np.array([0.3, 0.5, -0.2, -0.8, 0.4, 0.6, -0.3])
        target_position, target_orientation = forward_kinematics(
            robot_id, q_reference, client_id
        )

        results = [
            validate(
                "reachable_position_only",
                robot_id,
                target_position,
                target_orientation,
                False,
                lower,
                upper,
                client_id,
            ),
            validate(
                "reachable_full_pose",
                robot_id,
                target_position,
                target_orientation,
                True,
                lower,
                upper,
                client_id,
            ),
            validate(
                "unreachable_full_pose",
                robot_id,
                np.array([2.0, 0.0, 2.0]),
                target_orientation,
                True,
                lower,
                upper,
                client_id,
            ),
        ]

        print("\nIK candidates validated by FK")
        print(
            f"Thresholds: position < {POSITION_TOLERANCE_M * 1000:.1f} mm, "
            f"orientation < {np.rad2deg(ORIENTATION_TOLERANCE_RAD):.1f} deg\n"
        )
        for result in results:
            print(result.name)
            print(f"  orientation constrained = {result.orientation_constrained}")
            print(f"  q_candidate [rad]        = {np.round(result.q_candidate, 4)}")
            print(
                f"  position error           = "
                f"{result.position_error_m * 1000:.4f} mm"
            )
            print(
                f"  orientation error        = "
                f"{np.rad2deg(result.orientation_error_rad):.4f} deg"
            )
            print(
                f"  max joint-limit violation = "
                f"{result.max_limit_violation_rad:.6f} rad"
            )
            print(f"  verdict                  = {'PASS' if result.overall_pass else 'FAIL'}\n")

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as output_file:
            writer = csv.writer(output_file)
            writer.writerow(
                [
                    "name",
                    "orientation_constrained",
                    "position_error_m",
                    "orientation_error_rad",
                    "max_limit_violation_rad",
                    "position_pass",
                    "orientation_pass",
                    "limits_pass",
                    "overall_pass",
                    *[f"q{i}_rad" for i in range(1, 8)],
                ]
            )
            for result in results:
                writer.writerow(
                    [
                        result.name,
                        result.orientation_constrained,
                        result.position_error_m,
                        result.orientation_error_rad,
                        result.max_limit_violation_rad,
                        result.position_pass,
                        result.orientation_pass,
                        result.limits_pass,
                        result.overall_pass,
                        *result.q_candidate.tolist(),
                    ]
                )
        print(f"Saved result table to: {OUTPUT_PATH}")
    finally:
        p.disconnect(client_id)


if __name__ == "__main__":
    main()

