"""Unit 1, part 3: adapt a model-specific pose output to the canonical schema."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from unit01_schema_contract import (
    BODY_JOINT_NAMES,
    SchemaValidationError,
    make_synthetic_packet,
    validate_packet,
)


SOURCE_JOINT_NAMES = (
    "right_wrist",
    "left_elbow",
    "right_shoulder",
    "left_wrist",
    "left_shoulder",
    "right_elbow",
)


def make_mock_model_output() -> tuple[
    dict[str, np.ndarray | list[str]], dict[str, np.ndarray], dict[str, Any]
]:
    """Express the canonical body sequence using a deliberately different API."""
    reference_arrays, reference_metadata = make_synthetic_packet()
    source_indices = [BODY_JOINT_NAMES.index(name) for name in SOURCE_JOINT_NAMES]

    xyzw = reference_arrays["body_quaternion_xyzw"][:, source_indices]
    wxyz = np.concatenate((xyzw[..., 3:4], xyzw[..., :3]), axis=-1)
    raw: dict[str, np.ndarray | list[str]] = {
        "frame_time_ms": reference_arrays["timestamp"] * 1000.0,
        "pred_xyz_mm": reference_arrays["body_position"][:, source_indices] * 1000.0,
        "pred_quat_wxyz": wxyz,
        "score": reference_arrays["body_confidence"][:, source_indices],
        "observed": reference_arrays["body_valid"][:, source_indices],
        "joint_labels": list(SOURCE_JOINT_NAMES),
    }
    return raw, reference_arrays, reference_metadata


def adapt_body_model_output(
    raw: dict[str, np.ndarray | list[str]],
    packet_template: dict[str, np.ndarray],
    metadata_template: dict[str, Any],
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Convert units, quaternion layout, time, and joint order into canonical form."""
    source_names = list(raw["joint_labels"])
    missing = [name for name in BODY_JOINT_NAMES if name not in source_names]
    if missing:
        raise SchemaValidationError(f"adapter: source is missing joints {missing}")

    source_lookup = {name: index for index, name in enumerate(source_names)}
    reorder = [source_lookup[name] for name in BODY_JOINT_NAMES]

    raw_wxyz = np.asarray(raw["pred_quat_wxyz"])[:, reorder]
    canonical_xyzw = raw_wxyz[..., [1, 2, 3, 0]]

    arrays = {name: value.copy() for name, value in packet_template.items()}
    arrays["timestamp"] = np.asarray(raw["frame_time_ms"], dtype=np.float64) / 1000.0
    arrays["body_position"] = (
        np.asarray(raw["pred_xyz_mm"], dtype=np.float32)[:, reorder] / 1000.0
    )
    arrays["body_quaternion_xyzw"] = canonical_xyzw.astype(np.float32)
    arrays["body_confidence"] = np.asarray(raw["score"], dtype=np.float32)[:, reorder]
    arrays["body_valid"] = np.asarray(raw["observed"], dtype=bool)[:, reorder]

    metadata = dict(metadata_template)
    metadata["adapter_source"] = {
        "name": "mock_body_pose_model",
        "source_position_unit": "mm",
        "source_time_unit": "ms",
        "source_quaternion_order": "wxyz",
        "source_joint_names": source_names,
    }
    return arrays, metadata


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    output_dir = phase_root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    raw, reference_arrays, reference_metadata = make_mock_model_output()
    adapted_arrays, adapted_metadata = adapt_body_model_output(
        raw, reference_arrays, reference_metadata
    )
    validate_packet(adapted_arrays, adapted_metadata)

    position_error = float(
        np.max(np.abs(adapted_arrays["body_position"] - reference_arrays["body_position"]))
    )
    quaternion_component_error = float(
        np.max(
            np.abs(
                adapted_arrays["body_quaternion_xyzw"]
                - reference_arrays["body_quaternion_xyzw"]
            )
        )
    )
    timestamp_error = float(
        np.max(np.abs(adapted_arrays["timestamp"] - reference_arrays["timestamp"]))
    )

    print("Unit 1 part 3 - model adapter to canonical schema")
    print("\nSource contract")
    print("position / time unit       = mm / ms")
    print("quaternion order           = wxyz")
    print(f"joint order                = {list(raw['joint_labels'])}")
    print("\nCanonical contract")
    print("position / time unit       = m / s")
    print("quaternion order           = xyzw")
    print(f"joint order                = {list(BODY_JOINT_NAMES)}")
    print("\nAdapter verification")
    print("canonical validator        = PASS")
    print(f"max position error         = {position_error:.3e} m")
    print(f"max quaternion comp. error = {quaternion_component_error:.3e}")
    print(f"max timestamp error        = {timestamp_error:.3e} s")

    missing_joint_result: dict[str, str]
    bad_raw = dict(raw)
    bad_raw["joint_labels"] = list(raw["joint_labels"])[:-1]
    for field in ("pred_xyz_mm", "pred_quat_wxyz", "score", "observed"):
        bad_raw[field] = np.asarray(raw[field])[:, :-1]
    try:
        adapt_body_model_output(bad_raw, reference_arrays, reference_metadata)
    except SchemaValidationError as error:
        missing_joint_result = {"result": "REJECTED", "reason": str(error)}
        print(f"missing source joint       = REJECTED: {error}")
    else:
        missing_joint_result = {"result": "MISSED"}
        print("missing source joint       = MISSED")

    report = {
        "canonical_validation": "PASS",
        "max_position_error_m": position_error,
        "max_quaternion_component_error": quaternion_component_error,
        "max_timestamp_error_s": timestamp_error,
        "missing_joint_case": missing_joint_result,
    }
    report_path = output_dir / "unit01_adapter_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nSaved report to: {report_path}")


if __name__ == "__main__":
    main()

