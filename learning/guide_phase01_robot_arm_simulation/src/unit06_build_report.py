"""Unit 6: build one paper-style report from the validated stage outputs."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pybullet as p
import pybullet_data


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
REPORT_PATH = OUTPUT_DIR / "unit06_integrated_report.md"
JSON_PATH = OUTPUT_DIR / "unit06_integrated_metrics.json"


def read_csv(name: str) -> list[dict[str, str]]:
    path = OUTPUT_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite output: {path}")
    with path.open("r", newline="", encoding="utf-8") as input_file:
        return list(csv.DictReader(input_file))


def values(rows: list[dict[str, str]], key: str) -> np.ndarray:
    return np.asarray([float(row[key]) for row in rows])


def bool_value(value: str) -> bool:
    return value.strip().lower() == "true"


def get_joint_limits() -> tuple[np.ndarray, np.ndarray]:
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
        return np.asarray(lower), np.asarray(upper)
    finally:
        p.disconnect(client_id)


def main() -> None:
    trajectory_rows = [
        row
        for row in read_csv("unit04_trajectory_results.csv")
        if row["strategy"] == "previous_solution"
    ]
    failure_rows = read_csv("unit04_failed_waypoints.csv")
    smoothing_rows = read_csv("unit05_smoothing_metrics.csv")
    control_rows = read_csv("unit05_position_control.csv")

    normal_rows = [row for row in control_rows if row["rollout"] == "normal_2s"]
    fast_rows = [row for row in control_rows if row["rollout"] == "fast_0.5s"]
    lower, upper = get_joint_limits()

    reachable_q = np.asarray(
        [
            [float(row[f"q{i}_rad"]) for i in range(1, 8)]
            for row in trajectory_rows
        ]
    )
    limit_violation_frames = int(
        np.count_nonzero(
            np.any((reachable_q < lower[None, :]) | (reachable_q > upper[None, :]), axis=1)
        )
    )

    reachable_success = np.asarray(
        [bool_value(row["success"]) for row in trajectory_rows]
    )
    failed_mask = np.asarray([not bool_value(row["success"]) for row in failure_rows])
    successful_failure_case_indices = np.flatnonzero(~failed_mask)
    retained_gaps = np.diff(successful_failure_case_indices)

    metrics = {
        "input_contract": {
            "frames": len(trajectory_rows),
            "position_shape": [len(trajectory_rows), 3],
            "orientation_shape": [len(trajectory_rows), 4],
            "world_frame": "world (robot base coincident in this setup)",
            "position_unit": "m",
            "joint_angle_unit": "rad",
            "quaternion_order": "xyzw",
            "sample_rate_hz": 60.0,
            "timestep_s": 1.0 / 60.0,
            "duration_s": (len(trajectory_rows) - 1) / 60.0,
        },
        "reachable_ik_fk": {
            "successful_frames": int(reachable_success.sum()),
            "total_frames": len(trajectory_rows),
            "max_position_error_mm": float(
                values(trajectory_rows, "position_error_m").max() * 1000
            ),
            "max_orientation_error_deg": float(
                np.rad2deg(values(trajectory_rows, "orientation_error_rad").max())
            ),
            "max_adjacent_q_change_rad": float(
                values(trajectory_rows, "delta_q_norm_rad").max()
            ),
            "joint_limit_violation_frames": limit_violation_frames,
        },
        "raw_vs_smoothed": {
            "raw_max_fk_position_error_mm": float(
                values(smoothing_rows, "raw_position_error_m").max() * 1000
            ),
            "smoothed_max_fk_position_error_mm": float(
                values(smoothing_rows, "smooth_position_error_m").max() * 1000
            ),
            "raw_max_speed_norm_rad_s": float(
                values(smoothing_rows, "raw_speed_norm_rad_s").max()
            ),
            "smoothed_max_speed_norm_rad_s": float(
                values(smoothing_rows, "smooth_speed_norm_rad_s").max()
            ),
            "raw_max_acceleration_norm_rad_s2": float(
                values(smoothing_rows, "raw_acceleration_norm_rad_s2").max()
            ),
            "smoothed_max_acceleration_norm_rad_s2": float(
                values(smoothing_rows, "smooth_acceleration_norm_rad_s2").max()
            ),
        },
        "position_control": {
            "normal_2s": {
                "max_joint_tracking_error_rad": float(
                    values(normal_rows, "joint_error_norm_rad").max()
                ),
                "mean_joint_tracking_error_rad": float(
                    values(normal_rows, "joint_error_norm_rad").mean()
                ),
                "max_end_effector_error_mm": float(
                    values(normal_rows, "task_position_error_m").max() * 1000
                ),
                "max_actual_speed_norm_rad_s": float(
                    values(normal_rows, "actual_speed_norm_rad_s").max()
                ),
            },
            "fast_0_5s": {
                "max_joint_tracking_error_rad": float(
                    values(fast_rows, "joint_error_norm_rad").max()
                ),
                "mean_joint_tracking_error_rad": float(
                    values(fast_rows, "joint_error_norm_rad").mean()
                ),
                "max_end_effector_error_mm": float(
                    values(fast_rows, "task_position_error_m").max() * 1000
                ),
                "max_actual_speed_norm_rad_s": float(
                    values(fast_rows, "actual_speed_norm_rad_s").max()
                ),
            },
        },
        "boundary_failure_case": {
            "failed_frames": int(failed_mask.sum()),
            "total_frames": len(failure_rows),
            "max_position_error_mm": float(
                values(failure_rows, "position_error_m").max() * 1000
            ),
            "max_adjacent_q_change_rad": float(
                values(failure_rows, "delta_q_norm_rad").max()
            ),
            "largest_retained_frame_gap_if_failures_deleted": int(
                retained_gaps.max() if len(retained_gaps) else 0
            ),
        },
        "thresholds": {
            "ik_fk_position_mm": 5.0,
            "ik_fk_orientation_deg": 2.0,
        },
    }

    JSON_PATH.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    contract = metrics["input_contract"]
    reachable = metrics["reachable_ik_fk"]
    smoothing = metrics["raw_vs_smoothed"]
    normal = metrics["position_control"]["normal_2s"]
    fast = metrics["position_control"]["fast_0_5s"]
    boundary = metrics["boundary_failure_case"]

    report = f"""# Unit 6：论文导向综合实验报告

## 1. 输入约定

- 腕部位置 shape：`{contract['position_shape']}`
- 腕部方向 shape：`{contract['orientation_shape']}`
- 坐标系：`{contract['world_frame']}`
- 位置单位：`{contract['position_unit']}`
- 关节角单位：`{contract['joint_angle_unit']}`
- 四元数顺序：`{contract['quaternion_order']}`
- 采样率：`{contract['sample_rate_hz']:.1f} Hz`
- timestep：`{contract['timestep_s']:.6f} s`
- 总时长：`{contract['duration_s']:.3f} s`

## 2. 可达轨迹：IK/FK 验证

- 成功帧：`{reachable['successful_frames']}/{reachable['total_frames']}`
- 最大位置误差：`{reachable['max_position_error_mm']:.4f} mm`
- 最大姿态误差：`{reachable['max_orientation_error_deg']:.4f} deg`
- 最大相邻关节变化：`{reachable['max_adjacent_q_change_rad']:.6f} rad`
- 关节限位违规帧：`{reachable['joint_limit_violation_frames']}`

![reachable trajectory](unit04_trajectory_summary.png)

## 3. 原始轨迹与平滑轨迹

| 指标 | 原始 | 平滑后 |
|---|---:|---:|
| 最大 FK 位置误差 (mm) | {smoothing['raw_max_fk_position_error_mm']:.4f} | {smoothing['smoothed_max_fk_position_error_mm']:.4f} |
| 最大速度范数 (rad/s) | {smoothing['raw_max_speed_norm_rad_s']:.4f} | {smoothing['smoothed_max_speed_norm_rad_s']:.4f} |
| 最大加速度范数 (rad/s²) | {smoothing['raw_max_acceleration_norm_rad_s2']:.4f} | {smoothing['smoothed_max_acceleration_norm_rad_s2']:.4f} |

![smoothing metrics](unit05_smoothing_metrics.png)

## 4. Position control：正常与快速执行

| 指标 | 2 秒执行 | 0.5 秒执行 |
|---|---:|---:|
| 最大 joint tracking error (rad) | {normal['max_joint_tracking_error_rad']:.6f} | {fast['max_joint_tracking_error_rad']:.6f} |
| 平均 joint tracking error (rad) | {normal['mean_joint_tracking_error_rad']:.6f} | {fast['mean_joint_tracking_error_rad']:.6f} |
| 最大末端位置误差 (mm) | {normal['max_end_effector_error_mm']:.4f} | {fast['max_end_effector_error_mm']:.4f} |
| 最大实际速度范数 (rad/s) | {normal['max_actual_speed_norm_rad_s']:.4f} | {fast['max_actual_speed_norm_rad_s']:.4f} |

![position control](unit05_position_control.png)

## 5. 边界与失败案例

- 失败帧：`{boundary['failed_frames']}/{boundary['total_frames']}`
- 最大位置误差：`{boundary['max_position_error_mm']:.3f} mm`
- 最大相邻关节变化：`{boundary['max_adjacent_q_change_rad']:.6f} rad`
- 若删除失败帧，最大原始时间缺口：`{boundary['largest_retained_frame_gap_if_failures_deleted']} frames`

![failed waypoints](unit04_failed_waypoints.png)

## 6. 结论

1. IK 返回候选关节角后必须用 FK 回代并检查位置、姿态和关节限位。
2. 单帧 IK/FK 成功不保证关节轨迹平滑；必须检查相邻变化、速度和加速度。
3. 平滑能降低高频速度与加速度，但平滑后仍需重新验证任务空间误差。
4. 相同几何轨迹以更快时间尺度执行，会显著增大 tracking error。
5. 失败帧必须保留原始索引与失败标记，不能静默删除。
"""
    REPORT_PATH.write_text(report, encoding="utf-8")

    print("\nUnit 6 integrated report")
    print(f"reachable IK/FK frames       = {reachable['successful_frames']}/{reachable['total_frames']}")
    print(f"joint-limit violation frames = {reachable['joint_limit_violation_frames']}")
    print(f"boundary failed frames       = {boundary['failed_frames']}/{boundary['total_frames']}")
    print(f"normal execution max EE error = {normal['max_end_effector_error_mm']:.4f} mm")
    print(f"fast execution max EE error   = {fast['max_end_effector_error_mm']:.4f} mm")
    print(f"\nSaved report to: {REPORT_PATH}")
    print(f"Saved machine-readable metrics to: {JSON_PATH}")


if __name__ == "__main__":
    main()

