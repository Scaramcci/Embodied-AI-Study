"""Unit 5: smooth a joint trajectory and compare temporal/task-space metrics."""

from __future__ import annotations

import csv
import os
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
from scipy.signal import savgol_filter

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


END_EFFECTOR_LINK_INDEX = 6
TIMESTEP_S = 1.0 / 60.0
INPUT_PATH = OUTPUT_DIR / "unit04_trajectory_results.csv"
CSV_PATH = OUTPUT_DIR / "unit05_smoothing_metrics.csv"
FIGURE_PATH = OUTPUT_DIR / "unit05_smoothing_metrics.png"


def load_clean_trajectory() -> np.ndarray:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing {INPUT_PATH}. Run unit04_trajectory_ik.py first."
        )
    rows = []
    with INPUT_PATH.open("r", newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        for row in reader:
            if row["strategy"] == "previous_solution":
                rows.append([float(row[f"q{i}_rad"]) for i in range(1, 8)])
    if not rows:
        raise RuntimeError("No previous_solution rows found in Unit 4 output")
    return np.asarray(rows)


def set_configuration(robot_id: int, q: np.ndarray, client_id: int) -> None:
    for joint_index, angle in enumerate(q):
        p.resetJointState(
            robot_id,
            joint_index,
            float(angle),
            physicsClientId=client_id,
        )


def end_effector_position(robot_id: int, q: np.ndarray, client_id: int) -> np.ndarray:
    set_configuration(robot_id, q, client_id)
    state = p.getLinkState(
        robot_id,
        END_EFFECTOR_LINK_INDEX,
        computeForwardKinematics=True,
        physicsClientId=client_id,
    )
    return np.asarray(state[4])


def derivatives(q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    velocity = np.gradient(q, TIMESTEP_S, axis=0, edge_order=2)
    acceleration = np.gradient(velocity, TIMESTEP_S, axis=0, edge_order=2)
    return velocity, acceleration


def main() -> None:
    clean_q = load_clean_trajectory()
    frame_count, joint_count = clean_q.shape
    time_s = np.arange(frame_count) * TIMESTEP_S

    # Deterministic high-frequency perturbation represents frame-wise IK jitter.
    phases = np.linspace(0.0, np.pi, joint_count)
    jitter = 0.008 * np.sin(2.0 * np.pi * 12.0 * time_s[:, None] + phases)
    raw_q = clean_q + jitter
    raw_q[58:61, 3] += np.array([0.03, 0.06, 0.03])

    smoothed_q = savgol_filter(
        raw_q,
        window_length=15,
        polyorder=3,
        axis=0,
        mode="interp",
    )

    raw_velocity, raw_acceleration = derivatives(raw_q)
    smooth_velocity, smooth_acceleration = derivatives(smoothed_q)

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
        target_positions = np.asarray(
            [end_effector_position(robot_id, q, client_id) for q in clean_q]
        )
        raw_positions = np.asarray(
            [end_effector_position(robot_id, q, client_id) for q in raw_q]
        )
        smooth_positions = np.asarray(
            [end_effector_position(robot_id, q, client_id) for q in smoothed_q]
        )
    finally:
        p.disconnect(client_id)

    raw_position_error = np.linalg.norm(raw_positions - target_positions, axis=1)
    smooth_position_error = np.linalg.norm(smooth_positions - target_positions, axis=1)
    raw_speed_norm = np.linalg.norm(raw_velocity, axis=1)
    smooth_speed_norm = np.linalg.norm(smooth_velocity, axis=1)
    raw_acceleration_norm = np.linalg.norm(raw_acceleration, axis=1)
    smooth_acceleration_norm = np.linalg.norm(smooth_acceleration, axis=1)

    with CSV_PATH.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(
            [
                "frame",
                "time_s",
                "raw_position_error_m",
                "smooth_position_error_m",
                "raw_speed_norm_rad_s",
                "smooth_speed_norm_rad_s",
                "raw_acceleration_norm_rad_s2",
                "smooth_acceleration_norm_rad_s2",
                *[f"raw_q{i}_rad" for i in range(1, 8)],
                *[f"smooth_q{i}_rad" for i in range(1, 8)],
            ]
        )
        for frame_index in range(frame_count):
            writer.writerow(
                [
                    frame_index,
                    time_s[frame_index],
                    raw_position_error[frame_index],
                    smooth_position_error[frame_index],
                    raw_speed_norm[frame_index],
                    smooth_speed_norm[frame_index],
                    raw_acceleration_norm[frame_index],
                    smooth_acceleration_norm[frame_index],
                    *raw_q[frame_index].tolist(),
                    *smoothed_q[frame_index].tolist(),
                ]
            )

    figure, axes = plt.subplots(4, 1, figsize=(10, 13))
    axes[0].plot(time_s, clean_q[:, 3], "k--", label="clean reference q4")
    axes[0].plot(time_s, raw_q[:, 3], alpha=0.75, label="raw q4")
    axes[0].plot(time_s, smoothed_q[:, 3], linewidth=2, label="smoothed q4")
    axes[0].set_ylabel("q4 [rad]")
    axes[0].set_title("Example joint before and after smoothing")
    axes[0].grid(True)
    axes[0].legend()

    axes[1].plot(time_s, raw_speed_norm, label="raw")
    axes[1].plot(time_s, smooth_speed_norm, label="smoothed")
    axes[1].set_ylabel("||q_dot|| [rad/s]")
    axes[1].set_title("Joint-trajectory speed norm")
    axes[1].grid(True)
    axes[1].legend()

    axes[2].plot(time_s, raw_acceleration_norm, label="raw")
    axes[2].plot(time_s, smooth_acceleration_norm, label="smoothed")
    axes[2].set_ylabel("||q_ddot|| [rad/s^2]")
    axes[2].set_title("Joint-trajectory acceleration norm")
    axes[2].grid(True)
    axes[2].legend()

    axes[3].plot(time_s, raw_position_error * 1000, label="raw")
    axes[3].plot(time_s, smooth_position_error * 1000, label="smoothed")
    axes[3].set_xlabel("time [s]")
    axes[3].set_ylabel("FK error [mm]")
    axes[3].set_title("Task-space position error relative to clean wrist path")
    axes[3].grid(True)
    axes[3].legend()

    figure.tight_layout()
    figure.savefig(FIGURE_PATH, dpi=160)
    plt.close(figure)

    print("\nRaw versus smoothed joint trajectory")
    print(f"frames / timestep / duration = {frame_count} / {TIMESTEP_S:.6f} s / {time_s[-1]:.3f} s")
    print("raw trajectory contains deterministic high-frequency jitter and a q4 spike")
    print("smoother = Savitzky-Golay(window=15, polynomial order=3)\n")
    print(f"max FK position error, raw      = {raw_position_error.max() * 1000:.4f} mm")
    print(f"max FK position error, smoothed = {smooth_position_error.max() * 1000:.4f} mm")
    print(f"max speed norm, raw             = {raw_speed_norm.max():.4f} rad/s")
    print(f"max speed norm, smoothed        = {smooth_speed_norm.max():.4f} rad/s")
    print(f"max acceleration norm, raw      = {raw_acceleration_norm.max():.4f} rad/s^2")
    print(f"max acceleration norm, smoothed = {smooth_acceleration_norm.max():.4f} rad/s^2")
    print("\nSmoothing must be followed by FK and joint-limit validation.")
    print(f"Saved metrics to: {CSV_PATH}")
    print(f"Saved comparison figure to: {FIGURE_PATH}")


if __name__ == "__main__":
    main()

