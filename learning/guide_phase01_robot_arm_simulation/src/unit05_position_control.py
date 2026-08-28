"""Unit 5: execute one joint path at normal and fast playback speeds."""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
MPL_CONFIG_DIR = OUTPUT_DIR / ".matplotlib"
MPL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG_DIR))

import matplotlib
import numpy as np
import pybullet as p
import pybullet_data

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


END_EFFECTOR_LINK_INDEX = 6
PHYSICS_TIMESTEP_S = 1.0 / 240.0
INPUT_PATH = OUTPUT_DIR / "unit05_smoothing_metrics.csv"
CSV_PATH = OUTPUT_DIR / "unit05_position_control.csv"
FIGURE_PATH = OUTPUT_DIR / "unit05_position_control.png"


@dataclass
class Rollout:
    name: str
    sample_dt_s: float
    target_q: np.ndarray
    actual_q: np.ndarray
    joint_error_norm: np.ndarray
    actual_speed_norm: np.ndarray
    task_position_error_m: np.ndarray


def load_target_trajectory() -> np.ndarray:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing {INPUT_PATH}. Run unit05_smoothing_metrics.py first."
        )
    rows = []
    with INPUT_PATH.open("r", newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        for row in reader:
            rows.append([float(row[f"smooth_q{i}_rad"]) for i in range(1, 8)])
    return np.asarray(rows)


def reset_configuration(robot_id: int, q: np.ndarray, client_id: int) -> None:
    for joint_index, angle in enumerate(q):
        p.resetJointState(
            robot_id,
            joint_index,
            float(angle),
            targetVelocity=0.0,
            physicsClientId=client_id,
        )


def read_joint_positions(robot_id: int, client_id: int) -> np.ndarray:
    states = p.getJointStates(
        robot_id,
        list(range(7)),
        physicsClientId=client_id,
    )
    return np.asarray([state[0] for state in states])


def calculate_fk_positions(
    robot_id: int, q_frames: np.ndarray, client_id: int
) -> np.ndarray:
    positions = []
    for q in q_frames:
        reset_configuration(robot_id, q, client_id)
        state = p.getLinkState(
            robot_id,
            END_EFFECTOR_LINK_INDEX,
            computeForwardKinematics=True,
            physicsClientId=client_id,
        )
        positions.append(state[4])
    return np.asarray(positions)


def execute_rollout(
    name: str,
    robot_id: int,
    target_q: np.ndarray,
    simulation_steps_per_target: int,
    client_id: int,
) -> tuple[np.ndarray, float]:
    reset_configuration(robot_id, target_q[0], client_id)
    actual_frames = []

    for q_command in target_q:
        p.setJointMotorControlArray(
            bodyUniqueId=robot_id,
            jointIndices=list(range(7)),
            controlMode=p.POSITION_CONTROL,
            targetPositions=q_command.tolist(),
            forces=[120.0] * 7,
            positionGains=[0.25] * 7,
            velocityGains=[1.0] * 7,
            physicsClientId=client_id,
        )
        for _ in range(simulation_steps_per_target):
            p.stepSimulation(physicsClientId=client_id)
        actual_frames.append(read_joint_positions(robot_id, client_id))

    sample_dt_s = simulation_steps_per_target * PHYSICS_TIMESTEP_S
    return np.asarray(actual_frames), sample_dt_s


def build_rollout(
    name: str,
    target_q: np.ndarray,
    actual_q: np.ndarray,
    sample_dt_s: float,
    target_positions: np.ndarray,
    actual_positions: np.ndarray,
) -> Rollout:
    joint_error_norm = np.linalg.norm(actual_q - target_q, axis=1)
    actual_velocity = np.gradient(actual_q, sample_dt_s, axis=0, edge_order=2)
    actual_speed_norm = np.linalg.norm(actual_velocity, axis=1)
    task_position_error_m = np.linalg.norm(actual_positions - target_positions, axis=1)
    return Rollout(
        name=name,
        sample_dt_s=sample_dt_s,
        target_q=target_q,
        actual_q=actual_q,
        joint_error_norm=joint_error_norm,
        actual_speed_norm=actual_speed_norm,
        task_position_error_m=task_position_error_m,
    )


def main() -> None:
    target_q = load_target_trajectory()
    client_id = p.connect(p.DIRECT)
    if client_id < 0:
        raise RuntimeError("Could not connect to PyBullet")

    try:
        p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=client_id)
        p.setTimeStep(PHYSICS_TIMESTEP_S, physicsClientId=client_id)
        p.setGravity(0.0, 0.0, -9.81, physicsClientId=client_id)
        robot_id = p.loadURDF(
            "kuka_iiwa/model.urdf",
            useFixedBase=True,
            physicsClientId=client_id,
        )

        normal_actual, normal_dt = execute_rollout(
            "normal_2s", robot_id, target_q, 4, client_id
        )
        fast_actual, fast_dt = execute_rollout(
            "fast_0.5s", robot_id, target_q, 1, client_id
        )

        target_positions = calculate_fk_positions(robot_id, target_q, client_id)
        normal_positions = calculate_fk_positions(robot_id, normal_actual, client_id)
        fast_positions = calculate_fk_positions(robot_id, fast_actual, client_id)
    finally:
        p.disconnect(client_id)

    rollouts = [
        build_rollout(
            "normal_2s",
            target_q,
            normal_actual,
            normal_dt,
            target_positions,
            normal_positions,
        ),
        build_rollout(
            "fast_0.5s",
            target_q,
            fast_actual,
            fast_dt,
            target_positions,
            fast_positions,
        ),
    ]

    with CSV_PATH.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(
            [
                "rollout",
                "frame",
                "time_s",
                "joint_error_norm_rad",
                "actual_speed_norm_rad_s",
                "task_position_error_m",
                *[f"target_q{i}_rad" for i in range(1, 8)],
                *[f"actual_q{i}_rad" for i in range(1, 8)],
            ]
        )
        for rollout in rollouts:
            for frame_index in range(len(target_q)):
                writer.writerow(
                    [
                        rollout.name,
                        frame_index,
                        frame_index * rollout.sample_dt_s,
                        rollout.joint_error_norm[frame_index],
                        rollout.actual_speed_norm[frame_index],
                        rollout.task_position_error_m[frame_index],
                        *rollout.target_q[frame_index].tolist(),
                        *rollout.actual_q[frame_index].tolist(),
                    ]
                )

    frames = np.arange(len(target_q))
    figure, axes = plt.subplots(4, 1, figsize=(10, 13))
    axes[0].plot(frames, target_q[:, 3], "k--", label="target q4")
    for rollout in rollouts:
        axes[0].plot(frames, rollout.actual_q[:, 3], label=f"actual: {rollout.name}")
    axes[0].set_ylabel("q4 [rad]")
    axes[0].set_title("Same path, different execution duration")
    axes[0].grid(True)
    axes[0].legend()

    for rollout in rollouts:
        axes[1].plot(frames, rollout.joint_error_norm, label=rollout.name)
    axes[1].set_ylabel("||q_actual - q_target|| [rad]")
    axes[1].set_title("Joint-space tracking error")
    axes[1].grid(True)
    axes[1].legend()

    for rollout in rollouts:
        axes[2].plot(frames, rollout.task_position_error_m * 1000, label=rollout.name)
    axes[2].set_ylabel("position error [mm]")
    axes[2].set_title("End-effector error caused by controller lag")
    axes[2].grid(True)
    axes[2].legend()

    for rollout in rollouts:
        axes[3].plot(frames, rollout.actual_speed_norm, label=rollout.name)
    axes[3].set_xlabel("trajectory frame")
    axes[3].set_ylabel("||q_dot_actual|| [rad/s]")
    axes[3].set_title("Actual joint-speed norm")
    axes[3].grid(True)
    axes[3].legend()

    figure.tight_layout()
    figure.savefig(FIGURE_PATH, dpi=160)
    plt.close(figure)

    print("\nPosition-control rollout: same path, different timing")
    print(f"physics timestep = {PHYSICS_TIMESTEP_S:.6f} s (240 Hz)")
    for rollout in rollouts:
        duration_s = (len(target_q) - 1) * rollout.sample_dt_s
        print(f"\n{rollout.name}")
        print(f"  command sample dt             = {rollout.sample_dt_s:.6f} s")
        print(f"  trajectory duration           = {duration_s:.3f} s")
        print(
            f"  max joint tracking error norm = "
            f"{rollout.joint_error_norm.max():.6f} rad"
        )
        print(
            f"  mean joint tracking error     = "
            f"{rollout.joint_error_norm.mean():.6f} rad"
        )
        print(
            f"  max end-effector error        = "
            f"{rollout.task_position_error_m.max() * 1000:.4f} mm"
        )
        print(
            f"  max actual speed norm         = "
            f"{rollout.actual_speed_norm.max():.4f} rad/s"
        )

    print("\nA smooth geometric path can still be too fast for a controller to track.")
    print(f"Saved rollout table to: {CSV_PATH}")
    print(f"Saved comparison figure to: {FIGURE_PATH}")


if __name__ == "__main__":
    main()

