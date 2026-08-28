"""Unit 2: visualize frames and inspect the end-effector pose."""

from __future__ import annotations

import argparse
import time

import numpy as np
import pybullet as p
import pybullet_data


END_EFFECTOR_LINK_INDEX = 6
AXIS_LENGTH = 0.18


def homogeneous_transform(
    position: tuple[float, float, float],
    quaternion: tuple[float, float, float, float],
) -> np.ndarray:
    """Build world_T_link from position and an (x, y, z, w) quaternion."""
    rotation = np.asarray(p.getMatrixFromQuaternion(quaternion)).reshape(3, 3)
    transform = np.eye(4)
    transform[:3, :3] = rotation
    transform[:3, 3] = position
    return transform


def end_effector_pose(
    robot_id: int, client_id: int
) -> tuple[
    tuple[float, float, float], tuple[float, float, float, float]
]:
    """Return the URDF link-frame pose, rather than its inertial COM pose."""
    state = p.getLinkState(
        robot_id,
        END_EFFECTOR_LINK_INDEX,
        computeForwardKinematics=True,
        physicsClientId=client_id,
    )
    return state[4], state[5]


def print_pose(robot_id: int, client_id: int) -> None:
    position, quaternion = end_effector_pose(robot_id, client_id)
    euler = p.getEulerFromQuaternion(quaternion)
    transform = homogeneous_transform(position, quaternion)

    np.set_printoptions(precision=4, suppress=True)
    print("\n--- link_7 pose expressed in the world frame ---")
    print(f"position [m]      = {np.asarray(position).round(4)}")
    print(f"quaternion xyzw  = {np.asarray(quaternion).round(4)}")
    print(f"Euler rpy [rad]  = {np.asarray(euler).round(4)}")
    print("world_T_link7 =")
    print(transform)


def draw_axes(
    client_id: int,
    parent_object_id: int = -1,
    parent_link_index: int = -1,
    origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> None:
    """Draw RGB axes: x red, y green, z blue."""
    axes = (
        ((AXIS_LENGTH, 0.0, 0.0), (1.0, 0.0, 0.0)),
        ((0.0, AXIS_LENGTH, 0.0), (0.0, 1.0, 0.0)),
        ((0.0, 0.0, AXIS_LENGTH), (0.0, 0.0, 1.0)),
    )
    for endpoint, color in axes:
        p.addUserDebugLine(
            origin,
            endpoint,
            color,
            lineWidth=4,
            lifeTime=0,
            parentObjectUniqueId=parent_object_id,
            parentLinkIndex=parent_link_index,
            physicsClientId=client_id,
        )


def load_scene(connection_mode: int) -> tuple[int, int]:
    client_id = p.connect(connection_mode)
    if client_id < 0:
        raise RuntimeError("Could not connect to PyBullet")
    p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=client_id)
    p.loadURDF("plane.urdf", physicsClientId=client_id)
    robot_id = p.loadURDF(
        "kuka_iiwa/model.urdf",
        useFixedBase=True,
        physicsClientId=client_id,
    )
    return client_id, robot_id


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--direct-check", action="store_true")
    args = parser.parse_args()

    client_id, robot_id = load_scene(p.DIRECT if args.direct_check else p.GUI)
    try:
        if args.direct_check:
            print_pose(robot_id, client_id)
            transform = homogeneous_transform(*end_effector_pose(robot_id, client_id))
            if not np.allclose(transform[3], [0.0, 0.0, 0.0, 1.0]):
                raise RuntimeError("Invalid homogeneous-transform bottom row")
            print("DIRECT_CHECK=PASS")
            return

        p.resetDebugVisualizerCamera(
            cameraDistance=1.8,
            cameraYaw=45,
            cameraPitch=-25,
            cameraTargetPosition=[0, 0, 0.6],
            physicsClientId=client_id,
        )

        # World-frame axes are fixed at the world origin.
        draw_axes(client_id)
        # These axes are defined locally and therefore follow link 7.
        draw_axes(
            client_id,
            parent_object_id=robot_id,
            parent_link_index=END_EFFECTOR_LINK_INDEX,
        )

        sliders: list[tuple[int, int]] = []
        for joint_index in range(p.getNumJoints(robot_id, physicsClientId=client_id)):
            info = p.getJointInfo(robot_id, joint_index, physicsClientId=client_id)
            if info[2] != p.JOINT_REVOLUTE:
                continue
            slider_id = p.addUserDebugParameter(
                f"joint_{joint_index + 1}",
                float(info[8]),
                float(info[9]),
                0.0,
                physicsClientId=client_id,
            )
            sliders.append((joint_index, slider_id))

        print("RGB convention: x=red, y=green, z=blue")
        print("The axes at the origin are the world frame; the upper axes follow link_7.")
        print("A new pose is printed whenever a slider target changes noticeably.")
        print_pose(robot_id, client_id)
        previous_targets = np.zeros(len(sliders))

        while p.isConnected(client_id):
            targets = np.array(
                [
                    p.readUserDebugParameter(slider_id, physicsClientId=client_id)
                    for _, slider_id in sliders
                ]
            )
            for (joint_index, _), target in zip(sliders, targets):
                p.resetJointState(
                    robot_id,
                    joint_index,
                    float(target),
                    physicsClientId=client_id,
                )

            if np.max(np.abs(targets - previous_targets)) > 0.02:
                print_pose(robot_id, client_id)
                previous_targets = targets.copy()

            p.stepSimulation(physicsClientId=client_id)
            time.sleep(1.0 / 120.0)
    except KeyboardInterrupt:
        print("\nUnit 2 frame experiment stopped.")
    finally:
        if p.isConnected(client_id):
            p.disconnect(client_id)


if __name__ == "__main__":
    main()

