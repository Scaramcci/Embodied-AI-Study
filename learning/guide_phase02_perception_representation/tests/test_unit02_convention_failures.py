from __future__ import annotations

import sys
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from unit02_convention_failures import run_failure_experiment  # noqa: E402


def test_depth_scale_error_can_hide_from_reprojection() -> None:
    result = run_failure_experiment()["millimeter_depth_treated_as_meter"]
    assert result["camera_3d_error_m"] > 100.0
    assert result["pixel_reprojection_error_px"] < 1e-9


def test_range_is_not_z_depth_off_optical_axis() -> None:
    result = run_failure_experiment()["euclidean_range_treated_as_z_depth"]
    assert result["camera_3d_error_m"] > 0.0
    assert result["pixel_reprojection_error_px"] < 1e-9


def test_wrong_transform_direction_changes_world_points() -> None:
    result = run_failure_experiment()["camera_T_world_used_as_world_T_camera"]
    assert result["world_3d_error_m"] > 1.0

