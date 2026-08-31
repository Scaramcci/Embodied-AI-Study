"""Unit 3, part 1: construct an upper-body skeleton graph and its features."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np

from unit01_schema_contract import BODY_JOINT_NAMES, make_synthetic_packet


EDGE_NAMES = (
    ("left_shoulder", "left_elbow"),
    ("left_elbow", "left_wrist"),
    ("right_shoulder", "right_elbow"),
    ("right_elbow", "right_wrist"),
)


def build_edge_index(joint_names: tuple[str, ...] = BODY_JOINT_NAMES) -> np.ndarray:
    """Return directed parent-to-child graph edges with shape [2,E]."""
    lookup = {name: index for index, name in enumerate(joint_names)}
    missing = sorted({name for edge in EDGE_NAMES for name in edge} - lookup.keys())
    if missing:
        raise ValueError(f"cannot build skeleton; missing joints {missing}")
    return np.array(
        [[lookup[parent], lookup[child]] for parent, child in EDGE_NAMES],
        dtype=np.int64,
    ).T


def build_skeleton_features(
    positions: np.ndarray,
    quaternions_xyzw: np.ndarray,
    edge_index: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return node features, directed edge vectors, and edge lengths."""
    if positions.shape[:-1] != quaternions_xyzw.shape[:-1]:
        raise ValueError("positions and quaternions must share [T,J] dimensions")
    if positions.shape[-1] != 3 or quaternions_xyzw.shape[-1] != 4:
        raise ValueError("expected position [...,3] and quaternion [...,4]")
    if edge_index.ndim != 2 or edge_index.shape[0] != 2:
        raise ValueError(f"edge_index must have shape [2,E], got {edge_index.shape}")

    parent = edge_index[0]
    child = edge_index[1]
    node_features = np.concatenate((positions, quaternions_xyzw), axis=-1)
    edge_vectors = positions[:, child, :] - positions[:, parent, :]
    edge_lengths = np.linalg.norm(edge_vectors, axis=-1)
    return node_features, edge_vectors, edge_lengths


def run_graph_experiment() -> tuple[dict[str, np.ndarray], dict[str, float]]:
    packet, _metadata = make_synthetic_packet()
    positions = packet["body_position"].astype(np.float64)
    quaternions = packet["body_quaternion_xyzw"].astype(np.float64)
    edge_index = build_edge_index()
    node_features, edge_vectors, edge_lengths = build_skeleton_features(
        positions, quaternions, edge_index
    )

    translation = np.array([1.0, -0.5, 0.2])
    translated_positions = positions + translation
    _, translated_edge_vectors, translated_edge_lengths = build_skeleton_features(
        translated_positions, quaternions, edge_index
    )

    metrics = {
        "max_edge_vector_translation_error_m": float(
            np.max(np.abs(translated_edge_vectors - edge_vectors))
        ),
        "max_bone_length_translation_error_m": float(
            np.max(np.abs(translated_edge_lengths - edge_lengths))
        ),
        "max_bone_length_temporal_change_m": float(
            np.max(np.abs(edge_lengths - edge_lengths[0]))
        ),
    }
    arrays = {
        "positions": positions,
        "quaternions_xyzw": quaternions,
        "node_features": node_features,
        "edge_index": edge_index,
        "edge_vectors": edge_vectors,
        "edge_lengths": edge_lengths,
        "translated_positions": translated_positions,
    }
    return arrays, metrics


def save_outputs(
    phase_root: Path, arrays: dict[str, np.ndarray], metrics: dict[str, float]
) -> None:
    output_dir = phase_root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    array_path = output_dir / "unit03_skeleton_graph.npz"
    report_path = output_dir / "unit03_skeleton_graph.json"
    figure_path = output_dir / "unit03_skeleton_graph.png"

    np.savez_compressed(array_path, **arrays)
    report_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    positions = arrays["positions"][0]
    edge_index = arrays["edge_index"]
    figure = plt.figure(figsize=(7, 6), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    colors = ["tab:blue"] * 3 + ["tab:orange"] * 3
    axis.scatter(
        positions[:, 0], positions[:, 1], positions[:, 2], c=colors, s=55
    )
    for joint_index, name in enumerate(BODY_JOINT_NAMES):
        axis.text(*positions[joint_index], name, fontsize=8)
    for parent, child in edge_index.T:
        segment = positions[[parent, child]]
        axis.plot(segment[:, 0], segment[:, 1], segment[:, 2], color="black")
    axis.set_title("Upper-body skeleton graph, frame 0")
    axis.set_xlabel("world x [m]")
    axis.set_ylabel("world y [m]")
    axis.set_zlabel("world z [m]")
    axis.view_init(elev=18, azim=-70)
    figure.savefig(figure_path, dpi=160)
    plt.close(figure)

    print(f"\nSaved graph arrays to: {array_path}")
    print(f"Saved report       to: {report_path}")
    print(f"Saved figure       to: {figure_path}")


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    arrays, metrics = run_graph_experiment()
    np.set_printoptions(precision=5, suppress=True)

    print("Unit 3 part 1 - upper-body skeleton graph")
    print(f"joint names          = {list(BODY_JOINT_NAMES)}")
    print(f"edge names           = {list(EDGE_NAMES)}")
    print(f"positions shape      = {arrays['positions'].shape}  [T,J,xyz]")
    print(f"quaternions shape    = {arrays['quaternions_xyzw'].shape}  [T,J,xyzw]")
    print(f"node features shape  = {arrays['node_features'].shape}  [T,J,7]")
    print(f"edge_index shape     = {arrays['edge_index'].shape}  [2,E]")
    print(f"edge vectors shape   = {arrays['edge_vectors'].shape}  [T,E,xyz]")
    print("\nedge_index =")
    print(arrays["edge_index"])
    print("frame 0 edge lengths [m] =")
    print(arrays["edge_lengths"][0])
    print("\nTranslation invariance checks")
    print(
        "max edge-vector change = "
        f"{metrics['max_edge_vector_translation_error_m']:.3e} m"
    )
    print(
        "max bone-length change = "
        f"{metrics['max_bone_length_translation_error_m']:.3e} m"
    )
    print(
        "max temporal bone-length change = "
        f"{metrics['max_bone_length_temporal_change_m']:.3e} m"
    )
    save_outputs(phase_root, arrays, metrics)


if __name__ == "__main__":
    main()

