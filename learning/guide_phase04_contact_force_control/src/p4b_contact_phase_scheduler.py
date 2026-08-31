"""Phase 4 P4-2: contact-phase scheduling and arm/hand synchronization."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np


SAMPLE_RATE_HZ = 30.0
ENTER_THRESHOLD_M = 0.007
EXIT_THRESHOLD_M = 0.011
MIN_DWELL_FRAMES = 8
CONTACT_SETTLE_FRAMES = 10
PHASE_NAMES = ("approach", "contact", "manipulate", "release")


def make_contact_distance() -> np.ndarray:
    """Create an approach/hold/release distance with threshold chatter."""
    distance = np.empty(151, dtype=np.float64)
    distance[:41] = np.linspace(0.050, 0.010, 41)
    distance[41:47] = np.array([0.0075, 0.0085, 0.0076, 0.0084, 0.0074, 0.0065])
    distance[47:105] = 0.006 + 0.00025 * np.sin(np.linspace(0, 6 * np.pi, 58))
    distance[105:113] = np.array(
        [0.0065, 0.0075, 0.0083, 0.0077, 0.0084, 0.0076, 0.0090, 0.0120]
    )
    distance[113:] = np.linspace(0.013, 0.050, len(distance) - 113)
    return distance


def shift_stream_later(values: np.ndarray, frames: int) -> np.ndarray:
    """Delay a sampled stream while retaining its initial value at the boundary."""
    if frames < 0:
        raise ValueError("frames must be non-negative")
    if frames == 0:
        return values.copy()
    shifted = np.empty_like(values)
    shifted[:frames] = values[0]
    shifted[frames:] = values[:-frames]
    return shifted


def naive_contact(distance_m: np.ndarray, threshold_m: float = 0.008) -> np.ndarray:
    return distance_m <= threshold_m


def hysteresis_contact(
    distance_m: np.ndarray,
    enter_threshold_m: float = ENTER_THRESHOLD_M,
    exit_threshold_m: float = EXIT_THRESHOLD_M,
    min_dwell_frames: int = MIN_DWELL_FRAMES,
) -> np.ndarray:
    """Schmitt-trigger contact state with a minimum dwell time after each switch."""
    state = False
    last_switch = -min_dwell_frames
    contact = np.zeros(len(distance_m), dtype=bool)
    for frame, distance in enumerate(distance_m):
        can_switch = frame - last_switch >= min_dwell_frames
        if not state and distance <= enter_threshold_m and can_switch:
            state = True
            last_switch = frame
        elif state and distance >= exit_threshold_m and can_switch:
            state = False
            last_switch = frame
        contact[frame] = state
    return contact


def phases_from_contact(contact: np.ndarray) -> np.ndarray:
    """Map contact state to approach/contact/manipulate/release phase codes."""
    phase = np.zeros(len(contact), dtype=np.int64)
    first_contact = np.flatnonzero(contact)
    if len(first_contact) == 0:
        return phase
    start = int(first_contact[0])
    phase[start : start + CONTACT_SETTLE_FRAMES] = 1
    contact_after_settle = contact.copy()
    contact_after_settle[: start + CONTACT_SETTLE_FRAMES] = False
    phase[contact_after_settle] = 2
    end_candidates = np.flatnonzero(~contact & (np.arange(len(contact)) > start))
    if len(end_candidates):
        phase[int(end_candidates[0]) :] = 3
    return phase


def controller_from_phase(phase: np.ndarray) -> np.ndarray:
    """0: initialization retargeting; 1: contact-geometry refinement."""
    return np.isin(phase, (1, 2)).astype(np.int64)


def make_hand_commands(time_s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    initialization = 0.22 + 0.025 * np.sin(2.0 * np.pi * 0.35 * time_s)
    geometry_refined = initialization + 0.20 + 0.012 * np.sin(
        2.0 * np.pi * 0.18 * time_s
    )
    return initialization, geometry_refined


def select_command(
    initialization: np.ndarray, geometry_refined: np.ndarray, controller: np.ndarray
) -> np.ndarray:
    return np.where(controller.astype(bool), geometry_refined, initialization)


def transition_indices(values: np.ndarray) -> np.ndarray:
    return np.flatnonzero(values[1:] != values[:-1]) + 1


def run_scheduler_experiment(offset_frames: int = 5) -> tuple[dict[str, np.ndarray], dict[str, object]]:
    distance = make_contact_distance()
    time_s = np.arange(len(distance)) / SAMPLE_RATE_HZ
    delayed_distance = shift_stream_later(distance, offset_frames)

    raw_contact = naive_contact(distance)
    robust_contact = hysteresis_contact(distance)
    delayed_contact = hysteresis_contact(delayed_distance)
    robust_phase = phases_from_contact(robust_contact)
    delayed_phase = phases_from_contact(delayed_contact)

    raw_controller = raw_contact.astype(np.int64)
    robust_controller = controller_from_phase(robust_phase)
    delayed_controller = controller_from_phase(delayed_phase)
    initialization, geometry_refined = make_hand_commands(time_s)
    raw_command = select_command(initialization, geometry_refined, raw_controller)
    robust_command = select_command(initialization, geometry_refined, robust_controller)
    delayed_command = select_command(initialization, geometry_refined, delayed_controller)

    phase_mismatch = robust_phase != delayed_phase
    controller_mismatch = robust_controller != delayed_controller
    arrays = {
        "frame": np.arange(len(distance)),
        "timestamp_s": time_s,
        "distance_m": distance,
        "delayed_distance_m": delayed_distance,
        "raw_contact": raw_contact,
        "robust_contact": robust_contact,
        "delayed_contact": delayed_contact,
        "robust_phase": robust_phase,
        "delayed_phase": delayed_phase,
        "raw_controller": raw_controller,
        "robust_controller": robust_controller,
        "delayed_controller": delayed_controller,
        "initialization_command_rad": initialization,
        "geometry_refined_command_rad": geometry_refined,
        "raw_command_rad": raw_command,
        "robust_command_rad": robust_command,
        "delayed_command_rad": delayed_command,
        "phase_mismatch": phase_mismatch,
        "controller_mismatch": controller_mismatch,
    }
    metrics: dict[str, object] = {
        "frames": len(distance),
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "enter_threshold_m": ENTER_THRESHOLD_M,
        "exit_threshold_m": EXIT_THRESHOLD_M,
        "minimum_dwell_frames": MIN_DWELL_FRAMES,
        "raw_contact_transition_indices": transition_indices(raw_contact).tolist(),
        "robust_contact_transition_indices": transition_indices(robust_contact).tolist(),
        "raw_controller_switches": int(len(transition_indices(raw_controller))),
        "robust_controller_switches": int(len(transition_indices(robust_controller))),
        "raw_command_total_variation_rad": float(np.sum(np.abs(np.diff(raw_command)))),
        "robust_command_total_variation_rad": float(np.sum(np.abs(np.diff(robust_command)))),
        "raw_max_command_step_rad": float(np.max(np.abs(np.diff(raw_command)))),
        "robust_max_command_step_rad": float(np.max(np.abs(np.diff(robust_command)))),
        "offset_frames": offset_frames,
        "offset_s": offset_frames / SAMPLE_RATE_HZ,
        "delayed_contact_transition_indices": transition_indices(delayed_contact).tolist(),
        "phase_mismatch_indices": np.flatnonzero(phase_mismatch).tolist(),
        "controller_mismatch_indices": np.flatnonzero(controller_mismatch).tolist(),
    }
    return arrays, metrics


def save_outputs(
    phase_root: Path, arrays: dict[str, np.ndarray], metrics: dict[str, object]
) -> None:
    output_dir = phase_root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "p4b_contact_phase_scheduler.csv"
    report_path = output_dir / "p4b_contact_phase_scheduler.json"
    figure_path = output_dir / "p4b_contact_phase_scheduler.png"

    field_names = list(arrays)
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(field_names)
        for frame in range(len(arrays["frame"])):
            writer.writerow([arrays[name][frame] for name in field_names])
    report_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    t = arrays["timestamp_s"]
    figure, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True, constrained_layout=True)
    axes[0].plot(t, 1000.0 * arrays["distance_m"], label="synchronized distance")
    axes[0].plot(t, 1000.0 * arrays["delayed_distance_m"], "--", label="distance delayed by 5 frames")
    axes[0].axhline(1000.0 * ENTER_THRESHOLD_M, color="tab:green", linestyle=":", label="enter threshold")
    axes[0].axhline(1000.0 * EXIT_THRESHOLD_M, color="tab:red", linestyle=":", label="exit threshold")
    axes[0].set_ylabel("fingertip distance [mm]")
    axes[0].set_title("Noisy threshold crossing and timestamp offset")
    axes[0].legend(ncol=2, fontsize=8)
    axes[0].grid(alpha=0.25)

    axes[1].step(t, arrays["robust_phase"], where="post", label="synchronized scheduler")
    axes[1].step(t, arrays["delayed_phase"] + 0.05, where="post", linestyle="--", label="hand stream delayed")
    axes[1].set_yticks(np.arange(4), PHASE_NAMES)
    axes[1].set_ylabel("phase")
    axes[1].set_title("One timeline must drive arm and hand")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.25)

    axes[2].plot(t, arrays["raw_command_rad"], label="naive threshold command", alpha=0.8)
    axes[2].plot(t, arrays["robust_command_rad"], label="hysteresis + dwell command", linewidth=2)
    axes[2].plot(t, arrays["delayed_command_rad"], "--", label="delayed hand command")
    axes[2].fill_between(
        t,
        0.15,
        0.47,
        where=arrays["controller_mismatch"],
        color="tab:red",
        alpha=0.14,
        label="wrong active controller",
    )
    axes[2].set_ylim(0.15, 0.47)
    axes[2].set_xlabel("time [s]")
    axes[2].set_ylabel("representative finger q [rad]")
    axes[2].set_title("Controller chatter versus stable phase scheduling")
    axes[2].legend(ncol=2, fontsize=8)
    axes[2].grid(alpha=0.25)
    figure.savefig(figure_path, dpi=160)
    plt.close(figure)

    print(f"\nSaved table  to: {csv_path}")
    print(f"Saved report to: {report_path}")
    print(f"Saved figure to: {figure_path}")


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    arrays, metrics = run_scheduler_experiment()
    print("Phase 4 P4-2 - contact phase scheduling and arm/hand synchronization")
    print(f"frames / sample rate              = {metrics['frames']} / {metrics['sample_rate_hz']:.1f} Hz")
    print(
        "enter / exit threshold          = "
        f"{1000.0 * metrics['enter_threshold_m']:.1f} / "
        f"{1000.0 * metrics['exit_threshold_m']:.1f} mm"
    )
    print(f"minimum dwell time                = {metrics['minimum_dwell_frames']} frames")
    print("\nNaive single-threshold scheduler")
    print(f"  contact transition indices      = {metrics['raw_contact_transition_indices']}")
    print(f"  active-controller switches      = {metrics['raw_controller_switches']}")
    print(f"  command total variation         = {metrics['raw_command_total_variation_rad']:.4f} rad")
    print(f"  maximum command step            = {metrics['raw_max_command_step_rad']:.4f} rad")
    print("\nHysteresis + minimum-dwell scheduler")
    print(f"  contact transition indices      = {metrics['robust_contact_transition_indices']}")
    print(f"  active-controller switches      = {metrics['robust_controller_switches']}")
    print(f"  command total variation         = {metrics['robust_command_total_variation_rad']:.4f} rad")
    print(f"  maximum command step            = {metrics['robust_max_command_step_rad']:.4f} rad")
    print("\nDeliberate hand/object timestamp violation")
    print(f"  stream offset                   = +{metrics['offset_frames']} frames / {metrics['offset_s']:.3f} s")
    print(f"  delayed contact transitions     = {metrics['delayed_contact_transition_indices']}")
    print(f"  phase-mismatched frames         = {metrics['phase_mismatch_indices']}")
    print(f"  wrong-controller frames         = {metrics['controller_mismatch_indices']}")
    print("\nHysteresis suppresses threshold chatter; it cannot repair timestamp misalignment.")
    print("Arm and hand must use the same clock and the same phase state.")
    save_outputs(phase_root, arrays, metrics)


if __name__ == "__main__":
    main()
