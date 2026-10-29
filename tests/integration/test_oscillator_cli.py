import importlib.util
import json
from pathlib import Path

import pytest


pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("scipy") is None,
    reason="SciPy is required for the oscillator CLI smoke test",
)


def _load_cli():
    path = Path(__file__).parents[2] / "scripts" / "run_oscillator_benchmark.py"
    spec = importlib.util.spec_from_file_location("numeris_oscillator_cli", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_oscillator_cli_writes_reproducible_json(tmp_path):
    cli = _load_cli()
    first_path = tmp_path / "first" / "oscillator.json"
    second_path = tmp_path / "second" / "oscillator.json"
    arguments = {
        "solvers": ["RK45"],
        "rtol": 1e-6,
        "atol": 1e-8,
        "seed": 17,
    }

    first = cli.run_cli(output=first_path, **arguments)
    second = cli.run_cli(output=second_path, **arguments)

    assert first["experiment"]["seed"] == 17
    assert first["n_configurations"] == 1
    assert first_path.exists()
    first_json = json.loads(first_path.read_text(encoding="utf-8"))
    second_json = json.loads(second_path.read_text(encoding="utf-8"))
    assert first_json["experiment"] == second_json["experiment"]
    assert first_json["results"][0]["config"] == second_json["results"][0]["config"]
    assert first_json["results"][0]["trajectory"] == second_json["results"][0]["trajectory"]
    assert first_json["results"][0]["likelihood"] == second_json["results"][0]["likelihood"]
    # Runtime and process RSS are intentionally machine/run dependent.
    assert first_json["results"][0]["cost"]["nfev"] == second_json["results"][0]["cost"]["nfev"]
