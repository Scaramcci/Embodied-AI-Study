"""Unit 1, part 2: distinguish confidence, validity, and numerical failures."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from unit01_schema_contract import (
    SchemaValidationError,
    make_synthetic_packet,
    validate_packet,
)


def make_packet_with_one_missing_joint() -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    arrays, metadata = make_synthetic_packet()
    frame_index = 4
    joint_index = 2  # left_wrist
    arrays["body_valid"][frame_index, joint_index] = False
    arrays["body_confidence"][frame_index, joint_index] = 0.05
    arrays["body_position"][frame_index, joint_index] = np.nan
    arrays["body_quaternion_xyzw"][frame_index, joint_index] = np.nan
    return arrays, metadata


def build_numeric_failure_cases() -> dict[
    str, Callable[[dict[str, np.ndarray], dict[str, Any]], None]
]:
    def nan_but_still_valid(arrays: dict[str, np.ndarray], _metadata: dict[str, Any]) -> None:
        arrays["body_position"][4, 2] = np.nan

    def confidence_out_of_range(
        arrays: dict[str, np.ndarray], _metadata: dict[str, Any]
    ) -> None:
        arrays["body_confidence"][3, 1] = 1.2

    def non_unit_quaternion(
        arrays: dict[str, np.ndarray], _metadata: dict[str, Any]
    ) -> None:
        arrays["body_quaternion_xyzw"][2, 0] = np.array(
            [0.0, 0.0, 0.0, 2.0], dtype=np.float32
        )

    def missing_joint_axis(
        arrays: dict[str, np.ndarray], _metadata: dict[str, Any]
    ) -> None:
        arrays["body_position"] = arrays["body_position"][:, :-1, :]

    return {
        "nan_marked_as_valid": nan_but_still_valid,
        "confidence_above_one": confidence_out_of_range,
        "non_unit_quaternion": non_unit_quaternion,
        "wrong_body_shape": missing_joint_axis,
    }


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    output_dir = phase_root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    missing_arrays, missing_metadata = make_packet_with_one_missing_joint()
    validate_packet(missing_arrays, missing_metadata)

    print("Unit 1 part 2 - confidence, valid mask, and numeric checks")
    print("\nExplicit missing observation")
    print("frame / joint              = 4 / left_wrist")
    print(f"position                   = {missing_arrays['body_position'][4, 2]}")
    print(f"confidence                 = {missing_arrays['body_confidence'][4, 2]:.2f}")
    print(f"valid                      = {missing_arrays['body_valid'][4, 2]}")
    print("masked missing observation = PASS")

    arrays, metadata = make_synthetic_packet()
    report: dict[str, Any] = {
        "explicit_missing_observation": "PASS",
        "failure_cases": {},
    }
    print("\nDeliberate numerical violations")
    for case_name, corrupt in build_numeric_failure_cases().items():
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
            print(f"{case_name:<25} = REJECTED: {error}")
        else:
            report["failure_cases"][case_name] = {"result": "MISSED"}
            print(f"{case_name:<25} = MISSED")

    report_path = output_dir / "unit01_numeric_validation_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nSaved report to: {report_path}")


if __name__ == "__main__":
    main()

