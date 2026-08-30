from __future__ import annotations

import sys
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from unit02_depth_image_to_cloud import run_depth_cloud_experiment  # noqa: E402


def test_center_pixel_range_equals_z_depth() -> None:
    _arrays, metrics = run_depth_cloud_experiment()
    assert abs(metrics["center_range_m"] - metrics["center_z_depth_m"]) < 1e-12


def test_off_axis_range_is_greater_than_z_depth() -> None:
    _arrays, metrics = run_depth_cloud_experiment()
    assert metrics["off_axis_range_m"] > metrics["off_axis_z_depth_m"]


def test_full_depth_image_reprojects_to_original_pixels() -> None:
    _arrays, metrics = run_depth_cloud_experiment()
    assert metrics["max_pixel_reprojection_error_px"] < 1e-9

