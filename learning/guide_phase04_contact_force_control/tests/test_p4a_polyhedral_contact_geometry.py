from pathlib import Path
import sys


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from p4a_polyhedral_contact_geometry import run_polyhedral_experiment  # noqa: E402


def test_contact_regions_and_polyhedral_shapes() -> None:
    arrays, metrics = run_polyhedral_experiment()

    assert arrays["fingertips"].shape == (5, 3)
    assert arrays["contact_points"].shape == (5, 3)
    assert arrays["polyhedral_units"].shape == (5, 4, 3)
    assert arrays["edge_lengths"].shape == (5, 6)
    assert all(count > 0 for count in metrics["contact_region_point_count"])


def test_rigid_invariance_and_local_distortion_sensitivity() -> None:
    _, metrics = run_polyhedral_experiment()

    assert metrics["rigid_edge_length_change_m"] < 1e-12
    assert metrics["rigid_hand_local_edge_change_m"] < 1e-12
    assert metrics["rigid_hand_local_contact_change_m"] < 1e-12
    assert metrics["rigid_world_edge_vector_change_m"] > 1e-3
    assert metrics["distorted_edge_length_rmse_m"] > 1e-4
    assert metrics["distorted_hand_local_edge_rmse_m"] > 1e-4
    assert metrics["distorted_hand_local_contact_rmse_m"] > 1e-4

