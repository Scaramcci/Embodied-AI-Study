"""Phase 3 P3-2: arm-plane and temporal-smoothness loss trade-offs."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
from scipy.optimize import minimize


UPPER_ARM_M = 0.32
FOREARM_M = 0.30


def make_wrist_trajectory(timestamp: np.ndarray) -> np.ndarray:
    progress = timestamp / timestamp[-1]
    return np.column_stack(
        (
            0.43 + 0.035 * np.sin(2.0 * np.pi * progress),
            0.08 * np.sin(2.0 * np.pi * progress),
            0.16 + 0.035 * np.cos(2.0 * np.pi * progress),
        )
    )


def make_reference_swivel(timestamp: np.ndarray) -> np.ndarray:
    """A task-adaptive desired elbow/arm-plane trend with a small fast component."""
    progress = timestamp / timestamp[-1]
    return (
        0.35
        + 0.55 * np.sin(2.0 * np.pi * progress)
        + 0.12 * np.sin(12.0 * np.pi * progress)
    )


def elbow_circle_geometry(wrist: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return elbow-circle center and two orthonormal basis vectors per frame."""
    distance = np.linalg.norm(wrist, axis=1)
    if np.any(distance >= UPPER_ARM_M + FOREARM_M):
        raise ValueError("wrist target is outside the two-link workspace")
    if np.any(distance <= abs(UPPER_ARM_M - FOREARM_M)):
        raise ValueError("wrist target is inside the folded workspace boundary")

    axis = wrist / distance[:, None]
    center_distance = (
        UPPER_ARM_M**2 - FOREARM_M**2 + distance**2
    ) / (2.0 * distance)
    center = center_distance[:, None] * axis
    radius = np.sqrt(np.maximum(UPPER_ARM_M**2 - center_distance**2, 0.0))

    reference = np.repeat(np.array([[0.0, 0.0, 1.0]]), len(wrist), axis=0)
    nearly_parallel = np.abs(np.sum(axis * reference, axis=1)) > 0.95
    reference[nearly_parallel] = np.array([0.0, 1.0, 0.0])
    basis_u = np.cross(axis, reference)
    basis_u /= np.linalg.norm(basis_u, axis=1, keepdims=True)
    basis_v = np.cross(axis, basis_u)
    basis_v /= np.linalg.norm(basis_v, axis=1, keepdims=True)
    return center, radius[:, None] * basis_u, radius[:, None] * basis_v


def elbows_from_swivel(wrist: np.ndarray, swivel: np.ndarray) -> np.ndarray:
    center, radial_u, radial_v = elbow_circle_geometry(wrist)
    return (
        center
        + np.cos(swivel)[:, None] * radial_u
        + np.sin(swivel)[:, None] * radial_v
    )


def arm_plane_normals(wrist: np.ndarray, elbow: np.ndarray) -> np.ndarray:
    upper = elbow
    fore = wrist - elbow
    normals = np.cross(upper, fore)
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    if np.any(norms < 1e-10):
        raise ValueError("arm-plane normal is degenerate for a nearly straight arm")
    return normals / norms


def loss_and_gradient(
    swivel: np.ndarray,
    reference_swivel: np.ndarray,
    plane_weight: float,
    smooth_weight: float,
) -> tuple[float, np.ndarray]:
    count = len(swivel)
    delta = swivel - reference_swivel
    plane_loss = np.mean(1.0 - np.cos(delta))
    gradient = plane_weight * np.sin(delta) / count

    steps = np.diff(swivel)
    smooth_loss = np.mean(steps**2)
    smooth_gradient = np.zeros_like(swivel)
    scale = 2.0 / len(steps)
    smooth_gradient[:-1] -= scale * steps
    smooth_gradient[1:] += scale * steps
    gradient += smooth_weight * smooth_gradient
    return plane_weight * plane_loss + smooth_weight * smooth_loss, gradient


def optimize_swivel(
    initial: np.ndarray,
    reference: np.ndarray,
    plane_weight: float,
    smooth_weight: float,
) -> np.ndarray:
    result = minimize(
        lambda value: loss_and_gradient(
            value, reference, plane_weight, smooth_weight
        ),
        initial,
        jac=True,
        method="L-BFGS-B",
        bounds=[(-np.pi, np.pi)] * len(initial),
        options={"maxiter": 500, "ftol": 1e-12, "gtol": 1e-9},
    )
    if not result.success:
        raise RuntimeError(f"swivel optimization failed: {result.message}")
    return result.x


def evaluate_case(
    wrist: np.ndarray,
    swivel: np.ndarray,
    reference_normal: np.ndarray,
) -> tuple[np.ndarray, dict[str, float]]:
    elbow = elbows_from_swivel(wrist, swivel)
    normal = arm_plane_normals(wrist, elbow)
    dots = np.clip(np.sum(normal * reference_normal, axis=1), -1.0, 1.0)
    normal_error = np.arccos(dots)
    elbow_step = np.linalg.norm(np.diff(elbow, axis=0), axis=1)
    metrics = {
        "mean_arm_plane_error_deg": float(np.rad2deg(np.mean(normal_error))),
        "max_arm_plane_error_deg": float(np.rad2deg(np.max(normal_error))),
        "mean_adjacent_elbow_change_m": float(np.mean(elbow_step)),
        "max_adjacent_elbow_change_m": float(np.max(elbow_step)),
        "mean_swivel_step_rad": float(np.mean(np.abs(np.diff(swivel)))),
    }
    return elbow, metrics


def run_arm_plane_experiment() -> tuple[dict[str, np.ndarray], dict[str, object]]:
    timestamp = np.arange(121, dtype=np.float64) / 30.0
    wrist = make_wrist_trajectory(timestamp)
    reference_swivel = make_reference_swivel(timestamp)
    reference_elbow = elbows_from_swivel(wrist, reference_swivel)
    reference_normal = arm_plane_normals(wrist, reference_elbow)

    task_only = reference_swivel + 0.08 * np.sin(
        20.0 * np.pi * timestamp / timestamp[-1]
    )
    task_only[35:79] += 2.0
    plane_only = optimize_swivel(task_only, reference_swivel, 1.0, 0.0)
    balanced = optimize_swivel(task_only, reference_swivel, 1.0, 8.0)
    over_smooth = optimize_swivel(task_only, reference_swivel, 1.0, 250.0)

    cases = {
        "task_only": task_only,
        "plane_only": plane_only,
        "plane_plus_smooth": balanced,
        "over_smooth": over_smooth,
    }
    arrays: dict[str, np.ndarray] = {
        "timestamp": timestamp,
        "wrist_position": wrist,
        "reference_swivel": reference_swivel,
        "reference_elbow": reference_elbow,
        "reference_arm_plane_normal": reference_normal,
    }
    metrics: dict[str, object] = {
        "frame_count": len(timestamp),
        "upper_arm_length_m": UPPER_ARM_M,
        "forearm_length_m": FOREARM_M,
        "all_cases_wrist_task_error_m": 0.0,
        "case_weights": {
            "task_only": {"plane": 0.0, "smooth": 0.0},
            "plane_only": {"plane": 1.0, "smooth": 0.0},
            "plane_plus_smooth": {"plane": 1.0, "smooth": 8.0},
            "over_smooth": {"plane": 1.0, "smooth": 250.0},
        },
        "cases": {},
    }
    for name, swivel in cases.items():
        elbow, case_metrics = evaluate_case(wrist, swivel, reference_normal)
        arrays[f"{name}_swivel"] = swivel
        arrays[f"{name}_elbow"] = elbow
        metrics["cases"][name] = case_metrics
    return arrays, metrics


def save_outputs(
    phase_root: Path, arrays: dict[str, np.ndarray], metrics: dict[str, object]
) -> None:
    data_dir = phase_root / "data"
    output_dir = phase_root / "outputs"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_path = data_dir / "p3b_arm_plane_losses.npz"
    report_path = output_dir / "p3b_arm_plane_losses.json"
    figure_path = output_dir / "p3b_arm_plane_losses.png"
    np.savez_compressed(data_path, **arrays)
    report_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    time_s = arrays["timestamp"]
    figure, axes = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
    snapshot = 55
    wrist = arrays["wrist_position"][snapshot]
    axes[0, 0].scatter(0.0, 0.0, c="black", label="shoulder")
    axes[0, 0].scatter(wrist[1], wrist[2], c="tab:purple", label="wrist")
    for name, label in (
        ("reference", "reference elbow"),
        ("task_only", "task-only elbow"),
        ("plane_plus_smooth", "plane + smooth elbow"),
    ):
        elbow = arrays[f"{name}_elbow"][snapshot]
        axes[0, 0].plot(
            [0.0, elbow[1], wrist[1]],
            [0.0, elbow[2], wrist[2]],
            "o-",
            label=label,
        )
    axes[0, 0].set_aspect("equal")
    axes[0, 0].set_title(f"Same shoulder/wrist task, frame {snapshot} (y-z view)")
    axes[0, 0].set_xlabel("world y [m]")
    axes[0, 0].set_ylabel("world z [m]")
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(alpha=0.25)

    for name, label in (
        ("task_only", "task only"),
        ("plane_only", "plane only"),
        ("plane_plus_smooth", "plane + smooth"),
        ("over_smooth", "over-smooth"),
    ):
        axes[0, 1].plot(time_s, arrays[f"{name}_swivel"], label=label)
    axes[0, 1].plot(
        time_s,
        arrays["reference_swivel"],
        "k--",
        linewidth=1.5,
        label="reference trend",
    )
    axes[0, 1].set_title("Redundant elbow swivel solutions")
    axes[0, 1].set_xlabel("time [s]")
    axes[0, 1].set_ylabel("swivel angle [rad]")
    axes[0, 1].legend(fontsize=8, ncol=2)
    axes[0, 1].grid(alpha=0.25)

    labels = ["task only", "plane only", "plane + smooth", "over-smooth"]
    keys = ["task_only", "plane_only", "plane_plus_smooth", "over_smooth"]
    plane_errors = [
        metrics["cases"][key]["mean_arm_plane_error_deg"] for key in keys
    ]
    elbow_changes_mm = [
        1000.0 * metrics["cases"][key]["mean_adjacent_elbow_change_m"]
        for key in keys
    ]
    axes[1, 0].bar(labels, plane_errors)
    axes[1, 0].set_title("Anthropomorphic arm-plane error")
    axes[1, 0].set_ylabel("mean normal error [deg]")
    axes[1, 0].tick_params(axis="x", rotation=15)
    axes[1, 0].grid(axis="y", alpha=0.25)

    axes[1, 1].bar(labels, elbow_changes_mm)
    axes[1, 1].set_title("Temporal elbow motion")
    axes[1, 1].set_ylabel("mean adjacent elbow change [mm/frame]")
    axes[1, 1].tick_params(axis="x", rotation=15)
    axes[1, 1].grid(axis="y", alpha=0.25)
    figure.savefig(figure_path, dpi=160)
    plt.close(figure)

    print(f"\nSaved data   to: {data_path}")
    print(f"Saved report to: {report_path}")
    print(f"Saved figure to: {figure_path}")


def main() -> None:
    phase_root = Path(__file__).resolve().parents[1]
    arrays, metrics = run_arm_plane_experiment()

    print("Phase 3 P3-2 - arm-plane and temporal-smoothness losses")
    print(f"frames                            = {metrics['frame_count']}")
    print(
        f"upper-arm / forearm length        = "
        f"{metrics['upper_arm_length_m']:.3f} / "
        f"{metrics['forearm_length_m']:.3f} m"
    )
    print("wrist task error for every case   = 0.000 mm (fixed by construction)")
    print("\nCase summaries")
    for name in ("task_only", "plane_only", "plane_plus_smooth", "over_smooth"):
        case = metrics["cases"][name]
        weights = metrics["case_weights"][name]
        print(name)
        print(
            f"  weights plane / smooth          = "
            f"{weights['plane']:.1f} / {weights['smooth']:.1f}"
        )
        print(
            f"  mean arm-plane normal error     = "
            f"{case['mean_arm_plane_error_deg']:.4f} deg"
        )
        print(
            f"  max arm-plane normal error      = "
            f"{case['max_arm_plane_error_deg']:.4f} deg"
        )
        print(
            f"  mean adjacent elbow change      = "
            f"{1000.0 * case['mean_adjacent_elbow_change_m']:.4f} mm/frame"
        )
        print(
            f"  max adjacent elbow change       = "
            f"{1000.0 * case['max_adjacent_elbow_change_m']:.4f} mm/frame"
        )
    print("\nA zero wrist task error does not determine the redundant elbow configuration.")
    print("Plane and smoothness terms select among task-equivalent arm motions.")
    save_outputs(phase_root, arrays, metrics)


if __name__ == "__main__":
    main()

