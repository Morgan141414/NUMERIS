"""Serializable metadata contracts for parameterized ODE experiments.

This module intentionally stays separate from :class:`ODEModel`.  It describes
the configuration of a model and its observations without changing the runtime
ODE model contract.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


def _json_compatible(value: Any, *, field_name: str) -> Any:
    """Return ``value`` after validating that it can be encoded as JSON."""

    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{field_name} must contain only JSON-compatible values") from exc
    return value


@dataclass(frozen=True)
class ParameterSpec:
    """Description of one estimable parameter and its admissible interval."""

    name: str
    bounds: tuple[float, float]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("parameter name must be a non-empty string")
        if len(self.bounds) != 2:
            raise ValueError("parameter bounds must contain exactly two values")

        lower, upper = (float(value) for value in self.bounds)
        if lower >= upper:
            raise ValueError("parameter bounds must satisfy lower < upper")
        if not all(math.isfinite(value) for value in (lower, upper)):
            raise ValueError("parameter bounds must be finite")
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "bounds", (lower, upper))

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""

        return {"name": self.name, "bounds": list(self.bounds)}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ParameterSpec":
        """Build a parameter specification from its serialized form."""

        if not isinstance(data, Mapping):
            raise TypeError("parameter specification must be a mapping")
        try:
            return cls(name=data["name"], bounds=tuple(data["bounds"]))
        except KeyError as exc:
            raise ValueError(f"parameter specification is missing {exc.args[0]!r}") from exc


@dataclass(frozen=True)
class ModelConfig:
    """Serializable model, parameter, observation, and noise metadata."""

    model_id: str
    parameters: tuple[ParameterSpec, ...] = field(default_factory=tuple)
    observations: Mapping[str, Any] = field(default_factory=dict)
    noise: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.model_id, str) or not self.model_id.strip():
            raise ValueError("model_id must be a non-empty string")

        parameters = tuple(
            parameter if isinstance(parameter, ParameterSpec) else ParameterSpec.from_dict(parameter)
            for parameter in self.parameters
        )
        names = [parameter.name for parameter in parameters]
        if len(names) != len(set(names)):
            raise ValueError("parameter names must be unique")
        if not isinstance(self.observations, Mapping):
            raise TypeError("observations must be a mapping")
        if not isinstance(self.noise, Mapping):
            raise TypeError("noise must be a mapping")

        object.__setattr__(self, "model_id", self.model_id.strip())
        object.__setattr__(self, "parameters", parameters)
        _json_compatible(dict(self.observations), field_name="observations")
        _json_compatible(dict(self.noise), field_name="noise")

    @property
    def parameter_names(self) -> tuple[str, ...]:
        """Names in the same order as :attr:`parameters`."""

        return tuple(parameter.name for parameter in self.parameters)

    @property
    def parameter_bounds(self) -> dict[str, tuple[float, float]]:
        """Bounds keyed by parameter name."""

        return {parameter.name: parameter.bounds for parameter in self.parameters}

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation of this configuration."""

        return {
            "model_id": self.model_id,
            "parameters": [parameter.to_dict() for parameter in self.parameters],
            "observations": dict(self.observations),
            "noise": dict(self.noise),
        }

    def to_json(self, *, indent: int | None = None) -> str:
        """Serialize this configuration to a JSON string."""

        return json.dumps(self.to_dict(), indent=indent, sort_keys=True, allow_nan=False)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ModelConfig":
        """Build a configuration from a serialized mapping."""

        if not isinstance(data, Mapping):
            raise TypeError("model configuration must be a mapping")
        try:
            return cls(
                model_id=data["model_id"],
                parameters=tuple(ParameterSpec.from_dict(item) for item in data.get("parameters", ())),
                observations=data.get("observations", {}),
                noise=data.get("noise", {}),
            )
        except KeyError as exc:
            raise ValueError(f"model configuration is missing {exc.args[0]!r}") from exc

    @classmethod
    def from_json(cls, payload: str | Path) -> "ModelConfig":
        """Deserialize from a JSON string or a path to a JSON file."""

        if isinstance(payload, Path):
            return cls.from_dict(json.loads(payload.read_text(encoding="utf-8")))
        if not isinstance(payload, str):
            raise TypeError("payload must be a JSON string or pathlib.Path")
        return cls.from_dict(json.loads(payload))
