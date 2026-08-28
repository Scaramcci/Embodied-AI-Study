from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from unit01_schema_contract import (  # noqa: E402
    SchemaValidationError,
    build_failure_cases,
    make_synthetic_packet,
    validate_packet,
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

