"""Unit 2, part 1: pinhole projection, depth back-projection, and frame round trip."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


def project_points(points_camera: np.ndarray, intrinsics: np.ndarray) -> np.ndarray:
    """Project camera-frame 3D points to image pixels [u, v]."""
    points = np.asarray(points_camera, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError(f"points_camera must have shape [N,3], got {points.shape}")
    if not np.all(points[:, 2] > 0.0):
        raise ValueError("all camera-frame points must have positive Z depth")

    fx, fy = intrinsics[0, 0], intrinsics[1, 1]
    cx, cy = intrinsics[0, 2], intrinsics[1, 2]
    u = fx * points[:, 0] / points[:, 2] + cx
    v = fy * points[:, 1] / points[:, 2] + cy
    return np.column_stack((u, v))


def backproject_pixels(
    pixels_uv: np.ndarray, depth_z: np.ndarray, intrinsics: np.ndarray
) -> np.ndarray:
    """Back-project pixels and optical-axis depth to camera-frame 3D points."""
    pixels = np.asarray(pixels_uv, dtype=np.float64)
    depth = np.asarray(depth_z, dtype=np.float64)
    if pixels.ndim != 2 or pixels.shape[1] != 2:
        raise ValueError(f"pixels_uv must have shape [N,2], got {pixels.shape}")
    if depth.shape != (len(pixels),):
        raise ValueError(f"depth_z must have shape ({len(pixels)},), got {depth.shape}")
    if not np.all(depth > 0.0):
        raise ValueError("all depth values must be positive")

    fx, fy = intrinsics[0, 0], intrinsics[1, 1]
    cx, cy = intrinsics[0, 2], intrinsics[1, 2]
    x = (pixels[:, 0] - cx) * depth / fx
    y = (pixels[:, 1] - cy) * depth / fy
    return np.column_stack((x, y, depth))


def transform_points(transform: np.ndarray, points: np.ndarray) -> np.ndarray:
    """Apply target_T_source to row-wise source-frame points."""
    transform = np.asarray(transform, dtype=np.float64)
    points = np.asarray(points, dtype=np.float64)
    if transform.shape != (4, 4):
        raise ValueError(f"transform must have shape [4,4], got {transform.shape}")
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError(f"points must have shape [N,3], got {points.shape}")
    return points @ transform[:3, :3].T + transform[:3, 3]


def make_world_t_camera() -> np.ndarray:
    """Create a fixed camera pose in the world frame."""
    angle = np.deg2rad(20.0)
    rotation_y = np.array(
        [
            [np.cos(angle), 0.0, np.sin(angle)],
            [0.0, 1.0, 0.0],
            [-np.sin(angle), 0.0, np.cos(angle)],
        ],
        dtype=np.float64,
    )
    world_t_camera = np.eye(4, dtype=np.float64)
    world_t_camera[:3, :3] = rotation_y
    world_t_camera[:3, 3] = np.array([0.50, -0.20, 1.00])
    return world_t_camera


def run_roundtrip() -> tuple[dict[str, np.ndarray], dict[str, float]]:
    intrinsics = np.array(
        [[600.0, 0.0, 320.0], [0.0, 610.0, 240.0], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    points_camera = np.array(
        [
            [0.00, 0.00, 1.00],
            [0.10, -0.05, 1.20],
            [-0.15, 0.08, 1.50],
            [0.20, 0.12, 2.00],
            [-0.08, -0.10, 0.80],
        ],
        dtype=np.float64,
    )
    world_t_camera = make_world_t_camera()
    camera_t_world = np.linalg.inv(world_t_camera)

    pixels = project_points(points_camera, intrinsics)
    depth_z = points_camera[:, 2].copy()
    camera_backprojected = backproject_pixels(pixels, depth_z, intrinsics)
    points_world = transform_points(world_t_camera, camera_backprojected)
    camera_recovered = transform_points(camera_t_world, points_world)
    pixels_reprojected = project_points(camera_recovered, intrinsics)

    metrics = {
        "max_camera_point_error_m": float(
            np.max(np.linalg.norm(camera_recovered - points_camera, axis=1))
        ),
        "max_world_roundtrip_error_m": float(
            np.max(np.linalg.norm(camera_backprojected - points_camera, axis=1))
        ),
        "max_pixel_reprojection_error_px": float(
            np.max(np.linalg.norm(pixels_reprojected - pixels, axis=1))
        ),
    }
    arrays = {
        "intrinsics": intrinsics,
        "world_T_camera": world_t_camera,
        "points_camera": points_camera,
        "pixels_uv": pixels,
        "depth_z": depth_z,
        "points_world": points_world,
        "camera_recovered": camera_recovered,
        "pixels_reprojected": pixels_reprojected,
    }
    return arrays, metrics


def save_outputs(
    phase_root: Path, arrays: dict[str, np.ndarray], metrics: dict[str, float]
) -> None:
    output_dir = phase_root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "unit02_camera_roundtrip.csv"
    headers = [
        "point_index",
        "camera_x_m",
        "camera_y_m",
        "camera_z_depth_m",
        "pixel_u",
        "pixel_v",
        "world_x_m",
        "world_y_m",
        "world_z_m",
        "recovered_camera_x_m",
        "recovered_camera_y_m",
        "recovered_camera_z_m",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for index in range(len(arrays["points_camera"])):
            writer.writerow(
                [
                    index,
                    *arrays["points_camera"][index],
                    *arrays["pixels_uv"][index],
                    *arrays["points_world"][index],
                    *arrays["camera_recovered"][index],
                ]
            )

    report_path = output_dir / "unit02_camera_roundtrip.json"
    report_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"\nSaved point table to: {csv_path}")
    print(f"Saved metrics     to: {report_path}")


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    arrays, metrics = run_roundtrip()

    np.set_printoptions(precision=4, suppress=True)
    print("Unit 2 part 1 - camera projection and frame round trip")
    print("camera optical axes: +x right, +y down, +z forward")
    print("depth convention: Z coordinate along the camera optical axis")
    print("\nCamera intrinsics K =")
    print(arrays["intrinsics"])
    print("\nworld_T_camera =")
    print(arrays["world_T_camera"])
    print("\npoint_camera -> pixel [u,v] + depth -> point_world")
    for index in range(len(arrays["points_camera"])):
        print(
            f"{index}: camera {arrays['points_camera'][index]} -> "
            f"pixel {arrays['pixels_uv'][index]} depth {arrays['depth_z'][index]:.3f} -> "
            f"world {arrays['points_world'][index]}"
        )
    print("\nRound-trip errors")
    print(
        "max camera point error    = "
        f"{metrics['max_camera_point_error_m']:.3e} m"
    )
    print(
        "max back-projection error = "
        f"{metrics['max_world_roundtrip_error_m']:.3e} m"
    )
    print(
        "max pixel reproj. error   = "
        f"{metrics['max_pixel_reprojection_error_px']:.3e} px"
    )
    save_outputs(phase_root, arrays, metrics)


if __name__ == "__main__":
    main()

