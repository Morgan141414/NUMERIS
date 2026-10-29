"""Cross-platform process-memory measurement and profiling result schema.

Memory readings are best-effort diagnostics: operating systems expose
different counters and optional dependencies may be unavailable.  Missing
measurements are represented by ``None`` and never by fabricated zeroes.

The C++ gate is deliberately optional.  A C++ implementation may be
considered only after profiling identifies a measured hot spot and a
numerically equivalent implementation has been demonstrated.  A memory
reading alone is not evidence that C++ is warranted.
"""

from __future__ import annotations

import ctypes
import json
import math
import platform
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

try:
    import resource
except ImportError:  # pragma: no cover - Windows
    resource = None  # type: ignore[assignment]


def _positive_int(value: Any) -> int | None:
    """Return a non-negative integer, or ``None`` for an unusable reading."""
    try:
        converted = int(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return converted if converted >= 0 else None


def _psutil_rss_bytes() -> int | None:
    try:
        import psutil  # type: ignore[import-not-found]

        return _positive_int(psutil.Process().memory_info().rss)
    except (ImportError, OSError, AttributeError, TypeError, ValueError):
        return None


def _windows_working_set_bytes() -> int | None:
    if platform.system() != "Windows":
        return None
    try:
        class Counters(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.c_ulong),
                ("PageFaultCount", ctypes.c_ulong),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = Counters()
        counters.cb = ctypes.sizeof(Counters)
        process = ctypes.windll.kernel32.GetCurrentProcess()
        ok = ctypes.windll.psapi.GetProcessMemoryInfo(
            process, ctypes.byref(counters), counters.cb
        )
        return _positive_int(counters.WorkingSetSize) if ok else None
    except (AttributeError, OSError, TypeError, ValueError):
        return None


def process_memory_bytes() -> tuple[int | None, str]:
    """Return current process RSS in bytes and the measurement source.

    ``psutil`` is preferred when installed.  Windows uses the native API as a
    fallback; on systems without an available RSS API the result is ``None``.
    """
    rss = _psutil_rss_bytes()
    if rss is not None:
        return rss, "psutil"
    rss = _windows_working_set_bytes()
    if rss is not None:
        return rss, "windows-psapi"
    return None, "unavailable"


def peak_process_memory_bytes() -> tuple[int | None, str]:
    """Return the process high-water mark in bytes where the OS exposes it."""
    if resource is None:
        return None, "unavailable"
    try:
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # macOS reports bytes; Linux and most BSDs report KiB.
        multiplier = 1 if platform.system() == "Darwin" else 1024
        value = _positive_int(usage * multiplier)
        if value is not None:
            return value, "resource.ru_maxrss"
    except (AttributeError, OSError, TypeError, ValueError):
        pass
    return None, "unavailable"


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


@dataclass(frozen=True)
class ProfileResult:
    """Versioned, JSON-safe result of one profiling run.

    ``success`` is independent of measurement availability: a successful
    workload can legitimately have ``None`` memory values on a restricted OS.
    """

    schema_version: str = "1"
    workload: str = ""
    method: str = ""
    profile_path: str | None = None
    elapsed_s: float | None = None
    memory_before_bytes: int | None = None
    memory_after_bytes: int | None = None
    peak_memory_bytes: int | None = None
    memory_delta_bytes: int | None = None
    memory_source: str = "unavailable"
    cprofile_enabled: bool = False
    success: bool = True
    error: str | None = None
    cpp_gate: str = (
        "optional: require a measured hot spot and numerical equivalence before C++"
    )

    def __post_init__(self) -> None:
        for name in (
            "memory_before_bytes",
            "memory_after_bytes",
            "peak_memory_bytes",
        ):
            if getattr(self, name) is not None and _positive_int(getattr(self, name)) is None:
                raise ValueError(f"{name} must be a non-negative integer or None")
        if self.memory_delta_bytes is not None and not isinstance(
            self.memory_delta_bytes, int
        ):
            raise ValueError("memory_delta_bytes must be an integer or None")
        if self.elapsed_s is not None and (
            not math.isfinite(float(self.elapsed_s)) or float(self.elapsed_s) < 0
        ):
            raise ValueError("elapsed_s must be finite and non-negative or None")
        if self.success and self.error is not None:
            raise ValueError("successful profiles cannot contain an error")
        if not self.success and not self.error:
            raise ValueError("failed profiles must contain an error")

    def to_dict(self) -> dict[str, Any]:
        return _json_safe(asdict(self))

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True, allow_nan=False)

    def write_json(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self.to_json() + "\n", encoding="utf-8")


__all__ = ["ProfileResult", "peak_process_memory_bytes", "process_memory_bytes"]
