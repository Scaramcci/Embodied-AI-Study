"""Numerical evidence for the planar two-link FK lesson."""

from pathlib import Path
import sys

import numpy as np
import pytest


MODULE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_ROOT / "src"))

from f2_kinematics import forward_kinematics  # noqa: E402


def test_straight_arm_lies_on_positive_x_axis() -> None:
    points = forward_kinematics(q=[0.0, 0.0], link_lengths=[1.0, 0.5])

    expected = np.array([[0.0, 0.0], [1.0, 0.0], [1.5, 0.0]])
    np.testing.assert_allclose(points, expected, atol=1e-12)


def test_elbow_angle_is_relative_to_upper_arm() -> None:
    points = forward_kinematics(
        q=np.deg2rad([90.0, -90.0]),
        link_lengths=[1.0, 1.0],
    )

    expected = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    np.testing.assert_allclose(points, expected, atol=1e-12)


def test_rejects_non_positive_link_length() -> None:
    with pytest.raises(ValueError, match="positive"):
        forward_kinematics(q=[0.0, 0.0], link_lengths=[1.0, 0.0])


def test_rejects_wrong_joint_shape() -> None:
    with pytest.raises(ValueError, match="shape"):
        forward_kinematics(q=[0.0], link_lengths=[1.0, 1.0])

