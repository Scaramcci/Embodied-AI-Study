"""Unit 2, part 2: expose depth-unit, depth-definition, and transform-direction errors."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from unit02_camera_roundtrip import (
    backproject_pixels,
    project_points,
    run_roundtrip,
    transform_points,
)


def max_point_error(actual: np.ndarray, reference: np.ndarray) -> float:
    return float(np.max(np.linalg.norm(actual - reference, axis=1)))


def max_pixel_error(actual: np.ndarray, reference: np.ndarray) -> float:
    return float(np.max(np.linalg.norm(actual - reference, axis=1)))


def run_failure_experiment() -> dict[str, dict[str, float | str]]:
    arrays, _roundtrip_metrics = run_roundtrip()
    intrinsics = arrays["intrinsics"]
    pixels = arrays["pixels_uv"]
    reference_camera = arrays["points_camera"]
    reference_world = arrays["points_world"]

    # Failure 1: a depth sensor reports millimetres, but the values are treated as metres.
    depth_mm_mislabeled_as_m = arrays["depth_z"] * 1000.0
    camera_from_wrong_scale = backproject_pixels(
        pixels, depth_mm_mislabeled_as_m, intrinsics
    )
    pixels_from_wrong_scale = project_points(camera_from_wrong_scale, intrinsics)

    # Failure 2: Euclidean range is used where the back-projection expects Z-depth.
    euclidean_range = np.linalg.norm(reference_camera, axis=1)
    camera_from_range_as_z = backproject_pixels(pixels, euclidean_range, intrinsics)
    pixels_from_range_as_z = project_points(camera_from_range_as_z, intrinsics)

    # Failure 3: camera_T_world is applied to camera-frame points by mistake.
    camera_t_world = np.linalg.inv(arrays["world_T_camera"])
    world_from_wrong_direction = transform_points(camera_t_world, reference_camera)

    results: dict[str, dict[str, float | str]] = {
        "millimeter_depth_treated_as_meter": {
            "camera_3d_error_m": max_point_error(
                camera_from_wrong_scale, reference_camera
            ),
            "pixel_reprojection_error_px": max_pixel_error(
                pixels_from_wrong_scale, pixels
            ),
            "diagnosis": "3D scale is wrong although pixel reprojection still matches",
        },
        "euclidean_range_treated_as_z_depth": {
            "camera_3d_error_m": max_point_error(
                camera_from_range_as_z, reference_camera
            ),
            "pixel_reprojection_error_px": max_pixel_error(
                pixels_from_range_as_z, pixels
            ),
            "diagnosis": "point stays on the same camera ray but has the wrong distance",
        },
        "camera_T_world_used_as_world_T_camera": {
            "world_3d_error_m": max_point_error(
                world_from_wrong_direction, reference_world
            ),
            "diagnosis": "the inverse transform maps in the opposite frame direction",
        },
    }
    return results


def save_results(phase_root: Path, results: dict[str, dict[str, float | str]]) -> None:
    output_dir = phase_root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "unit02_convention_failures.json"
    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    csv_path = output_dir / "unit02_convention_failures.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["case", "camera_3d_error_m", "world_3d_error_m", "pixel_error_px", "diagnosis"]
        )
        for case_name, metrics in results.items():
            writer.writerow(
                [
                    case_name,
                    metrics.get("camera_3d_error_m", ""),
                    metrics.get("world_3d_error_m", ""),
                    metrics.get("pixel_reprojection_error_px", ""),
                    metrics["diagnosis"],
                ]
            )
    print(f"\nSaved table  to: {csv_path}")
    print(f"Saved report to: {json_path}")


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    results = run_failure_experiment()

    print("Unit 2 part 2 - convention failures")
    for case_name, metrics in results.items():
        print(f"\n{case_name}")
        if "camera_3d_error_m" in metrics:
            print(f"  max camera 3D error = {metrics['camera_3d_error_m']:.6f} m")
        if "world_3d_error_m" in metrics:
            print(f"  max world 3D error  = {metrics['world_3d_error_m']:.6f} m")
        if "pixel_reprojection_error_px" in metrics:
            print(
                "  max pixel error     = "
                f"{metrics['pixel_reprojection_error_px']:.6e} px"
            )
        print(f"  diagnosis           = {metrics['diagnosis']}")

    print("\nA zero pixel reprojection error does not prove that metric 3D scale is correct.")
    save_results(phase_root, results)


if __name__ == "__main__":
    main()

