"""Unit 1: build and validate a canonical perception data packet."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np


BODY_JOINT_NAMES = (
    "left_shoulder",
    "left_elbow",
    "left_wrist",
    "right_shoulder",
    "right_elbow",
    "right_wrist",
)
HAND_KEYPOINT_NAMES = (
    "palm",
    "thumb_tip",
    "index_tip",
    "middle_tip",
    "ring_tip",
    "little_tip",
)


class SchemaValidationError(ValueError):
    """Raised when an array packet violates the canonical data contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SchemaValidationError(message)


def _require_shape(name: str, value: np.ndarray, shape: tuple[int, ...]) -> None:
    _require(value.shape == shape, f"{name}: expected shape {shape}, got {value.shape}")


def _require_finite(name: str, value: np.ndarray) -> None:
    _require(np.isfinite(value).all(), f"{name}: contains NaN or infinity")


def _require_finite_where(
    name: str, value: np.ndarray, valid: np.ndarray
) -> None:
    """Require finite values only at observations declared valid."""
    expanded_valid = valid
    while expanded_valid.ndim < value.ndim:
        expanded_valid = expanded_valid[..., None]
    expanded_valid = np.broadcast_to(expanded_valid, value.shape)
    _require(
        bool(np.isfinite(value[expanded_valid]).all()),
        f"{name}: a valid observation contains NaN or infinity",
    )


def _require_unit_quaternions(
    name: str, value: np.ndarray, valid: np.ndarray | None = None
) -> None:
    norms = np.linalg.norm(value, axis=-1)
    if valid is not None:
        norms = norms[valid]
    max_error = float(np.max(np.abs(norms - 1.0)))
    _require(max_error < 1e-5, f"{name}: quaternion norm error {max_error:.3e}")


def validate_packet(arrays: dict[str, np.ndarray], metadata: dict[str, Any]) -> None:
    """Validate both numerical arrays and the metadata that gives them meaning."""
    required_metadata = {
        "schema_version",
        "coordinate_frames",
        "position_unit",
        "time_unit",
        "quaternion_order",
        "body_joint_names",
        "hand_keypoint_names",
        "timestamp_source",
        "confidence_definition",
        "missing_value_policy",
    }
    missing = sorted(required_metadata - metadata.keys())
    _require(not missing, f"metadata: missing fields {missing}")
    _require(metadata["position_unit"] == "m", "position_unit: canonical unit must be 'm'")
    _require(metadata["time_unit"] == "s", "time_unit: canonical unit must be 's'")
    _require(
        metadata["quaternion_order"] == "xyzw",
        "quaternion_order: canonical order must be 'xyzw'",
    )
    _require(
        tuple(metadata["body_joint_names"]) == BODY_JOINT_NAMES,
        "body_joint_names: semantic joint order does not match the canonical order",
    )
    _require(
        tuple(metadata["hand_keypoint_names"]) == HAND_KEYPOINT_NAMES,
        "hand_keypoint_names: keypoint order does not match the canonical order",
    )

    timestamps = arrays["timestamp"]
    _require(timestamps.ndim == 1, "timestamp: expected a one-dimensional array")
    frame_count = len(timestamps)
    _require(frame_count > 1, "timestamp: at least two frames are required")
    _require_finite("timestamp", timestamps)
    _require(
        bool(np.all(np.diff(timestamps) > 0.0)),
        "timestamp: values must be strictly increasing",
    )

    body_joint_count = len(BODY_JOINT_NAMES)
    hand_keypoint_count = len(HAND_KEYPOINT_NAMES)
    object_count = len(arrays["object_track_id"])
    point_count = arrays["object_cloud_local"].shape[1]

    expected_shapes = {
        "body_position": (frame_count, body_joint_count, 3),
        "body_quaternion_xyzw": (frame_count, body_joint_count, 4),
        "body_confidence": (frame_count, body_joint_count),
        "body_valid": (frame_count, body_joint_count),
        "body_edges": (2, 4),
        "hand_position": (frame_count, 2, hand_keypoint_count, 3),
        "hand_confidence": (frame_count, 2, hand_keypoint_count),
        "object_pose_xyzw": (frame_count, object_count, 7),
        "object_pose_confidence": (frame_count, object_count),
        "object_valid": (frame_count, object_count),
        "object_cloud_local": (object_count, point_count, 3),
    }
    for name, expected_shape in expected_shapes.items():
        _require_shape(name, arrays[name], expected_shape)

    _require(arrays["body_valid"].dtype == np.bool_, "body_valid: dtype must be bool")
    _require(arrays["object_valid"].dtype == np.bool_, "object_valid: dtype must be bool")

    for name in (
        "body_confidence",
        "hand_position",
        "hand_confidence",
        "object_pose_confidence",
        "object_cloud_local",
    ):
        _require_finite(name, arrays[name])

    _require_finite_where(
        "body_position", arrays["body_position"], arrays["body_valid"]
    )
    _require_finite_where(
        "body_quaternion_xyzw",
        arrays["body_quaternion_xyzw"],
        arrays["body_valid"],
    )
    _require_finite_where(
        "object_pose_xyzw", arrays["object_pose_xyzw"], arrays["object_valid"]
    )

    for name in ("body_confidence", "hand_confidence", "object_pose_confidence"):
        values = arrays[name]
        _require(
            bool(np.all((0.0 <= values) & (values <= 1.0))),
            f"{name}: values must lie in [0, 1]",
        )

    _require_unit_quaternions(
        "body_quaternion_xyzw",
        arrays["body_quaternion_xyzw"],
        arrays["body_valid"],
    )
    _require_unit_quaternions(
        "object_pose_xyzw",
        arrays["object_pose_xyzw"][..., 3:],
        arrays["object_valid"],
    )

    frames = metadata["coordinate_frames"]
    for field in ("body_position", "hand_position", "object_pose_xyzw"):
        _require(frames.get(field) == "world", f"{field}: expected world frame metadata")
    _require(
        frames.get("object_cloud_local") == "object",
        "object_cloud_local: expected object frame metadata",
    )


def make_synthetic_packet(frame_count: int = 10) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Create a small deterministic body/hand/object sequence in SI units."""
    timestamps = np.arange(frame_count, dtype=np.float64) / 30.0

    body_base = np.array(
        [
            [-0.18, 0.00, 1.45],
            [-0.34, 0.02, 1.22],
            [-0.43, 0.08, 1.02],
            [0.18, 0.00, 1.45],
            [0.34, 0.02, 1.22],
            [0.43, 0.08, 1.02],
        ],
        dtype=np.float32,
    )
    body_position = np.repeat(body_base[None, :, :], frame_count, axis=0)
    body_position[:, :, 1] += np.linspace(0.0, 0.045, frame_count, dtype=np.float32)[:, None]

    body_quaternion = np.zeros((frame_count, len(BODY_JOINT_NAMES), 4), dtype=np.float32)
    body_quaternion[..., 3] = 1.0

    hand_offsets = np.array(
        [
            [0.00, 0.00, 0.00],
            [-0.035, 0.030, 0.005],
            [-0.018, 0.065, 0.000],
            [0.000, 0.072, 0.000],
            [0.018, 0.065, 0.000],
            [0.034, 0.052, 0.000],
        ],
        dtype=np.float32,
    )
    wrists = body_position[:, [2, 5], :]
    hand_position = wrists[:, :, None, :] + hand_offsets[None, None, :, :]

    object_pose = np.zeros((frame_count, 1, 7), dtype=np.float32)
    object_pose[:, 0, :3] = np.array([0.42, 0.18, 0.92], dtype=np.float32)
    object_pose[:, 0, 1] += np.linspace(0.0, 0.03, frame_count, dtype=np.float32)
    object_pose[:, 0, 6] = 1.0

    half_extent = 0.04
    object_cloud = np.array(
        [
            [x, y, z]
            for x in (-half_extent, half_extent)
            for y in (-half_extent, half_extent)
            for z in (-half_extent, half_extent)
        ],
        dtype=np.float32,
    )[None, :, :]

    arrays = {
        "timestamp": timestamps,
        "body_position": body_position,
        "body_quaternion_xyzw": body_quaternion,
        "body_confidence": np.full((frame_count, 6), 0.95, dtype=np.float32),
        "body_valid": np.ones((frame_count, 6), dtype=bool),
        "body_edges": np.array([[0, 1, 3, 4], [1, 2, 4, 5]], dtype=np.int64),
        "hand_position": hand_position.astype(np.float32),
        "hand_confidence": np.full((frame_count, 2, 6), 0.92, dtype=np.float32),
        "object_track_id": np.array(["demo_object_0"]),
        "object_pose_xyzw": object_pose,
        "object_pose_confidence": np.full((frame_count, 1), 0.90, dtype=np.float32),
        "object_valid": np.ones((frame_count, 1), dtype=bool),
        "object_cloud_local": object_cloud,
    }
    metadata: dict[str, Any] = {
        "schema_version": "phase02.unit01.v1",
        "coordinate_frames": {
            "body_position": "world",
            "body_quaternion_xyzw": "world",
            "hand_position": "world",
            "object_pose_xyzw": "world",
            "object_cloud_local": "object",
        },
        "position_unit": "m",
        "time_unit": "s",
        "quaternion_order": "xyzw",
        "body_joint_names": list(BODY_JOINT_NAMES),
        "hand_keypoint_names": list(HAND_KEYPOINT_NAMES),
        "timestamp_source": "synthetic_30_hz_clock",
        "confidence_definition": "synthetic score in [0,1]; larger is more reliable",
        "missing_value_policy": "missing values use NaN and the corresponding valid mask is false",
    }
    return arrays, metadata


def build_failure_cases() -> dict[str, Callable[[dict[str, np.ndarray], dict[str, Any]], None]]:
    def wrong_unit(_arrays: dict[str, np.ndarray], metadata: dict[str, Any]) -> None:
        metadata["position_unit"] = "mm"

    def wrong_quaternion_order(_arrays: dict[str, np.ndarray], metadata: dict[str, Any]) -> None:
        metadata["quaternion_order"] = "wxyz"

    def repeated_timestamp(arrays: dict[str, np.ndarray], _metadata: dict[str, Any]) -> None:
        arrays["timestamp"][5] = arrays["timestamp"][4]

    def swapped_joint_order(_arrays: dict[str, np.ndarray], metadata: dict[str, Any]) -> None:
        names = metadata["body_joint_names"]
        names[0], names[1] = names[1], names[0]

    return {
        "meter_millimeter_contract": wrong_unit,
        "xyzw_wxyz_contract": wrong_quaternion_order,
        "non_increasing_timestamp": repeated_timestamp,
        "swapped_joint_order": swapped_joint_order,
    }


def run_experiment(root: Path) -> dict[str, Any]:
    arrays, metadata = make_synthetic_packet()
    validate_packet(arrays, metadata)

    data_dir = root / "data"
    output_dir = root / "outputs"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(data_dir / "unit01_valid_packet.npz", **arrays)
    (data_dir / "unit01_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("Unit 1 - canonical perception packet")
    print("Correct packet: PASS")
    print(f"frames                      = {len(arrays['timestamp'])}")
    print(f"body_position shape         = {arrays['body_position'].shape}")
    print(f"hand_position shape         = {arrays['hand_position'].shape}")
    print(f"object_pose_xyzw shape      = {arrays['object_pose_xyzw'].shape}")
    print(f"object_cloud_local shape    = {arrays['object_cloud_local'].shape}")
    print(f"position unit / frame       = {metadata['position_unit']} / world")
    print(f"quaternion order            = {metadata['quaternion_order']}")
    print("\nDeliberate contract violations")

    report: dict[str, Any] = {"correct_packet": "PASS", "failure_cases": {}}
    for case_name, corrupt in build_failure_cases().items():
        bad_arrays = {name: value.copy() for name, value in arrays.items()}
        bad_metadata = copy.deepcopy(metadata)
        corrupt(bad_arrays, bad_metadata)
        try:
            validate_packet(bad_arrays, bad_metadata)
        except SchemaValidationError as error:
            report["failure_cases"][case_name] = {
                "result": "REJECTED",
                "reason": str(error),
            }
            print(f"{case_name:<28} = REJECTED: {error}")
        else:
            report["failure_cases"][case_name] = {"result": "MISSED"}
            print(f"{case_name:<28} = MISSED")

    report_path = output_dir / "unit01_validation_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nSaved arrays   to: {data_dir / 'unit01_valid_packet.npz'}")
    print(f"Saved metadata to: {data_dir / 'unit01_metadata.json'}")
    print(f"Saved report   to: {report_path}")
    return report


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    run_experiment(phase_root)


if __name__ == "__main__":
    main()
