"""Unit 2, part 3: turn a synthetic Z-depth image into a camera/world point cloud."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np

from unit02_camera_roundtrip import (
    backproject_pixels,
    make_world_t_camera,
    project_points,
    transform_points,
)


def make_depth_fixture() -> dict[str, np.ndarray]:
    """Create a foreground rectangle at Z=0.8 m over a background at Z=1.5 m."""
    height, width = 121, 161
    intrinsics = np.array(
        [[140.0, 0.0, 80.0], [0.0, 140.0, 60.0], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    depth_z = np.full((height, width), 1.5, dtype=np.float32)
    object_mask = np.zeros((height, width), dtype=bool)
    object_mask[40:81, 55:106] = True
    depth_z[object_mask] = 0.8
    return {
        "depth_z_m": depth_z,
        "object_mask": object_mask,
        "intrinsics": intrinsics,
        "world_T_camera": make_world_t_camera(),
    }


def depth_image_to_points(
    depth_z: np.ndarray, intrinsics: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Back-project every depth pixel and return row-wise pixels and camera points."""
    height, width = depth_z.shape
    grid_u, grid_v = np.meshgrid(np.arange(width), np.arange(height))
    pixels_uv = np.column_stack((grid_u.ravel(), grid_v.ravel())).astype(np.float64)
    points_camera = backproject_pixels(pixels_uv, depth_z.ravel(), intrinsics)
    return pixels_uv, points_camera


def run_depth_cloud_experiment() -> tuple[dict[str, np.ndarray], dict[str, float]]:
    fixture = make_depth_fixture()
    pixels, points_camera = depth_image_to_points(
        fixture["depth_z_m"], fixture["intrinsics"]
    )
    points_world = transform_points(fixture["world_T_camera"], points_camera)
    pixels_reprojected = project_points(points_camera, fixture["intrinsics"])

    center_index = 60 * 161 + 80
    off_axis_index = 40 * 161 + 55
    ranges = np.linalg.norm(points_camera, axis=1)
    metrics = {
        "point_count": float(len(points_camera)),
        "center_z_depth_m": float(points_camera[center_index, 2]),
        "center_range_m": float(ranges[center_index]),
        "off_axis_z_depth_m": float(points_camera[off_axis_index, 2]),
        "off_axis_range_m": float(ranges[off_axis_index]),
        "max_pixel_reprojection_error_px": float(
            np.max(np.linalg.norm(pixels_reprojected - pixels, axis=1))
        ),
    }
    arrays = {
        **fixture,
        "pixels_uv": pixels,
        "points_camera": points_camera,
        "points_world": points_world,
    }
    return arrays, metrics


def save_outputs(
    phase_root: Path, arrays: dict[str, np.ndarray], metrics: dict[str, float]
) -> None:
    data_dir = phase_root / "data"
    output_dir = phase_root / "outputs"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    fixture_path = data_dir / "unit02_rgbd_fixture.npz"
    np.savez_compressed(
        fixture_path,
        depth_z_m=arrays["depth_z_m"],
        object_mask=arrays["object_mask"],
        intrinsics=arrays["intrinsics"],
        world_T_camera=arrays["world_T_camera"],
    )

    report_path = output_dir / "unit02_depth_image_to_cloud.json"
    report_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    depth = arrays["depth_z_m"]
    points = arrays["points_camera"]
    mask_flat = arrays["object_mask"].ravel()
    sample = np.arange(0, len(points), 8)

    figure = plt.figure(figsize=(11, 4.8), constrained_layout=True)
    depth_axis = figure.add_subplot(1, 2, 1)
    image = depth_axis.imshow(depth, cmap="viridis", vmin=0.7, vmax=1.6)
    depth_axis.set_title("Synthetic Z-depth image")
    depth_axis.set_xlabel("pixel u")
    depth_axis.set_ylabel("pixel v")
    figure.colorbar(image, ax=depth_axis, label="Z-depth [m]")

    cloud_axis = figure.add_subplot(1, 2, 2, projection="3d")
    colors = np.where(mask_flat[sample], "tab:orange", "tab:blue")
    cloud_axis.scatter(
        points[sample, 0],
        points[sample, 2],
        -points[sample, 1],
        c=colors,
        s=2,
        alpha=0.7,
    )
    cloud_axis.set_title("Back-projected camera-frame cloud")
    cloud_axis.set_xlabel("camera x [m]")
    cloud_axis.set_ylabel("camera z [m]")
    cloud_axis.set_zlabel("camera -y [m]")
    cloud_axis.view_init(elev=20, azim=-65)

    figure_path = output_dir / "unit02_depth_image_to_cloud.png"
    figure.savefig(figure_path, dpi=160)
    plt.close(figure)

    print(f"\nSaved fixture to: {fixture_path}")
    print(f"Saved report  to: {report_path}")
    print(f"Saved figure  to: {figure_path}")


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    arrays, metrics = run_depth_cloud_experiment()

    print("Unit 2 part 3 - Z-depth image to point cloud")
    print("foreground rectangle Z-depth = 0.8 m")
    print("background plane Z-depth     = 1.5 m")
    print(f"point count                  = {int(metrics['point_count'])}")
    print("\nSame Z-depth, different Euclidean range")
    print(
        "center pixel:   "
        f"Z = {metrics['center_z_depth_m']:.6f} m, "
        f"range = {metrics['center_range_m']:.6f} m"
    )
    print(
        "off-axis pixel: "
        f"Z = {metrics['off_axis_z_depth_m']:.6f} m, "
        f"range = {metrics['off_axis_range_m']:.6f} m"
    )
    print(
        "max pixel reprojection error = "
        f"{metrics['max_pixel_reprojection_error_px']:.3e} px"
    )
    save_outputs(phase_root, arrays, metrics)


if __name__ == "__main__":
    main()

