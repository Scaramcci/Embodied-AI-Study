"""Forward kinematics for a planar two-link arm."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray


def forward_kinematics(
    q: ArrayLike,
    link_lengths: ArrayLike,
) -> NDArray[np.float64]:
    """Return shoulder, elbow, and wrist positions in the base frame.

    Args:
        q: Joint configuration ``[theta_1, theta_2]`` in radians. ``theta_2``
            is the forearm angle relative to the upper arm.
        link_lengths: Positive lengths ``[l_1, l_2]`` in one consistent unit.

    Returns:
        A float array with shape ``(3, 2)``. Rows are shoulder, elbow, and
        wrist; columns are x and y coordinates in the base frame.
    """
    angles = np.asarray(q, dtype=float)
    lengths = np.asarray(link_lengths, dtype=float)

    if angles.shape != (2,):
        raise ValueError(f"q must have shape (2,), got {angles.shape}")
    if lengths.shape != (2,):
        raise ValueError(
            f"link_lengths must have shape (2,), got {lengths.shape}"
        )
    if not np.all(np.isfinite(angles)) or not np.all(np.isfinite(lengths)):
        raise ValueError("q and link_lengths must contain only finite values")
    if np.any(lengths <= 0.0):
        raise ValueError("link lengths must be positive")

    theta_1, theta_2 = angles
    l_1, l_2 = lengths

    shoulder = np.array([0.0, 0.0])
    elbow = np.array([l_1 * np.cos(theta_1), l_1 * np.sin(theta_1)])

    forearm_angle = theta_1 + theta_2
    wrist = elbow + np.array(
        [l_2 * np.cos(forearm_angle), l_2 * np.sin(forearm_angle)]
    )

    return np.stack([shoulder, elbow, wrist])

