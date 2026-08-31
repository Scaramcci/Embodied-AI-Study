"""Accelerated Phase 2A: object local/world cloud and six hand keypoints."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
import open3d as o3d


HAND_KEYPOINT_NAMES = (
    "palm",
    "thumb_tip",
    "index_tip",
    "middle_tip",
    "ring_tip",
    "little_tip",
)


def make_box_surface_points(samples_per_axis: int = 12) -> np.ndarray:
    """Create a cuboid surface in the object's own coordinate frame."""
    half_extents = np.array([0.06, 0.04, 0.12])
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


def make_world_t_object() -> np.ndarray:
    """Define the object's 6D pose as a rigid transform in the world frame."""
    yaw = np.deg2rad(35.0)
    pitch = np.deg2rad(-15.0)
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
    transform = np.eye(4)
    transform[:3, :3] = rotation_z @ rotation_y
    transform[:3, 3] = np.array([0.45, 0.10, 0.90])
    return transform


def transform_points(transform: np.ndarray, points: np.ndarray) -> np.ndarray:
    return points @ transform[:3, :3].T + transform[:3, 3]


def make_hand_keypoints_world(world_t_object: np.ndarray) -> np.ndarray:
    """Create palm + fingertips near one side of the object, then express them in world."""
    keypoints_object = np.array(
        [
            [-0.13, 0.000, -0.010],  # palm
            [-0.065, -0.035, -0.030],  # thumb
            [-0.065, -0.024, 0.040],  # index
            [-0.065, -0.008, 0.060],  # middle
            [-0.065, 0.012, 0.050],  # ring
            [-0.065, 0.030, 0.025],  # little
        ],
        dtype=np.float64,
    )
    return transform_points(world_t_object, keypoints_object)


def run_hand_object_experiment() -> tuple[dict[str, np.ndarray], dict[str, float]]:
    cloud_local = make_box_surface_points()
    world_t_object = make_world_t_object()

    open3d_cloud = o3d.geometry.PointCloud()
    open3d_cloud.points = o3d.utility.Vector3dVector(cloud_local)
    open3d_cloud.transform(world_t_object)
    cloud_world = np.asarray(open3d_cloud.points).copy()
    cloud_world_numpy = transform_points(world_t_object, cloud_local)

    hand_world = make_hand_keypoints_world(world_t_object)
    object_origin_world = world_t_object[:3, 3]
    local_radii = np.linalg.norm(cloud_local, axis=1)
    world_radii = np.linalg.norm(cloud_world - object_origin_world, axis=1)

    metrics = {
        "open3d_numpy_transform_error_m": float(
            np.max(np.linalg.norm(cloud_world - cloud_world_numpy, axis=1))
        ),
        "rigid_radius_preservation_error_m": float(
            np.max(np.abs(world_radii - local_radii))
        ),
        "local_cloud_centroid_norm_m": float(
            np.linalg.norm(np.mean(cloud_local, axis=0))
        ),
        "world_centroid_to_pose_translation_error_m": float(
            np.linalg.norm(np.mean(cloud_world, axis=0) - object_origin_world)
        ),
    }
    arrays = {
        "object_cloud_local": cloud_local,
        "world_T_object": world_t_object,
        "object_cloud_world": cloud_world,
        "hand_keypoints_world": hand_world,
    }
    return arrays, metrics


def save_outputs(
    phase_root: Path, arrays: dict[str, np.ndarray], metrics: dict[str, float]
) -> None:
    data_dir = phase_root / "data"
    output_dir = phase_root / "outputs"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    data_path = data_dir / "p2a_hand_object_geometry.npz"
    report_path = output_dir / "p2a_hand_object_geometry.json"
    figure_path = output_dir / "p2a_hand_object_geometry.png"
    np.savez_compressed(data_path, **arrays)
    report_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    figure = plt.figure(figsize=(11, 4.8), constrained_layout=True)
    local_axis = figure.add_subplot(1, 2, 1, projection="3d")
    local_cloud = arrays["object_cloud_local"]
    local_axis.scatter(*local_cloud.T, s=3, alpha=0.5)
    local_axis.scatter(0.0, 0.0, 0.0, c="black", marker="x", s=60)
    local_axis.set_title("object_cloud_local (object frame)")
    local_axis.set_xlabel("object x [m]")
    local_axis.set_ylabel("object y [m]")
    local_axis.set_zlabel("object z [m]")

    world_axis = figure.add_subplot(1, 2, 2, projection="3d")
    world_cloud = arrays["object_cloud_world"]
    hand = arrays["hand_keypoints_world"]
    world_axis.scatter(*world_cloud.T, s=3, alpha=0.4, label="object cloud")
    world_axis.scatter(*hand.T, c="tab:red", s=45, label="palm + fingertips")
    for index, name in enumerate(HAND_KEYPOINT_NAMES):
        world_axis.text(*hand[index], name, fontsize=7)
    world_axis.set_title("Same object and hand in world frame")
    world_axis.set_xlabel("world x [m]")
    world_axis.set_ylabel("world y [m]")
    world_axis.set_zlabel("world z [m]")
    world_axis.legend(loc="upper left")
    world_axis.view_init(elev=22, azim=-65)
    figure.savefig(figure_path, dpi=160)
    plt.close(figure)

    print(f"\nSaved data   to: {data_path}")
    print(f"Saved report to: {report_path}")
    print(f"Saved figure to: {figure_path}")


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    arrays, metrics = run_hand_object_experiment()
    np.set_printoptions(precision=5, suppress=True)

    print("Accelerated Phase 2A - hand/object task geometry")
    print(f"hand keypoint names       = {list(HAND_KEYPOINT_NAMES)}")
    print(f"object_cloud_local shape  = {arrays['object_cloud_local'].shape}")
    print(f"world_T_object shape      = {arrays['world_T_object'].shape}")
    print(f"object_cloud_world shape  = {arrays['object_cloud_world'].shape}")
    print(f"hand_keypoints_world shape = {arrays['hand_keypoints_world'].shape}")
    print("\nworld_T_object =")
    print(arrays["world_T_object"])
    print("object origin in world    =", arrays["world_T_object"][:3, 3])
    print("\nRigid-transform checks")
    print(
        "Open3D vs NumPy transform error = "
        f"{metrics['open3d_numpy_transform_error_m']:.3e} m"
    )
    print(
        "radius preservation error       = "
        f"{metrics['rigid_radius_preservation_error_m']:.3e} m"
    )
    print(
        "world centroid/translation error = "
        f"{metrics['world_centroid_to_pose_translation_error_m']:.3e} m"
    )
    print("\nLocal cloud describes object shape; world_T_object places it in the scene.")
    print("Only world-frame hand points and world-frame object points may be compared directly.")
    save_outputs(phase_root, arrays, metrics)


if __name__ == "__main__":
    main()

