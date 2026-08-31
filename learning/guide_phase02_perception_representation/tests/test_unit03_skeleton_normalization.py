from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from unit03_skeleton_graph import build_edge_index  # noqa: E402
from unit03_skeleton_normalization import (  # noqa: E402
    normalize_skeleton,
    run_normalization_experiment,
)


def test_normalization_removes_translation_and_uniform_scale() -> None:
    _arrays, metrics = run_normalization_experiment()
    assert metrics["max_translation_scale_invariance_error"] < 1e-12
    assert metrics["observed_scale_ratio"] == pytest.approx(1.6)


def test_normalization_is_reconstructable_with_metadata() -> None:
    _arrays, metrics = run_normalization_experiment()
    assert metrics["max_reconstruction_error_m"] < 1e-12
    assert metrics["max_normalized_center_norm"] < 1e-12
    assert metrics["mean_normalized_bone_length"] == pytest.approx(1.0)


def test_degenerate_skeleton_scale_is_rejected() -> None:
    collapsed = np.zeros((2, 6, 3))
    with pytest.raises(ValueError, match="scale"):
        normalize_skeleton(collapsed, build_edge_index())

