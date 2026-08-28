"""Unit 1: inspect the KUKA iiwa kinematic chain with GUI sliders."""

from __future__ import annotations

import argparse
import time

import pybullet as p
import pybullet_data


JOINT_TYPE_NAMES = {
    p.JOINT_REVOLUTE: "revolute",
    p.JOINT_PRISMATIC: "prismatic",
    p.JOINT_SPHERICAL: "spherical",
    p.JOINT_PLANAR: "planar",
    p.JOINT_FIXED: "fixed",
}


def text(value: bytes) -> str:
    """Decode PyBullet's byte-string names."""
    return value.decode("utf-8")


def print_joint_table(robot_id: int, client_id: int) -> list[dict[str, object]]:
    """Print all joints and return the controllable-joint metadata."""
    movable_joints: list[dict[str, object]] = []
    joint_count = p.getNumJoints(robot_id, physicsClientId=client_id)

    print("\nKUKA LBR iiwa joint table")
    print("-" * 105)
    print(
        f"{'idx':>3}  {'joint name':<20} {'type':<10} "
        f"{'child link':<22} {'limits (rad)':<25} {'parent':>6}"
    )
    print("-" * 105)

    for joint_index in range(joint_count):
        info = p.getJointInfo(robot_id, joint_index, physicsClientId=client_id)
        joint_type = info[2]
        lower_limit = float(info[8])
        upper_limit = float(info[9])
        parent_index = int(info[16])
        joint_name = text(info[1])
        child_link = text(info[12])

        print(
            f"{joint_index:>3}  {joint_name:<20} "
            f"{JOINT_TYPE_NAMES.get(joint_type, str(joint_type)):<10} "
            f"{child_link:<22} "
            f"[{lower_limit:>7.3f}, {upper_limit:>7.3f}]   "
            f"{parent_index:>6}"
        )

        if joint_type in (p.JOINT_REVOLUTE, p.JOINT_PRISMATIC):
            movable_joints.append(
                {
                    "index": joint_index,
                    "name": joint_name,
                    "child_link": child_link,
                    "lower": lower_limit,
                    "upper": upper_limit,
                }
            )

    print("-" * 105)
    return movable_joints


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--direct-check",
        action="store_true",
        help="load and inspect the robot without opening a GUI, then exit",
    )
    args = parser.parse_args()

    connection_mode = p.DIRECT if args.direct_check else p.GUI
    client_id = p.connect(connection_mode)
    if client_id < 0:
        raise RuntimeError("Could not connect to PyBullet")

    try:
        p.setAdditionalSearchPath(
            pybullet_data.getDataPath(), physicsClientId=client_id
        )
        p.setGravity(0, 0, -9.81, physicsClientId=client_id)
        p.loadURDF("plane.urdf", physicsClientId=client_id)
        robot_id = p.loadURDF(
            "kuka_iiwa/model.urdf",
            useFixedBase=True,
            physicsClientId=client_id,
        )

        movable_joints = print_joint_table(robot_id, client_id)
        if len(movable_joints) != 7:
            raise RuntimeError(
                f"Expected 7 movable joints, found {len(movable_joints)}"
            )

        end_effector = movable_joints[-1]
        print(
            "\nEnd effector used in this stage: "
            f"{end_effector['child_link']} (link index {end_effector['index']})"
        )

        if args.direct_check:
            print("DIRECT_CHECK=PASS")
            return

        p.resetDebugVisualizerCamera(
            cameraDistance=1.8,
            cameraYaw=45,
            cameraPitch=-25,
            cameraTargetPosition=[0, 0, 0.6],
            physicsClientId=client_id,
        )

        sliders: list[tuple[int, int]] = []
        for joint in movable_joints:
            joint_index = int(joint["index"])
            slider_id = p.addUserDebugParameter(
                f"{joint['name']} (index {joint_index})",
                float(joint["lower"]),
                float(joint["upper"]),
                0.0,
                physicsClientId=client_id,
            )
            sliders.append((joint_index, slider_id))

        print("\nGUI sliders are ready.")
        print("Move joint_1, joint_4, and joint_7 one at a time; reset each to 0.")
        print("Close the GUI window or press Ctrl+C in this terminal to exit.\n")

        while p.isConnected(client_id):
            for joint_index, slider_id in sliders:
                target = p.readUserDebugParameter(
                    slider_id, physicsClientId=client_id
                )
                p.setJointMotorControl2(
                    robot_id,
                    joint_index,
                    p.POSITION_CONTROL,
                    targetPosition=target,
                    force=500,
                    physicsClientId=client_id,
                )
            p.stepSimulation(physicsClientId=client_id)
            time.sleep(1.0 / 240.0)
    except KeyboardInterrupt:
        print("\nUnit 1 slider experiment stopped.")
    finally:
        if p.isConnected(client_id):
            p.disconnect(client_id)


if __name__ == "__main__":
    main()

