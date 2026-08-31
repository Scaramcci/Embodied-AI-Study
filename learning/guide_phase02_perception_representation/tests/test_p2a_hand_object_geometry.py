from __future__ import annotations

import sys
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from p2a_hand_object_geometry import run_hand_object_experiment  # noqa: E402


def test_local_cloud_is_transformed_to_world_without_shape_change() -> None:
    arrays, metrics = run_hand_object_experiment()
    assert arrays["object_cloud_local"].shape == arrays["object_cloud_world"].shape
    assert metrics["open3d_numpy_transform_error_m"] < 1e-12
    assert metrics["rigid_radius_preservation_error_m"] < 1e-12


def test_world_cloud_centroid_matches_object_pose_translation() -> None:
    arrays, metrics = run_hand_object_experiment()
    assert metrics["local_cloud_centroid_norm_m"] < 1e-12
    assert metrics["world_centroid_to_pose_translation_error_m"] < 1e-12
    assert arrays["hand_keypoints_world"].shape == (6, 3)

