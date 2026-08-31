"""Phase 4 P4-3: differentiable force surrogate and rolling command refinement."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np


SAMPLE_RATE_HZ = 30.0
FRAMES = 121
CONTACT_ANGLE_RAD = 0.25
TARGET_FORCE_TABLE_N = {"paper_cup": 4.0, "plastic_bottle": 8.0, "metal_tool": 12.0}
OBJECT_CATEGORY = "plastic_bottle"
TARGET_FORCE_N = TARGET_FORCE_TABLE_N[OBJECT_CATEGORY]
COMMAND_BOUNDS_RAD = (0.20, 0.85)

# M(q_command, q_feedback) = A(q_command-q0) + B(q_feedback-q0).
# This simple model is deliberately differentiable and has a closed-form optimizer.
SURROGATE_COMMAND_GAIN = 12.0
SURROGATE_FEEDBACK_GAIN = 8.0
TRUE_FORCE_GAIN = SURROGATE_COMMAND_GAIN + SURROGATE_FEEDBACK_GAIN


def predict_force(command_rad: float, feedback_rad: float) -> float:
    force = (
        SURROGATE_COMMAND_GAIN * (command_rad - CONTACT_ANGLE_RAD)
        + SURROGATE_FEEDBACK_GAIN * (feedback_rad - CONTACT_ANGLE_RAD)
    )
    return max(0.0, force)


def optimize_next_command(
    feedback_rad: float,
    prior_command_rad: float,
    target_force_n: float,
    smooth_weight: float,
) -> float:
    """Solve the scalar quadratic rolling objective in closed form."""
    a = SURROGATE_COMMAND_GAIN
    b = SURROGATE_FEEDBACK_GAIN
    numerator = a * (
        target_force_n + (a + b) * CONTACT_ANGLE_RAD - b * feedback_rad
    ) + smooth_weight * prior_command_rad
    command = numerator / (a * a + smooth_weight)
    return float(np.clip(command, *COMMAND_BOUNDS_RAD))


def measured_force(feedback_rad: float, frame: int) -> float:
    base_force = TRUE_FORCE_GAIN * max(0.0, feedback_rad - CONTACT_ANGLE_RAD)
    repeatable_sensor_ripple = 0.08 * np.sin(2.0 * np.pi * frame / 17.0)
    return max(0.0, base_force + repeatable_sensor_ripple)


def settling_time(force_n: np.ndarray, tolerance_n: float = 0.5) -> float | None:
    inside = np.abs(force_n - TARGET_FORCE_N) <= tolerance_n
    for frame in range(len(force_n)):
        if np.all(inside[frame:]):
            return frame / SAMPLE_RATE_HZ
    return None


def rollout(name: str, smooth_weight: float | None) -> dict[str, np.ndarray | float | str | None]:
    command = np.empty(FRAMES, dtype=np.float64)
    feedback = np.empty(FRAMES, dtype=np.float64)
    velocity = np.zeros(FRAMES, dtype=np.float64)
    predicted = np.empty(FRAMES, dtype=np.float64)
    measured = np.empty(FRAMES, dtype=np.float64)

    command[0] = 0.45
    feedback[0] = 0.30
    predicted[0] = predict_force(command[0], feedback[0])
    measured[0] = measured_force(feedback[0], 0)

    for frame in range(1, FRAMES):
        if smooth_weight is None:
            command[frame] = 0.45
        else:
            command[frame] = optimize_next_command(
                feedback[frame - 1], command[frame - 1], TARGET_FORCE_N, smooth_weight
            )

        # A small under-damped actuator model: feedback does not instantly equal command.
        velocity[frame] = (
            0.68 * velocity[frame - 1]
            + 0.18 * (command[frame] - feedback[frame - 1])
        )
        feedback[frame] = np.clip(
            feedback[frame - 1] + velocity[frame], *COMMAND_BOUNDS_RAD
        )
        predicted[frame] = predict_force(command[frame], feedback[frame - 1])
        measured[frame] = measured_force(feedback[frame], frame)

    error = measured - TARGET_FORCE_N
    command_step = np.diff(command, prepend=command[0])
    tail = measured[-30:]
    return {
        "name": name,
        "smooth_weight": smooth_weight,
        "command_rad": command,
        "feedback_rad": feedback,
        "predicted_force_n": predicted,
        "measured_force_n": measured,
        "force_error_n": error,
        "command_step_rad": command_step,
        "mae_n": float(np.mean(np.abs(error))),
        "final_30_mae_n": float(np.mean(np.abs(tail - TARGET_FORCE_N))),
        "overshoot_n": float(max(0.0, np.max(measured) - TARGET_FORCE_N)),
        "tail_oscillation_n": float(np.max(tail) - np.min(tail)),
        "max_command_step_rad": float(np.max(np.abs(command_step))),
        "settling_time_s": settling_time(measured),
    }


def run_force_experiment() -> tuple[dict[str, dict[str, np.ndarray | float | str | None]], dict[str, object]]:
    cases = {
        "no_adjustment": rollout("no_adjustment", None),
        "weak_regularization": rollout("weak_regularization", 1.0),
        "balanced": rollout("balanced", 1200.0),
        "over_regularized": rollout("over_regularized", 10000.0),
    }
    summary: dict[str, object] = {
        "frames": FRAMES,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "object_category": OBJECT_CATEGORY,
        "target_force_n": TARGET_FORCE_N,
        "surrogate": "linear differentiable command+feedback model",
        "cases": {},
    }
    for name, case in cases.items():
        summary["cases"][name] = {
            "smooth_weight": case["smooth_weight"],
            "mean_absolute_force_error_n": case["mae_n"],
            "final_30_frame_mae_n": case["final_30_mae_n"],
            "overshoot_n": case["overshoot_n"],
            "tail_force_oscillation_n": case["tail_oscillation_n"],
            "max_command_step_rad": case["max_command_step_rad"],
            "settling_time_s": case["settling_time_s"],
        }
    return cases, summary


def save_outputs(
    phase_root: Path,
    cases: dict[str, dict[str, np.ndarray | float | str | None]],
    summary: dict[str, object],
) -> None:
    output_dir = phase_root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "p4c_rolling_force_control.csv"
    report_path = output_dir / "p4c_rolling_force_control.json"
    figure_path = output_dir / "p4c_rolling_force_control.png"
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["case", "frame", "timestamp_s", "command_rad", "feedback_rad", "predicted_force_n", "measured_force_n"]
        )
        for name, case in cases.items():
            for frame in range(FRAMES):
                writer.writerow(
                    [
                        name,
                        frame,
                        frame / SAMPLE_RATE_HZ,
                        case["command_rad"][frame],
                        case["feedback_rad"][frame],
                        case["predicted_force_n"][frame],
                        case["measured_force_n"][frame],
                    ]
                )

    time_s = np.arange(FRAMES) / SAMPLE_RATE_HZ
    colors = {
        "no_adjustment": "tab:gray",
        "weak_regularization": "tab:red",
        "balanced": "tab:blue",
        "over_regularized": "tab:orange",
    }
    figure, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True, constrained_layout=True)
    for name, case in cases.items():
        axes[0].plot(time_s, case["measured_force_n"], label=name, color=colors[name])
    axes[0].axhline(TARGET_FORCE_N, color="black", linestyle="--", label="target force")
    axes[0].fill_between(time_s, TARGET_FORCE_N - 0.5, TARGET_FORCE_N + 0.5, color="tab:green", alpha=0.10, label="settling band")
    axes[0].set_ylabel("measured force [N]")
    axes[0].set_title("Rolling force regulation")
    axes[0].legend(ncol=3, fontsize=8)
    axes[0].grid(alpha=0.25)

    for name, case in cases.items():
        axes[1].plot(time_s, case["command_rad"], label=name, color=colors[name])
    axes[1].set_ylabel("command angle [rad]")
    axes[1].set_title("Optimized command: force accuracy versus command regularization")
    axes[1].grid(alpha=0.25)

    for name, case in cases.items():
        axes[2].plot(time_s, case["feedback_rad"], label=name, color=colors[name])
    axes[2].set_xlabel("time [s]")
    axes[2].set_ylabel("feedback angle [rad]")
    axes[2].set_title("Actuator feedback lags behind the command")
    axes[2].grid(alpha=0.25)
    figure.savefig(figure_path, dpi=160)
    plt.close(figure)

    print(f"\nSaved table  to: {csv_path}")
    print(f"Saved report to: {report_path}")
    print(f"Saved figure to: {figure_path}")


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    cases, summary = run_force_experiment()
    print("Phase 4 P4-3 - target force and rolling command refinement")
    print(f"frames / sample rate             = {summary['frames']} / {summary['sample_rate_hz']:.1f} Hz")
    print(f"object category / target force   = {summary['object_category']} / {summary['target_force_n']:.1f} N")
    print(f"force surrogate                  = {summary['surrogate']}")
    print("\nCase summaries")
    for name, case in summary["cases"].items():
        weight = "disabled" if case["smooth_weight"] is None else f"{case['smooth_weight']:.1f}"
        settling = "not settled" if case["settling_time_s"] is None else f"{case['settling_time_s']:.3f} s"
        print(name)
        print(f"  command smooth weight          = {weight}")
        print(f"  mean / final-30 force MAE      = {case['mean_absolute_force_error_n']:.4f} / {case['final_30_frame_mae_n']:.4f} N")
        print(f"  force overshoot                = {case['overshoot_n']:.4f} N")
        print(f"  final-30 force oscillation     = {case['tail_force_oscillation_n']:.4f} N")
        print(f"  maximum command step           = {case['max_command_step_rad']:.4f} rad")
        print(f"  settling time (+/-0.5 N)       = {settling}")
    print("\nEach cycle uses the latest feedback, optimizes one command, executes it, and repeats.")
    print("A semantic force target is a prior, not a safety guarantee or direct motor command.")
    save_outputs(phase_root, cases, summary)


if __name__ == "__main__":
    main()
