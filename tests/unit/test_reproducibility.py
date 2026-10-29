import json

import numpy as np

from numeris.reproducibility import ReproducibilityMetadata


def test_capture_contains_versions_solver_settings_and_hardware():
    metadata = ReproducibilityMetadata.capture(
        seed=42,
        solver_settings={"rtol": np.float64(1e-8), "method": "DOP853"},
        hardware_info={"test_machine": True},
    )
    assert metadata.python_version
    assert metadata.numpy_version == np.__version__
    assert metadata.scipy_version
    assert metadata.seed == 42
    assert metadata.solver_settings["rtol"] == 1e-8
    assert metadata.hardware_info["test_machine"] is True


def test_json_round_trip_is_serializable_and_preserves_data():
    metadata = ReproducibilityMetadata.capture(
        seed=7,
        solver_settings={"atol": np.array([1e-10, 1e-9])},
    )
    payload = metadata.to_json()
    assert isinstance(json.loads(payload), dict)
    restored = ReproducibilityMetadata.from_json(payload)
    assert restored.to_dict() == metadata.to_dict()
    assert restored.solver_settings["atol"] == [1e-10, 1e-9]
