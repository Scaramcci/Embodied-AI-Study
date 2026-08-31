"""Phase 4 P4-1: contact regions and local polyhedral hand-object geometry."""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np


FINGER_NAMES = ("thumb", "index", "middle", "ring", "little")
ADJACENT_FINGER = np.array([1, 2, 3, 4, 3])
CONTACT_RADIUS_M = 0.012
EDGE_PAIRS = tuple(combinations(range(4), 2))


def make_box_surface_points(samples_per_axis: int = 31) -> np.ndarray:
    half_extents = np.array([0.06, 0.04, 0.10])
    faces: list[np.ndarray] = []
    for fixed_axis in range(3):
        free_axes = [axis for axis in range(3) if axis != fixed_axis]
        grid_a = np.linspace(
            -half_extents[free_axes[0]],
            half_extents[free_axes[0]],
            samples_per_axis,
        )
        grid_b = np.linspace(
            -half_extents[free_axes[1]],
            half_extents[free_axes[1]],
            samples_per_axis,
        )
        mesh_a, mesh_b = np.meshgrid(grid_a, grid_b)
        for sign in (-1.0, 1.0):
            face = np.zeros((samples_per_axis**2, 3), dtype=np.float64)
            face[:, fixed_axis] = sign * half_extents[fixed_axis]
            face[:, free_axes[0]] = mesh_a.ravel()
            face[:, free_axes[1]] = mesh_b.ravel()
            faces.append(face)
    return np.concatenate(faces, axis=0)


def make_hand_keypoints() -> tuple[np.ndarray, np.ndarray]:
    palm = np.array([-0.14, 0.0, 0.0])
    fingertips = np.array(
        [
            [-0.063, -0.030, -0.040],
            [-0.063, -0.014, 0.020],
            [-0.063, 0.000, 0.060],
            [-0.063, 0.014, 0.040],
            [-0.063, 0.030, 0.000],
        ]
    )
    return palm, fingertips


def extract_contact_regions(
    fingertips: np.ndarray, object_cloud: np.ndarray
) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    regions: list[np.ndarray] = []
    centroids = np.empty_like(fingertips)
    nearest_points = np.empty_like(fingertips)
    for finger, fingertip in enumerate(fingertips):
        distances = np.linalg.norm(object_cloud - fingertip, axis=1)
        mask = distances <= CONTACT_RADIUS_M
        if not np.any(mask):
            raise ValueError(f"finger {finger} has no object points in contact radius")
        regions.append(np.flatnonzero(mask))
        centroids[finger] = np.mean(object_cloud[mask], axis=0)
        nearest_points[finger] = object_cloud[np.argmin(distances)]
    return regions, centroids, nearest_points


def build_polyhedral_units(
    palm: np.ndarray, fingertips: np.ndarray, contacts: np.ndarray
) -> np.ndarray:
    units = np.empty((len(fingertips), 4, 3), dtype=np.float64)
    for finger in range(len(fingertips)):
        units[finger] = np.vstack(
            (
                palm,
                fingertips[finger],
                fingertips[ADJACENT_FINGER[finger]],
                contacts[finger],
            )
        )
    return units


def geometry_descriptors(
    units_world: np.ndarray,
    palm_world: np.ndarray,
    contacts_world: np.ndarray,
    world_R_hand: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    edge_vectors_world = np.stack(
        [units_world[:, i] - units_world[:, j] for i, j in EDGE_PAIRS], axis=1
    )
    edge_lengths = np.linalg.norm(edge_vectors_world, axis=2)
    edge_vectors_hand = edge_vectors_world @ world_R_hand
    contact_in_hand = (contacts_world - palm_world) @ world_R_hand
    return edge_lengths, edge_vectors_world, edge_vectors_hand, contact_in_hand


def make_rigid_transform() -> tuple[np.ndarray, np.ndarray]:
    yaw = np.deg2rad(38.0)
    pitch = np.deg2rad(-22.0)
    rotation_z = np.array(
        [
            [np.cos(yaw), -np.sin(yaw), 0.0],
            [np.sin(yaw), np.cos(yaw), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    rotation_y = np.array(
        [
            [np.cos(pitch), 0.0, np.sin(pitch)],
            [0.0, 1.0, 0.0],
            [-np.sin(pitch), 0.0, np.cos(pitch)],
        ]
    )
    return rotation_z @ rotation_y, np.array([0.45, 0.10, 0.86])


def transform_points(points: np.ndarray, rotation: np.ndarray, translation: np.ndarray) -> np.ndarray:
    return points @ rotation.T + translation


def descriptor_rmse(reference: np.ndarray, candidate: np.ndarray) -> float:
    return float(np.sqrt(np.mean((candidate - reference) ** 2)))


def run_polyhedral_experiment() -> tuple[dict[str, np.ndarray], dict[str, object]]:
    object_cloud = make_box_surface_points()
    palm, fingertips = make_hand_keypoints()
    regions, contacts, nearest_points = extract_contact_regions(
        fingertips, object_cloud
    )
    units = build_polyhedral_units(palm, fingertips, contacts)
    identity = np.eye(3)
    edge_lengths, edge_world, edge_hand, contact_hand = geometry_descriptors(
        units, palm, contacts, identity
    )

    rotation, translation = make_rigid_transform()
    moved_cloud = transform_points(object_cloud, rotation, translation)
    moved_palm = transform_points(palm[None, :], rotation, translation)[0]
    moved_fingertips = transform_points(fingertips, rotation, translation)
    moved_contacts = transform_points(contacts, rotation, translation)
    moved_units = build_polyhedral_units(moved_palm, moved_fingertips, moved_contacts)
    moved_lengths, moved_edge_world, moved_edge_hand, moved_contact_hand = (
        geometry_descriptors(
            moved_units, moved_palm, moved_contacts, rotation
        )
    )

    distorted_fingertips = moved_fingertips.copy()
    distorted_contacts = moved_contacts.copy()
    distorted_fingertips[2] += np.array([0.014, -0.009, 0.006])
    distorted_contacts[1] += np.array([-0.006, 0.012, 0.008])
    distorted_units = build_polyhedral_units(
        moved_palm, distorted_fingertips, distorted_contacts
    )
    distorted_lengths, _, distorted_edge_hand, distorted_contact_hand = (
        geometry_descriptors(
            distorted_units, moved_palm, distorted_contacts, rotation
        )
    )

    contact_region_count = np.array([len(region) for region in regions])
    metrics: dict[str, object] = {
        "finger_names": list(FINGER_NAMES),
        "contact_radius_m": CONTACT_RADIUS_M,
        "contact_region_point_count": contact_region_count.tolist(),
        "nearest_point_distance_m": np.linalg.norm(
            fingertips - nearest_points, axis=1
        ).tolist(),
        "centroid_distance_m": np.linalg.norm(fingertips - contacts, axis=1).tolist(),
        "rigid_absolute_world_displacement_m": float(
            np.max(np.linalg.norm(moved_units - units, axis=2))
        ),
        "rigid_edge_length_change_m": float(
            np.max(np.abs(moved_lengths - edge_lengths))
        ),
        "rigid_world_edge_vector_change_m": float(
            np.max(np.linalg.norm(moved_edge_world - edge_world, axis=2))
        ),
        "rigid_hand_local_edge_change_m": float(
            np.max(np.linalg.norm(moved_edge_hand - edge_hand, axis=2))
        ),
        "rigid_hand_local_contact_change_m": float(
            np.max(np.linalg.norm(moved_contact_hand - contact_hand, axis=1))
        ),
        "distorted_edge_length_rmse_m": descriptor_rmse(
            edge_lengths, distorted_lengths
        ),
        "distorted_hand_local_edge_rmse_m": descriptor_rmse(
            edge_hand, distorted_edge_hand
        ),
        "distorted_hand_local_contact_rmse_m": descriptor_rmse(
            contact_hand, distorted_contact_hand
        ),
    }
    arrays = {
        "object_cloud": object_cloud,
        "palm": palm,
        "fingertips": fingertips,
        "contact_points": contacts,
        "nearest_points": nearest_points,
        "polyhedral_units": units,
        "edge_lengths": edge_lengths,
        "edge_vectors_hand": edge_hand,
        "contact_points_hand": contact_hand,
        "rigid_rotation": rotation,
        "rigid_translation": translation,
        "moved_object_cloud": moved_cloud,
        "moved_palm": moved_palm,
        "moved_fingertips": moved_fingertips,
        "moved_contact_points": moved_contacts,
        "moved_polyhedral_units": moved_units,
        "distorted_fingertips": distorted_fingertips,
        "distorted_contact_points": distorted_contacts,
        "distorted_polyhedral_units": distorted_units,
        "contact_region_offsets": np.cumsum(
            np.concatenate(([0], contact_region_count))
        ),
        "contact_region_indices": np.concatenate(regions),
    }
    return arrays, metrics


def draw_unit_edges(axis: plt.Axes, unit: np.ndarray, color: str, alpha: float = 1.0) -> None:
    for i, j in EDGE_PAIRS:
        axis.plot(
            [unit[i, 0], unit[j, 0]],
            [unit[i, 1], unit[j, 1]],
            [unit[i, 2], unit[j, 2]],
            color=color,
            alpha=alpha,
            linewidth=1.1,
        )


def save_outputs(
    phase_root: Path, arrays: dict[str, np.ndarray], metrics: dict[str, object]
) -> None:
    data_dir = phase_root / "data"
    output_dir = phase_root / "outputs"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_path = data_dir / "p4a_polyhedral_contact_geometry.npz"
    report_path = output_dir / "p4a_polyhedral_contact_geometry.json"
    figure_path = output_dir / "p4a_polyhedral_contact_geometry.png"
    np.savez_compressed(data_path, **arrays)
    report_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    figure = plt.figure(figsize=(15, 5), constrained_layout=True)
    original_axis = figure.add_subplot(1, 3, 1, projection="3d")
    original_axis.scatter(*arrays["object_cloud"].T, s=2, alpha=0.12, label="object cloud")
    original_axis.scatter(*arrays["fingertips"].T, c="tab:red", s=45, label="fingertips")
    original_axis.scatter(*arrays["palm"], c="black", s=55, marker="s", label="palm")
    original_axis.scatter(
        *arrays["contact_points"].T,
        c="tab:green",
        s=55,
        marker="x",
        label="region centroids",
    )
    for finger, name in enumerate(FINGER_NAMES):
        original_axis.text(*arrays["fingertips"][finger], name, fontsize=7)
    draw_unit_edges(original_axis, arrays["polyhedral_units"][2], "tab:purple")
    original_axis.set_title("Contact regions and one tetrahedral unit")
    original_axis.set_xlabel("object x [m]")
    original_axis.set_ylabel("object y [m]")
    original_axis.set_zlabel("object z [m]")
    original_axis.legend(fontsize=7)

    moved_axis = figure.add_subplot(1, 3, 2, projection="3d")
    moved_axis.scatter(
        *arrays["moved_object_cloud"].T, s=2, alpha=0.08, label="rigid-moved object"
    )
    draw_unit_edges(moved_axis, arrays["moved_polyhedral_units"][2], "tab:blue")
    draw_unit_edges(
        moved_axis, arrays["distorted_polyhedral_units"][2], "tab:red", alpha=0.8
    )
    moved_axis.scatter(
        *arrays["moved_polyhedral_units"][2].T,
        c="tab:blue",
        s=35,
        label="rigid-equivalent unit",
    )
    moved_axis.scatter(
        *arrays["distorted_polyhedral_units"][2].T,
        c="tab:red",
        s=25,
        marker="x",
        label="locally distorted unit",
    )
    moved_axis.set_title("Rigid motion versus local distortion")
    moved_axis.set_xlabel("world x [m]")
    moved_axis.set_ylabel("world y [m]")
    moved_axis.set_zlabel("world z [m]")
    moved_axis.legend(fontsize=7)

    metric_axis = figure.add_subplot(1, 3, 3)
    labels = ["edge length", "local edge", "local contact"]
    invariant_mm = 1000.0 * np.array(
        [
            metrics["rigid_edge_length_change_m"],
            metrics["rigid_hand_local_edge_change_m"],
            metrics["rigid_hand_local_contact_change_m"],
        ]
    )
    distorted_mm = 1000.0 * np.array(
        [
            metrics["distorted_edge_length_rmse_m"],
            metrics["distorted_hand_local_edge_rmse_m"],
            metrics["distorted_hand_local_contact_rmse_m"],
        ]
    )
    positions = np.arange(len(labels))
    metric_axis.bar(positions - 0.18, invariant_mm, width=0.36, label="global rigid move")
    metric_axis.bar(positions + 0.18, distorted_mm, width=0.36, label="local distortion")
    metric_axis.set_xticks(positions, labels, rotation=15)
    metric_axis.set_ylabel("descriptor change [mm or mm RMSE]")
    metric_axis.set_title("Desired invariance and distortion sensitivity")
    metric_axis.legend(fontsize=8)
    metric_axis.grid(axis="y", alpha=0.25)
    figure.savefig(figure_path, dpi=160)
    plt.close(figure)

    print(f"\nSaved data   to: {data_path}")
    print(f"Saved report to: {report_path}")
    print(f"Saved figure to: {figure_path}")


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    arrays, metrics = run_polyhedral_experiment()
    print("Phase 4 P4-1 - contact regions and polyhedral contact geometry")
    print(f"fingers / polyhedral units       = {len(FINGER_NAMES)} / {len(FINGER_NAMES)}")
    print(f"contact region radius            = {1000.0 * metrics['contact_radius_m']:.1f} mm")
    print(f"region point counts              = {metrics['contact_region_point_count']}")
    print(
        "nearest-point distances [mm]    = "
        f"{np.round(1000.0 * np.array(metrics['nearest_point_distance_m']), 4)}"
    )
    print(
        "centroid distances [mm]         = "
        f"{np.round(1000.0 * np.array(metrics['centroid_distance_m']), 4)}"
    )
    print("\nSame hand-object configuration after a global rigid transform")
    print(
        f"absolute world-coordinate change = "
        f"{metrics['rigid_absolute_world_displacement_m']:.6f} m"
    )
    print(
        f"edge-length change               = "
        f"{metrics['rigid_edge_length_change_m']:.3e} m"
    )
    print(
        f"raw world edge-vector change     = "
        f"{metrics['rigid_world_edge_vector_change_m']:.6f} m"
    )
    print(
        f"hand-local edge-vector change    = "
        f"{metrics['rigid_hand_local_edge_change_m']:.3e} m"
    )
    print(
        f"hand-local contact-pose change   = "
        f"{metrics['rigid_hand_local_contact_change_m']:.3e} m"
    )
    print("\nDeliberate local geometry distortion")
    print(
        f"edge-length RMSE                  = "
        f"{1000.0 * metrics['distorted_edge_length_rmse_m']:.4f} mm"
    )
    print(
        f"hand-local edge-vector RMSE       = "
        f"{1000.0 * metrics['distorted_hand_local_edge_rmse_m']:.4f} mm"
    )
    print(
        f"hand-local contact-pose RMSE      = "
        f"{1000.0 * metrics['distorted_hand_local_contact_rmse_m']:.4f} mm"
    )
    print("\nGlobal motion should not change contact semantics; local distortion should.")
    print("Raw world-frame edge vectors are not rotation invariant unless frames are aligned.")
    save_outputs(phase_root, arrays, metrics)


if __name__ == "__main__":
    main()

