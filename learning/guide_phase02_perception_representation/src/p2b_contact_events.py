"""Accelerated Phase 2B: fingertip distances, contact events, and timestamp error."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
from scipy.spatial import cKDTree

from p2a_hand_object_geometry import make_box_surface_points, transform_points


FINGERTIP_NAMES = (
    "thumb_tip",
    "index_tip",
    "middle_tip",
    "ring_tip",
    "little_tip",
)
CONTACT_THRESHOLD_M = 0.008
TIMESTAMP_OFFSET_FRAMES = 5


def rotation_z(angle: float) -> np.ndarray:
    return np.array(
        [
            [np.cos(angle), -np.sin(angle), 0.0],
            [np.sin(angle), np.cos(angle), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )


def make_object_trajectory(timestamp: np.ndarray) -> np.ndarray:
    """Create a slowly moving object pose in a fixed world frame."""
    duration = timestamp[-1]
    poses = np.repeat(np.eye(4)[None, :, :], len(timestamp), axis=0)
    for frame, time_s in enumerate(timestamp):
        progress = time_s / duration
        poses[frame, :3, :3] = rotation_z(
            np.deg2rad(20.0) * np.sin(np.pi * progress)
        )
        poses[frame, :3, 3] = np.array(
            [
                0.40 + 0.12 * progress,
                0.10 + 0.02 * np.sin(2.0 * np.pi * progress),
                0.90,
            ]
        )
    return poses


def make_gap_profile(frame_count: int) -> tuple[np.ndarray, np.ndarray]:
    """Return fingertip-to-surface gap and semantic phase for every frame."""
    approach_end = 30
    contact_end = 85
    gaps = np.empty(frame_count, dtype=np.float64)
    phases = np.empty(frame_count, dtype="<U10")

    gaps[: approach_end + 1] = np.linspace(0.050, 0.002, approach_end + 1)
    phases[: approach_end + 1] = "approach"
    gaps[approach_end + 1 : contact_end + 1] = 0.002
    phases[approach_end + 1 : contact_end + 1] = "contact"
    gaps[contact_end + 1 :] = np.linspace(
        0.002, 0.050, frame_count - contact_end - 1
    )
    phases[contact_end + 1 :] = "release"
    return gaps, phases


def make_hand_sequence_world(
    object_poses: np.ndarray, gaps: np.ndarray
) -> np.ndarray:
    """Create palm + five fingertips near the object's negative-x face."""
    fingertip_yz = np.array(
        [
            [-0.030000, -0.040],
            [-0.013333, 0.020],
            [0.000000, 0.060],
            [0.013333, 0.040],
            [0.030000, 0.000],
        ]
    )
    hand_world = np.empty((len(gaps), 6, 3), dtype=np.float64)
    for frame, (pose, gap) in enumerate(zip(object_poses, gaps, strict=True)):
        palm_object = np.array([[-0.13, 0.0, 0.0]])
        fingertips_object = np.column_stack(
            (
                np.full(5, -0.06 - gap),
                fingertip_yz[:, 0],
                fingertip_yz[:, 1],
            )
        )
        hand_world[frame] = transform_points(
            pose, np.vstack((palm_object, fingertips_object))
        )
    return hand_world


def nearest_distances(
    hand_world: np.ndarray,
    object_cloud_local: np.ndarray,
    object_poses: np.ndarray,
    object_frame_indices: np.ndarray,
) -> np.ndarray:
    """Compare each hand frame with the selected object frame in world coordinates."""
    distances = np.empty((len(hand_world), 5), dtype=np.float64)
    for hand_frame, object_frame in enumerate(object_frame_indices):
        cloud_world = transform_points(object_poses[object_frame], object_cloud_local)
        tree = cKDTree(cloud_world)
        distances[hand_frame] = tree.query(hand_world[hand_frame, 1:])[0]
    return distances


def transition_frames(contact: np.ndarray) -> list[int]:
    """Return frames where a boolean contact sequence changes state."""
    return (np.flatnonzero(contact[1:] != contact[:-1]) + 1).tolist()


def run_contact_experiment() -> tuple[dict[str, np.ndarray], dict[str, object]]:
    timestamp = np.arange(121, dtype=np.float64) / 30.0
    object_cloud_local = make_box_surface_points(samples_per_axis=25)
    object_poses = make_object_trajectory(timestamp)
    gaps, phases = make_gap_profile(len(timestamp))
    hand_world = make_hand_sequence_world(object_poses, gaps)

    aligned_indices = np.arange(len(timestamp))
    offset_indices = np.minimum(
        aligned_indices + TIMESTAMP_OFFSET_FRAMES, len(timestamp) - 1
    )
    aligned_distance = nearest_distances(
        hand_world, object_cloud_local, object_poses, aligned_indices
    )
    offset_distance = nearest_distances(
        hand_world, object_cloud_local, object_poses, offset_indices
    )
    aligned_contact = aligned_distance < CONTACT_THRESHOLD_M
    offset_contact = offset_distance < CONTACT_THRESHOLD_M
    mismatch = aligned_contact != offset_contact

    metrics: dict[str, object] = {
        "frame_count": len(timestamp),
        "sample_rate_hz": 30.0,
        "contact_threshold_m": CONTACT_THRESHOLD_M,
        "timestamp_offset_frames": TIMESTAMP_OFFSET_FRAMES,
        "timestamp_offset_s": TIMESTAMP_OFFSET_FRAMES / 30.0,
        "aligned_min_distance_m": float(np.min(aligned_distance)),
        "aligned_max_distance_m": float(np.max(aligned_distance)),
        "aligned_contact_entries": int(np.sum(aligned_contact)),
        "offset_contact_entries": int(np.sum(offset_contact)),
        "mismatched_contact_entries": int(np.sum(mismatch)),
        "frames_with_any_mismatch": np.flatnonzero(
            np.any(mismatch, axis=1)
        ).tolist(),
        "middle_finger_aligned_transitions": transition_frames(
            aligned_contact[:, 2]
        ),
        "middle_finger_offset_transitions": transition_frames(offset_contact[:, 2]),
    }
    arrays = {
        "timestamp": timestamp,
        "object_cloud_local": object_cloud_local,
        "world_T_object": object_poses,
        "hand_keypoints_world": hand_world,
        "hand_object_distance": aligned_distance,
        "contact_event": aligned_contact,
        "offset_hand_object_distance": offset_distance,
        "offset_contact_event": offset_contact,
        "phase": phases,
    }
    return arrays, metrics


def save_outputs(
    phase_root: Path, arrays: dict[str, np.ndarray], metrics: dict[str, object]
) -> None:
    data_dir = phase_root / "data"
    output_dir = phase_root / "outputs"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    data_path = data_dir / "p2b_contact_events.npz"
    report_path = output_dir / "p2b_contact_events.json"
    figure_path = output_dir / "p2b_contact_events.png"
    np.savez_compressed(data_path, **arrays)
    report_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    time_s = arrays["timestamp"]
    figure, axes = plt.subplots(
        2, 1, figsize=(10, 7), sharex=True, constrained_layout=True
    )
    for finger, name in enumerate(FINGERTIP_NAMES):
        axes[0].plot(
            time_s,
            1000.0 * arrays["hand_object_distance"][:, finger],
            label=name,
        )
    axes[0].axhline(
        1000.0 * CONTACT_THRESHOLD_M,
        color="black",
        linestyle="--",
        label="contact threshold",
    )
    axes[0].set_ylabel("nearest surface distance [mm]")
    axes[0].set_title("Aligned fingertip-to-object distance")
    axes[0].legend(ncol=3, fontsize=8)
    axes[0].grid(alpha=0.25)

    middle = 2
    axes[1].plot(
        time_s,
        1000.0 * arrays["hand_object_distance"][:, middle],
        label="aligned timestamps",
    )
    axes[1].plot(
        time_s,
        1000.0 * arrays["offset_hand_object_distance"][:, middle],
        label=f"object shifted +{TIMESTAMP_OFFSET_FRAMES} frames",
    )
    axes[1].axhline(
        1000.0 * CONTACT_THRESHOLD_M,
        color="black",
        linestyle="--",
        label="contact threshold",
    )
    axes[1].fill_between(
        time_s,
        0.0,
        1.0,
        where=arrays["contact_event"][:, middle]
        != arrays["offset_contact_event"][:, middle],
        transform=axes[1].get_xaxis_transform(),
        color="tab:red",
        alpha=0.15,
        label="contact disagreement",
    )
    axes[1].set_xlabel("time [s]")
    axes[1].set_ylabel("middle fingertip distance [mm]")
    axes[1].set_title("Same world frame, wrong timestamp")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.25)
    figure.savefig(figure_path, dpi=160)
    plt.close(figure)

    print(f"\nSaved data   to: {data_path}")
    print(f"Saved report to: {report_path}")
    print(f"Saved figure to: {figure_path}")


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    arrays, metrics = run_contact_experiment()

    print("Accelerated Phase 2B - fingertip distance and contact event")
    print(
        f"frames / sample rate       = {metrics['frame_count']} / "
        f"{metrics['sample_rate_hz']:.1f} Hz"
    )
    print(
        f"contact threshold          = "
        f"{1000.0 * metrics['contact_threshold_m']:.1f} mm"
    )
    print(
        f"distance shape             = "
        f"{arrays['hand_object_distance'].shape}  [T,5 fingertips]"
    )
    print(
        f"contact_event shape        = "
        f"{arrays['contact_event'].shape}  [T,5 fingertips]"
    )
    print("\nCorrectly aligned streams")
    print(
        f"minimum distance           = "
        f"{1000.0 * metrics['aligned_min_distance_m']:.3f} mm"
    )
    print(
        f"maximum distance           = "
        f"{1000.0 * metrics['aligned_max_distance_m']:.3f} mm"
    )
    print(
        f"middle-finger transitions  = "
        f"{metrics['middle_finger_aligned_transitions']}"
    )
    print("\nDeliberate timestamp violation")
    print(
        "object stream offset       = "
        f"+{metrics['timestamp_offset_frames']} frames / "
        f"{metrics['timestamp_offset_s']:.3f} s"
    )
    print(
        f"mismatched contact entries = {metrics['mismatched_contact_entries']}"
    )
    print(f"frames with any mismatch   = {metrics['frames_with_any_mismatch']}")
    print(
        f"middle-finger transitions  = "
        f"{metrics['middle_finger_offset_transitions']}"
    )
    print("\ncontact_event says whether distance crosses a threshold.")
    print("It does not encode contact geometry, force, friction, or grasp stability.")
    save_outputs(phase_root, arrays, metrics)


if __name__ == "__main__":
    main()

