"""Phase 5 P5-1: demonstration episodes, causal alignment, and action chunks."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np


SAMPLE_RATE_HZ = 10.0
DT_S = 1.0 / SAMPLE_RATE_HZ
ACTION_CHUNK_HORIZON = 4
JOINT_NAMES = ("shoulder", "elbow", "wrist")
PHASE_NAMES = ("approach", "contact", "manipulate", "release")


class ContractError(ValueError):
    """Raised when a demonstration violates its declared temporal contract."""


def make_episode(episode_id: int, length: int, offset: float) -> dict[str, np.ndarray]:
    local_frame = np.arange(length)
    timestamp = local_frame * DT_S
    phase = np.full(length, 2, dtype=np.int64)
    phase[:2] = 0
    phase[2] = 1
    phase[-2:] = 3
    contact = np.isin(phase, (1, 2))

    command = np.column_stack(
        (
            offset + 0.10 + 0.025 * local_frame,
            -0.20 + 0.045 * np.sin(0.55 * local_frame + offset),
            0.08 * np.cos(0.40 * local_frame + offset),
        )
    )
    feedback = np.empty_like(command)
    feedback[0] = command[0] - np.array([0.018, -0.012, 0.009])
    for frame in range(1, length):
        feedback[frame] = feedback[frame - 1] + 0.72 * (
            command[frame - 1] - feedback[frame - 1]
        )

    object_pose = np.zeros((length, 7), dtype=np.float64)
    object_pose[:, 0] = 0.45 + 0.008 * local_frame
    object_pose[:, 1] = 0.10 + 0.03 * episode_id
    object_pose[:, 2] = 0.90
    object_pose[:, 6] = 1.0  # quaternion xyzw = [0, 0, 0, 1]

    fingertip_contact = np.repeat(contact[:, None], 5, axis=1)
    force = fingertip_contact * (
        1.2 + 0.15 * np.arange(5)[None, :] + 0.04 * local_frame[:, None]
    )
    terminal = np.zeros(length, dtype=bool)
    terminal[-1] = True

    return {
        "episode_id": np.full(length, episode_id, dtype=np.int64),
        "local_frame": local_frame,
        "timestamp_s": timestamp,
        "observation_available_s": timestamp.copy(),
        "action_timestamp_s": timestamp.copy(),
        "robot_q_feedback_rad": feedback,
        "object_pose_xyz_xyzw": object_pose,
        "fingertip_contact": fingertip_contact,
        "force_n": force,
        "phase": phase,
        "robot_q_command_rad": command,
        "terminal": terminal,
        "valid": np.ones(length, dtype=bool),
    }


def concatenate_episodes(episodes: list[dict[str, np.ndarray]]) -> dict[str, np.ndarray]:
    return {
        key: np.concatenate([episode[key] for episode in episodes], axis=0)
        for key in episodes[0]
    }


def validate_demonstration(data: dict[str, np.ndarray]) -> None:
    required = {
        "episode_id",
        "local_frame",
        "timestamp_s",
        "observation_available_s",
        "action_timestamp_s",
        "robot_q_feedback_rad",
        "object_pose_xyz_xyzw",
        "fingertip_contact",
        "force_n",
        "phase",
        "robot_q_command_rad",
        "terminal",
        "valid",
    }
    missing = sorted(required - set(data))
    if missing:
        raise ContractError(f"missing required fields {missing}")

    total_frames = len(data["episode_id"])
    expected_shapes = {
        "robot_q_feedback_rad": (total_frames, len(JOINT_NAMES)),
        "object_pose_xyz_xyzw": (total_frames, 7),
        "fingertip_contact": (total_frames, 5),
        "force_n": (total_frames, 5),
        "robot_q_command_rad": (total_frames, len(JOINT_NAMES)),
    }
    for name, shape in expected_shapes.items():
        if data[name].shape != shape:
            raise ContractError(f"{name}: expected shape {shape}, got {data[name].shape}")

    if np.any(data["observation_available_s"] > data["timestamp_s"] + 1e-12):
        raise ContractError("observation contains information unavailable at decision time")
    if not np.allclose(data["action_timestamp_s"], data["timestamp_s"], atol=1e-12):
        raise ContractError("action timestamp must match its decision timestamp")

    quaternion = data["object_pose_xyz_xyzw"][:, 3:]
    if not np.allclose(np.linalg.norm(quaternion, axis=1), 1.0, atol=1e-8):
        raise ContractError("object quaternion must be unit xyzw")

    episode_ids = data["episode_id"]
    for episode_id in np.unique(episode_ids):
        indices = np.flatnonzero(episode_ids == episode_id)
        if not np.all(np.diff(indices) == 1):
            raise ContractError(f"episode {episode_id}: frames must be contiguous")
        if not np.all(np.diff(data["timestamp_s"][indices]) > 0):
            raise ContractError(f"episode {episode_id}: timestamps must strictly increase")
        if not np.array_equal(data["local_frame"][indices], np.arange(len(indices))):
            raise ContractError(f"episode {episode_id}: local frame index is invalid")
        terminals = np.flatnonzero(data["terminal"][indices])
        if not np.array_equal(terminals, np.array([len(indices) - 1])):
            raise ContractError(f"episode {episode_id}: terminal must mark only its last frame")

    numeric_fields = (
        "robot_q_feedback_rad",
        "object_pose_xyz_xyzw",
        "force_n",
        "robot_q_command_rad",
    )
    for name in numeric_fields:
        if np.any(~np.isfinite(data[name][data["valid"]])):
            raise ContractError(f"{name}: valid rows must be finite")


def build_action_chunks(
    data: dict[str, np.ndarray], horizon: int = ACTION_CHUNK_HORIZON
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    total_frames, action_dim = data["robot_q_command_rad"].shape
    chunks = np.zeros((total_frames, horizon, action_dim), dtype=np.float64)
    padding_mask = np.zeros((total_frames, horizon), dtype=bool)
    source_episode = np.full((total_frames, horizon), -1, dtype=np.int64)
    source_local_frame = np.full((total_frames, horizon), -1, dtype=np.int64)

    for anchor in range(total_frames):
        anchor_episode = data["episode_id"][anchor]
        for step in range(horizon):
            source = anchor + step
            if source >= total_frames or data["episode_id"][source] != anchor_episode:
                break
            chunks[anchor, step] = data["robot_q_command_rad"][source]
            padding_mask[anchor, step] = True
            source_episode[anchor, step] = data["episode_id"][source]
            source_local_frame[anchor, step] = data["local_frame"][source]
    return chunks, padding_mask, source_episode, source_local_frame


def validate_chunks(
    data: dict[str, np.ndarray],
    chunks: np.ndarray,
    padding_mask: np.ndarray | None,
    source_episode: np.ndarray,
) -> None:
    if padding_mask is None:
        raise ContractError("action chunk requires a padding mask")
    expected_shape = (len(data["episode_id"]), ACTION_CHUNK_HORIZON, len(JOINT_NAMES))
    if chunks.shape != expected_shape:
        raise ContractError(f"action chunk: expected shape {expected_shape}, got {chunks.shape}")
    if padding_mask.shape != expected_shape[:2]:
        raise ContractError("padding mask shape does not match action chunk")
    anchor_episode = data["episode_id"][:, None]
    if np.any(padding_mask & (source_episode != anchor_episode)):
        raise ContractError("action chunk crosses an episode boundary")
    if np.any(~padding_mask & (source_episode != -1)):
        raise ContractError("padded action entries must have source episode -1")


def make_naive_cross_episode_chunks(
    data: dict[str, np.ndarray]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    total_frames, action_dim = data["robot_q_command_rad"].shape
    chunks = np.zeros((total_frames, ACTION_CHUNK_HORIZON, action_dim))
    mask = np.zeros((total_frames, ACTION_CHUNK_HORIZON), dtype=bool)
    source_episode = np.full((total_frames, ACTION_CHUNK_HORIZON), -1, dtype=np.int64)
    for anchor in range(total_frames):
        stop = min(total_frames, anchor + ACTION_CHUNK_HORIZON)
        count = stop - anchor
        chunks[anchor, :count] = data["robot_q_command_rad"][anchor:stop]
        mask[anchor, :count] = True
        source_episode[anchor, :count] = data["episode_id"][anchor:stop]
    return chunks, mask, source_episode


def rejected_message(name: str, function, *args) -> str:
    try:
        function(*args)
    except ContractError as error:
        return f"REJECTED: {error}"
    raise AssertionError(f"{name} was expected to be rejected")


def run_demonstration_experiment() -> tuple[dict[str, np.ndarray], dict[str, object]]:
    data = concatenate_episodes([make_episode(0, 9, 0.00), make_episode(1, 7, 0.16)])
    validate_demonstration(data)
    chunks, mask, source_episode, source_local_frame = build_action_chunks(data)
    validate_chunks(data, chunks, mask, source_episode)

    shifted_action = {key: value.copy() for key, value in data.items()}
    shifted_action["action_timestamp_s"] += DT_S

    future_leakage = {key: value.copy() for key, value in data.items()}
    future_leakage["observation_available_s"][4] += DT_S

    naive_chunks, naive_mask, naive_source_episode = make_naive_cross_episode_chunks(data)
    violations = {
        "one_frame_action_shift": rejected_message(
            "one_frame_action_shift", validate_demonstration, shifted_action
        ),
        "future_feedback_leakage": rejected_message(
            "future_feedback_leakage", validate_demonstration, future_leakage
        ),
        "naive_chunk_cross_episode": rejected_message(
            "naive_chunk_cross_episode",
            validate_chunks,
            data,
            naive_chunks,
            naive_mask,
            naive_source_episode,
        ),
        "missing_padding_mask": rejected_message(
            "missing_padding_mask",
            validate_chunks,
            data,
            chunks,
            None,
            source_episode,
        ),
    }

    arrays = {
        **data,
        "action_chunk_rad": chunks,
        "action_chunk_valid": mask,
        "action_chunk_source_episode": source_episode,
        "action_chunk_source_local_frame": source_local_frame,
    }
    episode_lengths = [int(np.sum(data["episode_id"] == i)) for i in np.unique(data["episode_id"])]
    metrics: dict[str, object] = {
        "episodes": len(episode_lengths),
        "episode_lengths": episode_lengths,
        "total_frames": len(data["episode_id"]),
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "joint_names": list(JOINT_NAMES),
        "observation_q_shape": list(data["robot_q_feedback_rad"].shape),
        "action_q_shape": list(data["robot_q_command_rad"].shape),
        "object_pose_shape": list(data["object_pose_xyz_xyzw"].shape),
        "contact_force_shape": list(data["force_n"].shape),
        "terminal_global_indices": np.flatnonzero(data["terminal"]).tolist(),
        "chunk_horizon": ACTION_CHUNK_HORIZON,
        "chunk_shape": list(chunks.shape),
        "chunk_mask_shape": list(mask.shape),
        "valid_chunk_entries": int(np.sum(mask)),
        "padded_chunk_entries": int(mask.size - np.sum(mask)),
        "example_anchor_global_frame": 7,
        "example_source_local_frames": source_local_frame[7].tolist(),
        "example_valid_mask": mask[7].tolist(),
        "violations": violations,
    }
    return arrays, metrics


def save_outputs(
    phase_root: Path, arrays: dict[str, np.ndarray], metrics: dict[str, object]
) -> None:
    data_dir = phase_root / "data"
    output_dir = phase_root / "outputs"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_path = data_dir / "p5a_demonstration_contract.npz"
    report_path = output_dir / "p5a_demonstration_contract.json"
    figure_path = output_dir / "p5a_demonstration_contract.png"
    np.savez_compressed(data_path, **arrays)
    report_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    global_frame = np.arange(metrics["total_frames"])
    boundary = metrics["episode_lengths"][0] - 0.5
    figure, axes = plt.subplots(3, 1, figsize=(11, 9), constrained_layout=True)
    axes[0].plot(global_frame, arrays["robot_q_feedback_rad"][:, 0], "o-", label="observation: q feedback")
    axes[0].plot(global_frame, arrays["robot_q_command_rad"][:, 0], "s--", label="action: q command")
    axes[0].axvline(boundary, color="black", linestyle=":", label="episode boundary")
    axes[0].scatter(
        np.flatnonzero(arrays["terminal"]),
        arrays["robot_q_command_rad"][arrays["terminal"], 0],
        marker="x",
        s=85,
        color="tab:red",
        label="terminal",
    )
    axes[0].set_ylabel("joint 0 [rad]")
    axes[0].set_title("Two independent episodes: observation now, command next")
    axes[0].legend(ncol=2, fontsize=8)
    axes[0].grid(alpha=0.25)

    image = axes[1].imshow(
        arrays["action_chunk_valid"].astype(int).T,
        aspect="auto",
        origin="lower",
        cmap="Blues",
        vmin=0,
        vmax=1,
        interpolation="nearest",
    )
    axes[1].axvline(boundary, color="tab:red", linestyle=":")
    axes[1].set_yticks(np.arange(ACTION_CHUNK_HORIZON), [f"t+{i}" for i in range(ACTION_CHUNK_HORIZON)])
    axes[1].set_ylabel("chunk step")
    axes[1].set_title("Action-chunk valid mask: padded tail never enters the next episode")
    figure.colorbar(image, ax=axes[1], ticks=[0, 1], label="0 padded / 1 valid")

    example_anchor = metrics["example_anchor_global_frame"]
    local_sources = arrays["action_chunk_source_local_frame"][example_anchor]
    valid = arrays["action_chunk_valid"][example_anchor]
    x = np.arange(ACTION_CHUNK_HORIZON)
    axes[2].bar(x[valid], arrays["action_chunk_rad"][example_anchor, valid, 0], color="tab:blue", label="valid action")
    axes[2].bar(x[~valid], np.full(np.sum(~valid), 0.02), color="lightgray", hatch="//", label="padding (ignored)")
    labels = [f"local {frame}" if is_valid else "PAD" for frame, is_valid in zip(local_sources, valid)]
    axes[2].set_xticks(x, labels)
    axes[2].set_ylabel("joint-0 command [rad]")
    axes[2].set_xlabel("chunk position")
    axes[2].set_title(f"Anchor global frame {example_anchor}: chunk stops at episode terminal")
    axes[2].legend(fontsize=8)
    axes[2].grid(axis="y", alpha=0.25)
    figure.savefig(figure_path, dpi=160)
    plt.close(figure)

    print(f"\nSaved data   to: {data_path}")
    print(f"Saved report to: {report_path}")
    print(f"Saved figure to: {figure_path}")


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    _, metrics = run_demonstration_experiment()
    print("Phase 5 P5-1 - demonstration contract and action chunks")
    print(f"episodes / total frames          = {metrics['episodes']} / {metrics['total_frames']}")
    print(f"episode lengths                  = {metrics['episode_lengths']}")
    print(f"sample rate                      = {metrics['sample_rate_hz']:.1f} Hz")
    print(f"joint order                      = {metrics['joint_names']}")
    print("\nCanonical demonstration")
    print(f"  observation q shape            = {tuple(metrics['observation_q_shape'])}  [T,Nq]")
    print(f"  action command shape           = {tuple(metrics['action_q_shape'])}  [T,Na]")
    print(f"  object pose shape              = {tuple(metrics['object_pose_shape'])}  [T,xyz+xyzw]")
    print(f"  contact/force shape            = {tuple(metrics['contact_force_shape'])}  [T,5]")
    print(f"  terminal global indices        = {metrics['terminal_global_indices']}")
    print("  causal/episode validator       = PASS")
    print("\nFuture action chunks")
    print(f"  horizon H                      = {metrics['chunk_horizon']}")
    print(f"  action chunk shape             = {tuple(metrics['chunk_shape'])}  [T,H,Na]")
    print(f"  padding mask shape             = {tuple(metrics['chunk_mask_shape'])}  [T,H]")
    print(f"  valid / padded entries         = {metrics['valid_chunk_entries']} / {metrics['padded_chunk_entries']}")
    print(f"  anchor global frame            = {metrics['example_anchor_global_frame']}")
    print(f"  source local frames            = {metrics['example_source_local_frames']}")
    print(f"  valid mask                     = {metrics['example_valid_mask']}")
    print("\nDeliberate contract violations")
    for name, result in metrics["violations"].items():
        print(f"{name:29s} = {result}")
    print("\nPadding is absence, not a physical zero command.")
    print("An action chunk must stop at the terminal boundary of its own episode.")

    arrays, metrics = run_demonstration_experiment()
    save_outputs(phase_root, arrays, metrics)


if __name__ == "__main__":
    main()
