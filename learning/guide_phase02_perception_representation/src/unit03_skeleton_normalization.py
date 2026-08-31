"""Unit 3, part 2: center and scale-normalize an upper-body skeleton."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np

from unit01_schema_contract import BODY_JOINT_NAMES, make_synthetic_packet
from unit03_skeleton_graph import build_edge_index


def normalize_skeleton(
    positions: np.ndarray, edge_index: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Remove per-frame geometric center and mean bone-length scale."""
    positions = np.asarray(positions, dtype=np.float64)
    if positions.ndim != 3 or positions.shape[-1] != 3:
        raise ValueError(f"positions must have shape [T,J,3], got {positions.shape}")

    center = np.mean(positions, axis=1)
    parent, child = edge_index
    edge_vectors = positions[:, child] - positions[:, parent]
    edge_lengths = np.linalg.norm(edge_vectors, axis=-1)
    scale = np.mean(edge_lengths, axis=1)
    if not np.all(scale > 1e-8):
        raise ValueError("skeleton scale is zero or too small")

    normalized = (positions - center[:, None, :]) / scale[:, None, None]
    return normalized, center, scale


def denormalize_skeleton(
    normalized: np.ndarray, center: np.ndarray, scale: np.ndarray
) -> np.ndarray:
    """Restore metric positions when center and scale metadata are retained."""
    return normalized * scale[:, None, None] + center[:, None, :]


def run_normalization_experiment() -> tuple[dict[str, np.ndarray], dict[str, float]]:
    packet, _metadata = make_synthetic_packet()
    positions = packet["body_position"].astype(np.float64)
    edge_index = build_edge_index()

    normalized, center, scale = normalize_skeleton(positions, edge_index)
    reconstructed = denormalize_skeleton(normalized, center, scale)

    size_factor = 1.6
    translation = np.array([0.8, -0.4, 0.25])
    transformed = size_factor * positions + translation
    normalized_transformed, transformed_center, transformed_scale = normalize_skeleton(
        transformed, edge_index
    )

    parent, child = edge_index
    normalized_edge_lengths = np.linalg.norm(
        normalized[:, child] - normalized[:, parent], axis=-1
    )
    metrics = {
        "max_normalized_center_norm": float(
            np.max(np.linalg.norm(np.mean(normalized, axis=1), axis=1))
        ),
        "mean_normalized_bone_length": float(np.mean(normalized_edge_lengths)),
        "max_translation_scale_invariance_error": float(
            np.max(np.abs(normalized_transformed - normalized))
        ),
        "max_reconstruction_error_m": float(
            np.max(np.linalg.norm(reconstructed - positions, axis=-1))
        ),
        "observed_scale_ratio": float(np.mean(transformed_scale / scale)),
    }
    arrays = {
        "positions": positions,
        "normalized": normalized,
        "center": center,
        "scale": scale,
        "transformed_positions": transformed,
        "transformed_center": transformed_center,
        "transformed_scale": transformed_scale,
        "normalized_transformed": normalized_transformed,
        "edge_index": edge_index,
    }
    return arrays, metrics


def draw_skeleton(axis: plt.Axes, positions: np.ndarray, edge_index: np.ndarray) -> None:
    colors = ["tab:blue"] * 3 + ["tab:orange"] * 3
    axis.scatter(positions[:, 0], positions[:, 1], positions[:, 2], c=colors, s=35)
    for parent, child in edge_index.T:
        segment = positions[[parent, child]]
        axis.plot(segment[:, 0], segment[:, 1], segment[:, 2], color="black")


def save_outputs(
    phase_root: Path, arrays: dict[str, np.ndarray], metrics: dict[str, float]
) -> None:
    output_dir = phase_root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    array_path = output_dir / "unit03_skeleton_normalization.npz"
    report_path = output_dir / "unit03_skeleton_normalization.json"
    figure_path = output_dir / "unit03_skeleton_normalization.png"
    np.savez_compressed(array_path, **arrays)
    report_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    figure = plt.figure(figsize=(12, 4.3), constrained_layout=True)
    titles_and_points = (
        ("Original metric skeleton", arrays["positions"][0]),
        ("Translated and 1.6x larger", arrays["transformed_positions"][0]),
        ("Normalized skeletons overlap", arrays["normalized"][0]),
    )
    for index, (title, points) in enumerate(titles_and_points, start=1):
        axis = figure.add_subplot(1, 3, index, projection="3d")
        draw_skeleton(axis, points, arrays["edge_index"])
        if index == 3:
            draw_skeleton(
                axis, arrays["normalized_transformed"][0], arrays["edge_index"]
            )
        axis.set_title(title)
        axis.set_xlabel("x")
        axis.set_ylabel("y")
        axis.set_zlabel("z")
        axis.view_init(elev=18, azim=-70)
    figure.savefig(figure_path, dpi=160)
    plt.close(figure)

    print(f"\nSaved arrays to: {array_path}")
    print(f"Saved report to: {report_path}")
    print(f"Saved figure to: {figure_path}")


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    arrays, metrics = run_normalization_experiment()
    np.set_printoptions(precision=6, suppress=True)

    print("Unit 3 part 2 - skeleton centering and scale normalization")
    print(f"joint names                     = {list(BODY_JOINT_NAMES)}")
    print(f"frame 0 center [m]              = {arrays['center'][0]}")
    print(f"frame 0 scale [m]               = {arrays['scale'][0]:.6f}")
    print(f"normalized positions shape      = {arrays['normalized'].shape}")
    print("\nNormalization checks")
    print(
        "max normalized center norm      = "
        f"{metrics['max_normalized_center_norm']:.3e}"
    )
    print(
        "mean normalized bone length     = "
        f"{metrics['mean_normalized_bone_length']:.6f}"
    )
    print(
        "observed transformed scale ratio = "
        f"{metrics['observed_scale_ratio']:.6f}"
    )
    print(
        "max normalized overlap error    = "
        f"{metrics['max_translation_scale_invariance_error']:.3e}"
    )
    print(
        "max metric reconstruction error = "
        f"{metrics['max_reconstruction_error_m']:.3e} m"
    )
    print("\nNormalization removes absolute translation and uniform body scale.")
    print("Keep center and scale metadata if metric positions must be reconstructed.")
    save_outputs(phase_root, arrays, metrics)


if __name__ == "__main__":
    main()

