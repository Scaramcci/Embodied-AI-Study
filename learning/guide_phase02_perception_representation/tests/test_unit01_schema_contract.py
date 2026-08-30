from __future__ import annotations

import copy
import sys
from pathlib import Path

import numpy as np
import pytest


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from unit01_schema_contract import (  # noqa: E402
    SchemaValidationError,
    build_failure_cases,
    make_synthetic_packet,
    validate_packet,
)
from unit01_validity_and_numeric_checks import (  # noqa: E402
    build_numeric_failure_cases,
    make_packet_with_one_missing_joint,
)
from unit01_adapter_pipeline import (  # noqa: E402
    adapt_body_model_output,
    make_mock_model_output,
)


def test_valid_packet_passes() -> None:
    arrays, metadata = make_synthetic_packet()
    validate_packet(arrays, metadata)


@pytest.mark.parametrize("case_name", list(build_failure_cases()))
def test_contract_violation_is_rejected(case_name: str) -> None:
    arrays, metadata = make_synthetic_packet()
    bad_arrays = {name: value.copy() for name, value in arrays.items()}
    bad_metadata = copy.deepcopy(metadata)
    build_failure_cases()[case_name](bad_arrays, bad_metadata)

    with pytest.raises(SchemaValidationError):
        validate_packet(bad_arrays, bad_metadata)


def test_explicitly_masked_nan_is_accepted() -> None:
    arrays, metadata = make_packet_with_one_missing_joint()
    validate_packet(arrays, metadata)


@pytest.mark.parametrize("case_name", list(build_numeric_failure_cases()))
def test_numeric_violation_is_rejected(case_name: str) -> None:
    arrays, metadata = make_synthetic_packet()
    bad_arrays = {name: value.copy() for name, value in arrays.items()}
    bad_metadata = copy.deepcopy(metadata)
    build_numeric_failure_cases()[case_name](bad_arrays, bad_metadata)

    with pytest.raises(SchemaValidationError):
        validate_packet(bad_arrays, bad_metadata)


def test_model_adapter_recovers_canonical_packet() -> None:
    raw, reference_arrays, reference_metadata = make_mock_model_output()
    arrays, metadata = adapt_body_model_output(
        raw, reference_arrays, reference_metadata
    )

    validate_packet(arrays, metadata)
    assert np.allclose(arrays["timestamp"], reference_arrays["timestamp"])
    assert np.allclose(arrays["body_position"], reference_arrays["body_position"])
    assert np.allclose(
        arrays["body_quaternion_xyzw"],
        reference_arrays["body_quaternion_xyzw"],
    )


def test_model_adapter_rejects_missing_joint() -> None:
    raw, reference_arrays, reference_metadata = make_mock_model_output()
    raw["joint_labels"] = list(raw["joint_labels"])[:-1]
    for field in ("pred_xyz_mm", "pred_quat_wxyz", "score", "observed"):
        raw[field] = np.asarray(raw[field])[:, :-1]

    with pytest.raises(SchemaValidationError, match="missing joints"):
        adapt_body_model_output(raw, reference_arrays, reference_metadata)
