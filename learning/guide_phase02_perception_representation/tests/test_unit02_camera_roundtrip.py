from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from unit02_camera_roundtrip import (  # noqa: E402
    backproject_pixels,
    project_points,
    run_roundtrip,
)


def test_projection_frame_roundtrip() -> None:
    _arrays, metrics = run_roundtrip()
    assert metrics["max_camera_point_error_m"] < 1e-12
    assert metrics["max_world_roundtrip_error_m"] < 1e-12
    assert metrics["max_pixel_reprojection_error_px"] < 1e-9


def test_projection_rejects_nonpositive_depth() -> None:
    intrinsics = np.eye(3)
    with pytest.raises(ValueError, match="positive Z"):
        project_points(np.array([[0.0, 0.0, 0.0]]), intrinsics)


def test_backprojection_rejects_mismatched_depth_count() -> None:
    intrinsics = np.eye(3)
    with pytest.raises(ValueError, match="depth_z"):
        backproject_pixels(np.zeros((2, 2)), np.ones(1), intrinsics)

