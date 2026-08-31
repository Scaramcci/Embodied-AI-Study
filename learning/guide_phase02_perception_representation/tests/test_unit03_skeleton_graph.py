from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from unit03_skeleton_graph import (  # noqa: E402
    build_edge_index,
    build_skeleton_features,
    run_graph_experiment,
)


def test_edge_index_matches_two_arm_chains() -> None:
    expected = np.array([[0, 1, 3, 4], [1, 2, 4, 5]])
    assert np.array_equal(build_edge_index(), expected)


def test_edge_vectors_are_child_minus_parent() -> None:
    arrays, _metrics = run_graph_experiment()
    parent, child = arrays["edge_index"]
    expected = arrays["positions"][:, child] - arrays["positions"][:, parent]
    assert np.allclose(arrays["edge_vectors"], expected)


def test_edges_are_translation_invariant() -> None:
    arrays, metrics = run_graph_experiment()
    assert metrics["max_edge_vector_translation_error_m"] < 1e-12
    assert metrics["max_bone_length_translation_error_m"] < 1e-12
    assert arrays["node_features"].shape == (10, 6, 7)


def test_feature_builder_rejects_mismatched_joint_count() -> None:
    positions = np.zeros((2, 6, 3))
    quaternions = np.zeros((2, 5, 4))
    try:
        build_skeleton_features(positions, quaternions, build_edge_index())
    except ValueError as error:
        assert "share [T,J]" in str(error)
    else:
        raise AssertionError("mismatched joint dimensions were not rejected")

