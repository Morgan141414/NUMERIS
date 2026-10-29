import json

import pytest

from numeris.models.config import ModelConfig, ParameterSpec


def test_parameter_spec_validates_and_serializes_bounds():
    parameter = ParameterSpec(" damping ", [0.0, 1.0])

    assert parameter.name == "damping"
    assert parameter.bounds == (0.0, 1.0)
    assert parameter.to_dict() == {"name": "damping", "bounds": [0.0, 1.0]}


@pytest.mark.parametrize(
    "bounds",
    [(-1.0, -1.0), (1.0, 0.0), (float("nan"), 1.0), (0.0, float("inf"))],
)
def test_parameter_spec_rejects_invalid_bounds(bounds):
    with pytest.raises(ValueError):
        ParameterSpec("rate", bounds)


def test_model_config_round_trips_json_and_exposes_parameter_metadata():
    config = ModelConfig(
        model_id="oscillator-v1",
        parameters=(ParameterSpec("frequency", (0.1, 4.0)), ParameterSpec("damping", (0.0, 1.0))),
        observations={"kind": "synthetic", "count": 201, "target": "state"},
        noise={"distribution": "gaussian", "sigma": 0.05},
    )

    restored = ModelConfig.from_json(config.to_json())

    assert restored == config
    assert restored.parameter_names == ("frequency", "damping")
    assert restored.parameter_bounds["frequency"] == (0.1, 4.0)


def test_model_config_rejects_duplicate_parameters_and_non_json_metadata():
    with pytest.raises(ValueError, match="unique"):
        ModelConfig(
            "duplicate",
            parameters=(ParameterSpec("x", (0.0, 1.0)), ParameterSpec("x", (1.0, 2.0))),
        )

    with pytest.raises(TypeError, match="JSON-compatible"):
        ModelConfig("invalid", observations={"times": object()})


def test_model_config_dict_is_json_serializable():
    config = ModelConfig("minimal")

    assert json.loads(json.dumps(config.to_dict())) == config.to_dict()
