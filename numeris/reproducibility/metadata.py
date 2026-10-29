"""Capture and serialize the execution context of an experiment."""

from __future__ import annotations

import json
import platform
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from os import cpu_count
from typing import Any, Mapping

import numpy as np


def _package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "unavailable"


def _json_safe(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


@dataclass(frozen=True)
class ReproducibilityMetadata:
    """Serializable environment and configuration record.

    ``created_at_utc`` is informational; all computational settings are kept
    separately so metadata can be used to reproduce an experiment.
    """

    python_version: str
    numpy_version: str
    scipy_version: str
    seed: int | None = None
    solver_settings: dict[str, Any] = field(default_factory=dict)
    hardware_info: dict[str, Any] = field(default_factory=dict)
    created_at_utc: str = ""

    @classmethod
    def capture(
        cls,
        *,
        seed: int | None = None,
        solver_settings: Mapping[str, Any] | None = None,
        hardware_info: Mapping[str, Any] | None = None,
    ) -> "ReproducibilityMetadata":
        """Capture versions, solver configuration, and host information."""
        default_hardware = {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_count": cpu_count(),
        }
        if hardware_info:
            default_hardware.update(hardware_info)
        return cls(
            python_version=platform.python_version(),
            numpy_version=np.__version__,
            scipy_version=_package_version("scipy"),
            seed=seed,
            solver_settings=_json_safe(dict(solver_settings or {})),
            hardware_info=_json_safe(default_hardware),
            created_at_utc=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> dict[str, Any]:
        return _json_safe(asdict(self))

    def to_json(self, *, indent: int | None = 2) -> str:
        """Return a stable JSON representation."""
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReproducibilityMetadata":
        return cls(
            python_version=str(data["python_version"]),
            numpy_version=str(data["numpy_version"]),
            scipy_version=str(data["scipy_version"]),
            seed=data.get("seed"),
            solver_settings=dict(data.get("solver_settings", {})),
            hardware_info=dict(data.get("hardware_info", {})),
            created_at_utc=str(data.get("created_at_utc", "")),
        )

    @classmethod
    def from_json(cls, payload: str) -> "ReproducibilityMetadata":
        return cls.from_dict(json.loads(payload))
